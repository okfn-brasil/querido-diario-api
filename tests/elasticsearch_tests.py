from datetime import date, timedelta
from unittest import TestCase
import os
import unittest

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

    def test_create_elasticsearch_mapper_using_non_existing_index_should_fail(self):
        with self.assertRaisesRegex(Exception, "Index does not exist") as cm:
            create_elasticsearch_data_mapper("localhost", "zpto")


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
                "checksum": "0",
                "date": date.today(),
                "territory_id": "4202909",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content",
            },
            {
                "checksum": "1",
                "date": date.today() - day,
                "territory_id": "4205902",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content",
            },
            {
                "checksum": "2",
                "date": date.today() + day,
                "territory_id": "4205902",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content",
            },
            {
                "checksum": "3",
                "date": date.today() - day,
                "territory_id": "4202909",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content. anotherkeyword",
            },
            {
                "checksum": "4",
                "date": date.today() + day,
                "territory_id": "4205902",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content. keyword1",
            },
            {
                "checksum": "5",
                "date": date.today(),
                "territory_id": "4202909",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette with some keywork which is: 000.000.000-00",
            },
            {
                "checksum": "6",
                "date": week_ago - day,
                "territory_id": "4202919",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 6",
            },
            {
                "checksum": "7",
                "date": week_ago,
                "territory_id": "4202919",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 7",
            },
            {
                "checksum": "8",
                "date": week_ago + day,
                "territory_id": "4202919",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 8",
            },
            {
                "checksum": "9",
                "date": week_ago - day,
                "territory_id": "4202920",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 9",
            },
            {
                "checksum": "10",
                "date": week_ago,
                "territory_id": "4202920",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 10",
            },
            {
                "checksum": "11",
                "date": week_ago + day,
                "territory_id": "4202920",
                "url": "https://queridodiario.ok.org.br/",
                "content": "This is a fake gazette content from ID 11",
            },
        ]
        bulk_data = []
        for gazette in self._data:
            bulk_data.append({"index": {"_index": "gazettes", "_id": gazette["checksum"]}})
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

    def test_get_gazettes_by_keywords(self):
        gazettes = self._mapper.get_gazettes(keywords=["000.000.000-00"])
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"])
            for d in self._data
            if "000.000.000-00" in d["content"]
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

        gazettes = self._mapper.get_gazettes(keywords=["anotherkeyword"])
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"])
            for d in self._data
            if "anotherkeyword" in d["content"]
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

        gazettes = self._mapper.get_gazettes(keywords=["keyword1"])
        expected_gazettes = [
            Gazette(d["territory_id"], d["date"], d["url"])
            for d in self._data
            if "keyword1" in d["content"]
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_get_gazettes_by_keywords_does_not_exist(self):
        gazettes = self._mapper.get_gazettes(keywords=["wasd1234xxx"])
        self.assertEqual(0, len(list(gazettes)), msg="No gazettes should be return ")

    def test_get_gazettes_by_invalid_since_date(self):
        two_months_future = date.today() + timedelta(weeks=8)
        gazettes = self._mapper.get_gazettes(since=two_months_future)
        self.assertEqual(0, len(list(gazettes)), msg="No gazettes should be return ")

    def test_get_gazettes_by_invalid_until_date(self):
        two_months_ago = date.today() - timedelta(weeks=8)
        gazettes = self._mapper.get_gazettes(until=two_months_ago)
        self.assertEqual(0, len(list(gazettes)), msg="No gazettes should be return ")
