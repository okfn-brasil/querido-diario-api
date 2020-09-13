import os
import unittest
from unittest import TestCase
from datetime import date, timedelta

import elasticsearch

from database import ElasticSearchDataMapper, create_elasticsearch_data_mapper
from gazettes import GazetteDataGateway, Gazette


class ElasticSearchInterfaceTest(TestCase):
    def test_create_elasticsearch_mapper(self):
        mapper = create_elasticsearch_data_mapper("localhost", "gazettes")
        self.assertIsInstance(mapper, GazetteDataGateway)

    @unittest.expectedFailure
    def test_create_elasticsearch_mapper_should_fail_without_host(self):
        create_elasticsearch_data_mapper()

    def test_create_elasticsearch_mapper_without_host(self):
        with self.assertRaisesRegex(Exception, "Missing host") as cm:
            mapper = create_elasticsearch_data_mapper("", "gazettes")

    def test_create_elasticsearch_mapper_without_index_name(self):
        with self.assertRaisesRegex(Exception, "Missing index name") as cm:
            mapper = create_elasticsearch_data_mapper("localhost")


class ElasticSearchDataMapperTest(TestCase):
    def setUp(self):
        self._es = elasticsearch.Elasticsearch(hosts=["localhost"])
        self._es.indices.delete(
            index="gazettes", ignore_unavailable=True, timeout="30s"
        )
        self._es.indices.create(
            index="gazettes",
            body={"mappings": {"properties": {"date": {"type": "date"}}}},
            timeout="30s",
        )
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        self._data = [
            {
                "id": 0,
                "date": date.today(),
                "territory_id": "4202909",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content",
            },
            {
                "id": 1,
                "date": date.today() - day,
                "territory_id": "4205902",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content",
            },
            {
                "id": 2,
                "date": date.today() + day,
                "territory_id": "4205902",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content",
            },
            {
                "id": 3,
                "date": date.today() - day,
                "territory_id": "4202909",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content. anotherkeyword",
            },
            {
                "id": 4,
                "date": date.today() + day,
                "territory_id": "4205902",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content. keyword1",
            },
            {
                "id": 5,
                "date": date.today(),
                "territory_id": "4202909",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content. 000.000.000-00",
            },
            {
                "id": 6,
                "date": week_ago - day,
                "territory_id": "4202919",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 6",
            },
            {
                "id": 7,
                "date": week_ago,
                "territory_id": "4202919",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 7",
            },
            {
                "id": 8,
                "date": week_ago + day,
                "territory_id": "4202919",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 8",
            },
            {
                "id": 9,
                "date": week_ago - day,
                "territory_id": "4202920",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 9",
            },
            {
                "id": 10,
                "date": week_ago,
                "territory_id": "4202920",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 10",
            },
            {
                "id": 11,
                "date": week_ago + day,
                "territory_id": "4202920",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 11",
            },
        ]
        bulk_data = []
        for gazette in self._data:
            bulk_data.append({"index": {"_index": "gazettes", "_id": gazette["id"]}})
            bulk_data.append(gazette)
        self._es.bulk(bulk_data, index="gazettes", refresh=True)
        self._mapper = create_elasticsearch_data_mapper("localhost", "gazettes")

    def tearDown(self):
        self._es.close()

    def test_get_none_gazettes(self):
        gazettes = list(self._mapper.get_gazettes())
        self.assertEqual(0, len(gazettes))

    def test_return_gazette_objects(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        gazettes = self._mapper.get_gazettes(since=week_ago - day)
        for gazette in gazettes:
            self.assertIsInstance(gazette, Gazette)

    def test_gazettes_fields(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        gazettes = self._mapper.get_gazettes(since=week_ago - day)
        for g in gazettes:
            self.assertIsInstance(g.territory_id, str)
            self.assertIsInstance(g.url, str)
            self.assertIsInstance(g.date, date)

    def test_return_get_gazettes_sort_by_date_in_descending_order(self):
        two_weeks_ago = date.today() - timedelta(days=14)
        gazettes = list(self._mapper.get_gazettes(since=two_weeks_ago))
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"]) for d in self._data
        ]
        self.assertGreater(len(gazettes), 0)
        self.assertGreater(gazettes[0].date, gazettes[-1].date)

    def test_search_gazettes_since_date(self):
        gazettes = self._mapper.get_gazettes(since=date.today())
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"])
            for d in self._data
            if d["date"] >= date.today()
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_until_date(self):
        yesterday = date.today() - timedelta(days=1)
        gazettes = self._mapper.get_gazettes(until=yesterday)
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"])
            for d in self._data
            if d["date"] <= yesterday
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_by_territory_id(self):
        gazettes = self._mapper.get_gazettes(territory_id="4202909")
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"])
            for d in self._data
            if d["territory_id"] == "4202909"
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_by_territory_id_and_dates(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"])
            for d in self._data
            if d["territory_id"] == "4202920"
            and d["date"] >= (week_ago - day)
            and d["date"] <= (week_ago + day)
        ]

        gazettes = self._mapper.get_gazettes(
            territory_id="4202920", since=week_ago - day, until=week_ago + day
        )
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_pagination_interaction_when_return_all_gazettes_(self):
        two_weeks_ago = date.today() - timedelta(days=14)
        gazettes = list(self._mapper.get_gazettes(since=two_weeks_ago))
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"]) for d in self._data
        ]
        self.assertCountEqual(gazettes, expected_gazettes)
