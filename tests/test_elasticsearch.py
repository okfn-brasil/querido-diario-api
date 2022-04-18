from datetime import date, timedelta, datetime
from unittest import TestCase, skip, skipIf, skipUnless
from unittest.mock import patch, MagicMock
import os
import unittest
import uuid
import time

import elasticsearch

from index import ElasticSearchDataMapper, create_elasticsearch_data_mapper
from gazettes import GazetteDataGateway, Gazette


FILE_ENDPOINT = "http://test.com"


class ElasticSearchInterfaceTest(TestCase):
    @patch("elasticsearch.Elasticsearch")
    def test_create_elasticsearch_mapper(self, es_mock):
        mapper = create_elasticsearch_data_mapper("localhost", "gazettes")
        self.assertIsInstance(mapper, GazetteDataGateway)

    @patch("elasticsearch.Elasticsearch")
    @unittest.expectedFailure
    def test_create_elasticsearch_mapper_should_fail_without_host(self, es_mock):
        create_elasticsearch_data_mapper()

    @patch("elasticsearch.Elasticsearch")
    def test_create_elasticsearch_mapper_without_host(self, es_mock):
        with self.assertRaisesRegex(Exception, "Missing host") as cm:
            mapper = create_elasticsearch_data_mapper("", "gazettes")

    @patch("elasticsearch.Elasticsearch")
    def test_create_elasticsearch_mapper_without_index_name(self, es_mock):
        with self.assertRaisesRegex(Exception, "Missing index name") as cm:
            mapper = create_elasticsearch_data_mapper("localhost")

    def configure_es_mock_to_return_itself_in_the_es_constructor(
        self, es_mock, indices_mock
    ):
        es_mock.indices = indices_mock
        es_mock.return_value = es_mock

    @patch("elasticsearch.Elasticsearch")
    @patch("elasticsearch.client.IndicesClient")
    def test_create_elasticsearch_mapper_using_non_existing_index_should_fail(
        self, indices_mock, es_mock
    ):
        indices_mock.exists.return_value = False
        self.configure_es_mock_to_return_itself_in_the_es_constructor(
            es_mock, indices_mock
        )
        with self.assertRaisesRegex(Exception, "Index does not exist") as cm:
            create_elasticsearch_data_mapper("localhost", "zpto")


class ElasticSearchBaseTestCase(TestCase):

    INDEX = "gazettes"
    _data = []

    def build_expected_query(
        self,
        since=None,
        until=None,
        querystring=None,
        territory_id=None,
        offset=0,
        size=10,
    ):
        if not (since or until or territory_id or querystring):
            return {"query": {"match_none": {}}}

        query = {
            "query": {"bool": {"filter": [], "must": []}},
            "from": offset,
            "size": size,
            "sort": [{"date": {"order": "desc"}}],
            "highlight": {
                "fields": {
                    "source_text": {
                        "fragment_size": 150,
                        "number_of_fragments": 1,
                        "type": "unified",
                        "pre_tags": [""],
                        "post_tags": [""],
                    }
                }
            },
        }

        date_query = {"range": {"date": {}}}
        if since:
            date_query["range"]["date"]["gte"] = since.strftime("%Y-%m-%d")
        if until:
            date_query["range"]["date"]["lte"] = until.strftime("%Y-%m-%d")
        if since or until:
            query["query"]["bool"]["filter"].append(date_query)
        if territory_id:
            query["query"]["bool"]["filter"].append(
                {"term": {"territory_id": territory_id}}
            )
        if querystring:
            query["query"]["bool"]["must"].append(
                {
                    "simple_query_string": {
                        "query": querystring,
                        "fields": ["source_text"],
                    }
                }
            )
        return query

    def setUp(self):
        self.es_mock = self.create_patch("elasticsearch.Elasticsearch")
        self.indices_mock = self.create_patch("elasticsearch.client.IndicesClient")
        self.generate_data()
        self._mapper = ElasticSearchDataMapper("localhost", self.INDEX)
        self.configure_es_mock_to_return_itself_in_the_es_constructor()
        self.set_mock_search_return()

    def create_patch(self, name):
        patcher = patch(name)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def configure_es_mock_to_return_itself_in_the_es_constructor(self):
        self.es_mock.indices = self.indices_mock
        self.es_mock = self.es_mock.return_value

    def set_mock_search_return(self):
        hits = [
            {
                "_index": "",
                "_type": "_doc",
                "_id": hit["file_checksum"],
                "_score": None,
                "_source": hit,
                "highlight": {"source_text": []},
            }
            for hit in self._data
        ]
        self.es_mock.search.return_value = {
            "took": 4,
            "timed_out": False,
            "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
            "hits": {
                "total": {"value": len(self._data), "relation": "eq"},
                "max_score": None,
                "hits": hits,
            },
        }

    def get_latest_gazettes_files(self, gazettes_count):
        self._data.sort(reverse=True, key=lambda x: x["date"])
        return [
            Gazette(
                d["territory_id"],
                datetime.strptime(d["date"], "%Y-%m-%d").date(),
                d["url"],
                d["file_checksum"],
                d["territory_name"],
                d["state_code"],
                d["highlight_texts"],
                d["edition_number"],
                d["is_extra_edition"],
            )
            for d in self._data[:gazettes_count]
        ]

    def get_expected_document_page(self, page_number, page_size):
        end_slice = start_slice + page_size
        total_documents = len(self._data)
        expected_gazettes = self.get_latest_gazettes_files(total_documents)
        return expected_gazettes[start_slice:end_slice]


class ElasticSearchDataMapperTest(ElasticSearchBaseTestCase):

    TERRITORY_ID1 = "3304557"
    TERRITORY_ID2 = "4205902"
    TERRITORY_ID3 = "4205919"
    TERRITORY_ID4 = "4205920"
    maxDiff = None

    def generate_data(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        self._data = [
            {
                "source_text": "This is a fake gazette content",
                "date": datetime.strftime(date.today(), "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e5",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID1,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content",
                "date": datetime.strftime(date.today() - day, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e52",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID2,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content",
                "date": datetime.strftime(date.today() + day, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e53",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID2,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content. anotherkeyword",
                "date": datetime.strftime(date.today() - day, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e54",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID1,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content. keyword1",
                "date": datetime.strftime(date.today() + day, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e55",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID2,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette with some keywork which is: 000.000.000-00",
                "date": datetime.strftime(date.today(), "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e56",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID1,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content from ID 6",
                "date": datetime.strftime(week_ago - day, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e57",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID3,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content from ID 7",
                "date": datetime.strftime(week_ago, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e58",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID3,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content from ID 8",
                "date": datetime.strftime(week_ago + day, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e59",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID3,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content from ID 9",
                "date": datetime.strftime(week_ago - day, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e510",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID4,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content from ID 10",
                "date": datetime.strftime(week_ago, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e511",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID4,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content from ID 11",
                "date": datetime.strftime(week_ago + day, "%Y-%m-%d"),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e512",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": self.TERRITORY_ID4,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "edition_number": "123.456",
                "is_extra_edition": False,
                "highlight_texts": [],
            },
        ]

    def assert_query_body_is_correct(
        self,
        since=None,
        until=None,
        querystring=None,
        territory_id=None,
        offset=0,
        size=10,
    ):
        expected_query = self.build_expected_query(
            since=since,
            until=until,
            querystring=querystring,
            territory_id=territory_id,
            offset=offset,
            size=size,
        )
        self.es_mock.search.assert_called_with(body=expected_query, index=self.INDEX)

    def test_get_none_gazettes(self):
        self._data = []
        self.set_mock_search_return()

        gazettes = self._mapper.get_gazettes()[1]

        self.assert_query_body_is_correct()
        self.assertEqual(0, len(gazettes))

    def test_return_gazette_objects(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        gazettes = self._mapper.get_gazettes(since=week_ago - day)[1]
        self.assert_query_body_is_correct(since=week_ago - day)
        self.assertGreater(len(gazettes), 0)
        for gazette in gazettes:
            self.assertIsInstance(gazette, Gazette)

    def test_gazettes_fields(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        gazettes = self._mapper.get_gazettes(since=week_ago - day)[1]
        self.assert_query_body_is_correct(since=week_ago - day)
        for g in gazettes:
            self.assertIsInstance(g.territory_id, str)
            self.assertIsInstance(g.url, str)
            self.assertIsInstance(g.date, date)

    def test_return_get_gazettes_sort_by_date_in_descending_order(self):
        two_weeks_ago = date.today() - timedelta(days=14)
        gazettes = self._mapper.get_gazettes(since=two_weeks_ago)[1]
        expected_gazettes = [
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
                d["highlight_texts"],
                d["edition_number"],
                d["is_extra_edition"],
            )
            for d in self._data
        ]
        self.assert_query_body_is_correct(since=two_weeks_ago)
        self.assertGreater(len(gazettes), 0)
        self.assertGreater(gazettes[0].date, gazettes[-1].date)

    def set_empty_es_return(self):
        self._data = []
        self.set_mock_search_return()

    def set_search_results_should_be_returned(self, indices=[]):
        """
        Define the entries returned by the ES mock in the search method call and
        return a list of Gazettes object of those entries
        """

        data = [self._data[i] for i in indices]
        self._data = data
        self.set_mock_search_return()

        expected_gazettes = [
            Gazette(
                d["territory_id"],
                datetime.strptime(d["date"], "%Y-%m-%d").date(),
                d["url"],
                d["file_checksum"],
                d["territory_name"],
                d["state_code"],
                d["highlight_texts"],
                d["edition_number"],
                d["is_extra_edition"],
            )
            for d in self._data
        ]

        return expected_gazettes

    def test_search_gazettes_since_date(self):
        expected_gazettes = self.set_search_results_should_be_returned(
            indices=[0, 2, 4, 5]
        )
        today = date.today()
        gazettes = self._mapper.get_gazettes(since=today)[1]

        self.assert_query_body_is_correct(since=today)
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_until_date(self):
        expected_gazettes = self.set_search_results_should_be_returned(
            indices=[1, 3, 6, 7, 8, 9, 10, 11]
        )
        yesterday = date.today() - timedelta(days=1)
        gazettes = self._mapper.get_gazettes(until=yesterday)[1]

        self.assert_query_body_is_correct(until=yesterday)
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_by_territory_id(self):
        expected_gazettes = self.set_search_results_should_be_returned(
            indices=[0, 3, 5]
        )
        gazettes = self._mapper.get_gazettes(territory_id=self.TERRITORY_ID1)[1]
        self.assert_query_body_is_correct(territory_id=self.TERRITORY_ID1)
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_by_territory_id_and_dates(self):
        expected_gazettes = self.set_search_results_should_be_returned(
            indices=[9, 10, 11]
        )
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID4, since=week_ago - day, until=week_ago + day
        )[1]
        self.assert_query_body_is_correct(
            territory_id=self.TERRITORY_ID4, since=week_ago - day, until=week_ago + day
        )
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_get_gazettes_by_querystring(self):
        expected_gazettes = self.set_search_results_should_be_returned(indices=[3])
        gazettes = self._mapper.get_gazettes(querystring="anotherkeyword")[1]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_get_gazettes_by_invalid_since_date(self):
        self.set_empty_es_return()
        two_months_future = date.today() + timedelta(weeks=8)
        gazettes = self._mapper.get_gazettes(since=two_months_future)[1]
        self.assertEqual(0, len(gazettes), msg="No gazettes should be return ")

    def test_get_gazettes_by_invalid_until_date(self):
        self.set_empty_es_return()
        two_months_ago = date.today() - timedelta(weeks=8)
        gazettes = self._mapper.get_gazettes(until=two_months_ago)[1]
        self.assertEqual(0, len(gazettes), msg="No gazettes should be return ")

    def test_from_and_size_fields(self):
        today = date.today()
        self._mapper.get_gazettes(until=today, offset=5, size=15)
        self.assert_query_body_is_correct(until=today, offset=5, size=15)


def is_running_integration_tests():
    return os.environ.get("RUN_INTEGRATION_TESTS", 0) == "1"


class ElasticSearchIntegrationBaseTestCase(TestCase):
    _data = []

    def delete_index(self):
        for attempt in range(3):
            try:
                self._es.indices.delete(
                    index=self.INDEX, ignore_unavailable=True, timeout="30s"
                )
                self._es.indices.refresh()
                return
            except Exception as e:
                time.sleep(10)

    def create_index(self):
        for attempt in range(3):
            try:
                self._es.indices.create(
                    index=self.INDEX,
                    body={"mappings": {"properties": {"date": {"type": "date"}}}},
                    timeout="30s",
                )
                self._es.indices.refresh()
                return
            except Exception as e:
                time.sleep(10)

    def recreate_index(self):
        self.delete_index()
        self.create_index()

    def try_push_data_to_index(self, bulk_data):
        for attempt in range(3):
            try:
                self._es.bulk(bulk_data, index=self.INDEX, refresh=True, timeout="30s")
                return
            except Exception as e:
                time.sleep(10)

    def add_data_on_index(self):
        bulk_data = []
        for gazette in self._data:
            bulk_data.append(
                {"index": {"_index": self.INDEX, "_id": gazette["file_checksum"]}}
            )
            bulk_data.append(gazette)
        self.try_push_data_to_index(bulk_data)

    def setUp(self):
        self._es = elasticsearch.Elasticsearch(hosts=["localhost"])
        self.recreate_index()
        self.generate_data()
        self.add_data_on_index()
        self._mapper = create_elasticsearch_data_mapper("localhost", self.INDEX)

    def tearDown(self):
        self._es.close()

    def get_latest_gazettes_files(self, gazettes_count):
        self._data.sort(reverse=True, key=lambda x: x["date"])
        return [
            Gazette(
                d["territory_id"],
                datetime.strptime(d["date"], "%Y-%m-%d").date(),
                d["url"],
                d["file_checksum"],
                d["territory_name"],
                d["state_code"],
                d["highlight_texts"],
                d["edition_number"],
                d["is_extra_edition"],
            )
            for d in self._data[:gazettes_count]
        ]

    def get_expected_document_page(self, offset, size):
        total_documents = len(self._data)
        expected_gazettes = self.get_latest_gazettes_files(total_documents)
        return expected_gazettes[offset : offset + size]


@skipUnless(is_running_integration_tests(), "Integration tests disable")
class ElasticSearchDataMapperPaginationTest(ElasticSearchIntegrationBaseTestCase):

    INDEX = "gazettes_pagination"
    TERRITORY_ID = "3304557"
    maxDiff = None

    def generate_data(self):
        if len(self._data) > 0:
            return
        for days_old in range(50):
            self.create_new_fake_gazette(days_old)

    def create_new_fake_gazette(self, days_old: int):
        document_uuid = str(uuid.uuid1())
        document_date = date.today() - timedelta(days=days_old)
        gazette = {
            "source_text": "This is a fake gazette content",
            "date": datetime.strftime(document_date, "%Y-%m-%d"),
            "edition_number": None,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": document_uuid,
            "file_path": f"3304557/2019-02-26/{document_uuid}",
            "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/{document_uuid}",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": self.TERRITORY_ID,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "highlight_texts": [],
        }
        self._data.append(gazette)

    def assert_basic_function_calls(
        self,
        since=None,
        until=None,
        querystring=None,
        territory_id=None,
        offset=0,
        size=10,
    ):
        expected_query = self.build_expected_query(
            since=since,
            until=until,
            querystring=querystring,
            territory_id=territory_id,
            offset=offset,
            size=size,
        )
        self.es_mock.search.assert_called_with(body=expected_query, index=self.INDEX)

    def test_page_size(self):
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=0, size=10
        )[1]
        self.assertEqual(10, len(gazettes), msg="Invalid page size.")
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=0, size=20
        )[1]
        self.assertEqual(20, len(gazettes), msg="Invalid page size.")
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=0, size=30
        )[1]
        self.assertEqual(30, len(gazettes), msg="Invalid page size.")

    def test_pages_should_return_gazette_items(self):
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=0, size=10
        )[1]
        self.assertNotEqual(0, len(gazettes))
        for gazette in gazettes:
            self.assertIsInstance(gazette, Gazette)

    def test_first_page_should_return_latest_gazettes(self):
        page_size = 10
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=0, size=page_size
        )[1]
        self.assertCountEqual(gazettes, self.get_expected_document_page(0, page_size))

    def test_consecutive_page_items_should_have_older_dates(self):
        page_size = 10
        first_page = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=0, size=page_size
        )[1]
        second_page = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=page_size, size=page_size
        )[1]
        expected_gazettes = self.get_latest_gazettes_files(20)
        self.assertCountEqual(first_page, expected_gazettes[:page_size])
        self.assertCountEqual(second_page, expected_gazettes[page_size:])

    def test_get_switching_between_gazettes_pages(self):
        page_size = 10
        first_page = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=0, size=page_size
        )[1]
        second_page = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=page_size, size=page_size
        )[1]
        first_page_second_time = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=0, size=page_size
        )[1]
        second_page_second_time = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=page_size, size=page_size
        )[1]
        expected_second_page = self.get_expected_document_page(page_size, page_size)
        expected_first_page = self.get_expected_document_page(0, page_size)

        self.assertCountEqual(
            first_page, expected_first_page, msg="Unexpected first page"
        )
        self.assertCountEqual(
            second_page, expected_second_page, msg="Unexpected second page"
        )
        self.assertCountEqual(
            first_page_second_time, expected_first_page, msg="Unexpected first page"
        )
        self.assertCountEqual(
            second_page_second_time, expected_second_page, msg="Unexpected second page"
        )
        self.assertCountEqual(
            first_page,
            first_page_second_time,
            msg="Page request second time is different from the first one",
        )
        self.assertCountEqual(
            second_page,
            second_page_second_time,
            msg="Page request second time is different from the first one",
        )

    def test_get_page_does_not_exist(self):
        _, gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, offset=99
        )
        self.assertCountEqual(
            [],
            gazettes,
            msg="When requesting a page that does not exists. Not gazettes should be return",
        )

    def test_get_all_pages_available(self):
        page_size = 10
        total_documents = len(self._data)
        for page_number in range(int(total_documents / page_size)):
            page = self._mapper.get_gazettes(
                territory_id=self.TERRITORY_ID,
                offset=page_size * page_number,
                size=page_size,
            )[1]
            expected_page = self.get_expected_document_page(
                page_size * page_number, page_size
            )
            self.assertCountEqual(
                page, expected_page, msg=f"Page {page_number} is not right",
            )


@skipUnless(is_running_integration_tests(), "Integration tests disable")
class ElasticSearchDataMapperQuerystringTest(ElasticSearchIntegrationBaseTestCase):

    INDEX = "gazettes_querystring"

    def generate_data(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        self._data = [
            {
                "source_text": "This is a fake gazette content. prefeitura",
                "date": date.today(),
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e5",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": "3304557",
                "processed": False,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content. prefeitura foobar xpto piraporinha",
                "date": date.today() - day,
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e51",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": "3304557",
                "processed": False,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content. prefeitura, piraporinha and cafundo",
                "date": date.today() + day,
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e52",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": "3304557",
                "processed": False,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "highlight_texts": [],
            },
            {
                "source_text": "This is a fake gazette content. piraporinha and cafundo",
                "date": date.today() + day,
                "edition_number": None,
                "is_extra_edition": False,
                "power": "executive",
                "file_checksum": "2566f0e0ff98d899ee0633da64bc65e53",
                "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "url": f"{FILE_ENDPOINT}/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                "scraped_at": "2020-10-30T07:04:29.796347",
                "created_at": "2020-10-30T07:05:33.094289",
                "territory_id": "3304557",
                "processed": False,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
                "highlight_texts": [],
            },
        ]

    def test_get_gazettes_should_not_error_with_malformed_querystring(self):
        _, gazettes = self._mapper.get_gazettes(querystring="prefeitura + ´[")
        self.assertEqual(
            3,
            len(gazettes),
            msg="3 gazettes should contain the keyword 'prefeitura' and ignore the malformed end of the querystring: 'prefeitura + ´['",
        )

    def test_get_gazettes_by_keywords(self):
        _, gazettes = self._mapper.get_gazettes(querystring="prefeitura")
        self.assertEqual(
            3, len(gazettes), msg="3 gazettes should contain the keyword 'prefeitura'",
        )

        _, gazettes = self._mapper.get_gazettes(querystring="foobar cafundo")
        self.assertEqual(
            3,
            len(gazettes),
            msg="3 gazettes should contain the keywords 'foobar' or 'cafundo'",
        )

        _, gazettes = self._mapper.get_gazettes(querystring="wasd1234xxx")
        self.assertEqual(
            0, len(gazettes), msg="0 gazettes should contain the word 'wasd1234xxx'"
        )

    def test_get_gazettes_by_phrase(self):
        _, gazettes = self._mapper.get_gazettes(querystring='"content. prefeitura"')
        self.assertEqual(
            3,
            len(gazettes),
            msg="3 gazettes should contain the phrase 'content. prefeitura'",
        )

        _, gazettes = self._mapper.get_gazettes(
            querystring='"content. prefeitura" cafundo'
        )
        self.assertEqual(
            4,
            len(gazettes),
            msg="4 gazettes should contain the phrase 'content. prefeitura' or the word 'cafundo'",
        )

        _, gazettes = self._mapper.get_gazettes(
            querystring='"content. prefeitura cafundo"'
        )
        self.assertEqual(
            0,
            len(gazettes),
            msg="0 gazettes should contain the phrase 'content. prefeitura cafundo'",
        )

    def test_get_gazettes_by_negation_operator(self):
        _, gazettes = self._mapper.get_gazettes(querystring="-piraporinha")
        self.assertEqual(
            1,
            len(gazettes),
            msg="1 gazette should not contain the keyword 'piraporinha'",
        )

        _, gazettes = self._mapper.get_gazettes(querystring="-gazette")
        self.assertEqual(
            0, len(gazettes), msg="0 gazettes should not contain the keyword 'gazette'",
        )

    def test_get_gazettes_by_prefix_operator(self):
        _, gazettes = self._mapper.get_gazettes(querystring="gaz*")
        self.assertEqual(
            4, len(gazettes), msg="4 gazettes should contain words with prefix 'gaz'",
        )

        _, gazettes = self._mapper.get_gazettes(querystring="gazz*")
        self.assertEqual(
            0, len(gazettes), msg="0 gazettes should contain words with prefix 'gazz'",
        )

    def test_get_gazettes_by_fuzzy_operator(self):
        _, gazettes = self._mapper.get_gazettes(querystring="foobiz~2")
        self.assertEqual(
            1,
            len(gazettes),
            msg="1 gazette should contain words similar to 'foobiz' at a maximum edit distance of 2",
        )

        _, gazettes = self._mapper.get_gazettes(querystring="foobiz~1")
        self.assertEqual(
            0,
            len(gazettes),
            msg="0 gazettes should contain words similar to 'foobiz' at a maximum edit distance of 1",
        )

    def test_get_gazettes_by_slop_operator(self):
        _, gazettes = self._mapper.get_gazettes(
            querystring='"prefeitura piraporinha"~1'
        )
        self.assertEqual(
            1,
            len(gazettes),
            msg="1 gazette should contain the words 'prefeitura' and 'piraporinha' with 1 word between them at maximum",
        )

        _, gazettes = self._mapper.get_gazettes(
            querystring='"prefeitura piraporinha"~2'
        )
        self.assertEqual(
            2,
            len(gazettes),
            msg="2 gazettes should contain the words 'prefeitura' and 'piraporinha' with 2 words between them at maximum",
        )

    def test_get_gazettes_by_and_operator(self):
        _, gazettes = self._mapper.get_gazettes(querystring="prefeitura + cafundo")
        self.assertEqual(
            1,
            len(gazettes),
            msg="1 gazette should contain both the keywords 'prefeitura' and 'cafundo'",
        )

    def test_get_gazettes_by_or_operator(self):
        _, gazettes = self._mapper.get_gazettes(
            querystring="(prefeitura + cafundo) | foobar"
        )
        self.assertEqual(
            2,
            len(gazettes),
            msg="2 gazettes should contain both the keywords 'prefeitura' and 'cafundo' or the keyword 'foobar'",
        )

    def test_get_gazettes_by_precedence_operator(self):
        _, gazettes = self._mapper.get_gazettes(
            querystring="(prefeitura + xpto) | cafundo"
        )
        self.assertEqual(
            3,
            len(gazettes),
            msg="3 gazettes should contain both the keywords 'prefeitura' and 'xpto' or the keyword 'cafundo'",
        )

        _, gazettes = self._mapper.get_gazettes(
            querystring="prefeitura + (xpto | cafundo)"
        )
        self.assertEqual(
            2,
            len(gazettes),
            msg="2 gazettes should contain the keyword 'prefeitura' and the keywords 'cafundo' or 'xpto'",
        )


class Elasticsearch(TestCase):
    def setUp(self):
        self.host = "localhost"
        self.index = "gazettes"
        self.search_result_json = {
            "took": 4,
            "timed_out": False,
            "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
            "hits": {
                "total": {"value": 8, "relation": "eq"},
                "max_score": None,
                "hits": [
                    {
                        "_index": "gazettes",
                        "_type": "_doc",
                        "_id": "2566f0e0ff98d899ee0633da64bc65e52",
                        "_score": None,
                        "_source": {
                            "source_text": "This is a fake gazette content",
                            "date": "2021-01-07",
                            "edition_number": "123.456",
                            "is_extra_edition": False,
                            "power": "executive",
                            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e52",
                            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "url": "http://test.com/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                            "scraped_at": "2020-10-30T07:04:29.796347",
                            "created_at": "2020-10-30T07:05:33.094289",
                            "territory_id": "4205902",
                            "territory_name": "Rio de Janeiro",
                            "state_code": "RJ",
                        },
                        "highlight": {"source_text": []},
                        "sort": [1609977600000],
                    },
                    {
                        "_index": "gazettes",
                        "_type": "_doc",
                        "_id": "2566f0e0ff98d899ee0633da64bc65e54",
                        "_score": None,
                        "_source": {
                            "source_text": "This is a fake gazette content. anotherkeyword",
                            "date": "2021-01-07",
                            "edition_number": "123.456",
                            "is_extra_edition": False,
                            "power": "executive",
                            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e54",
                            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "url": "http://test.com/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                            "scraped_at": "2020-10-30T07:04:29.796347",
                            "created_at": "2020-10-30T07:05:33.094289",
                            "territory_id": "3304557",
                            "territory_name": "Rio de Janeiro",
                            "state_code": "RJ",
                        },
                        "highlight": {"source_text": []},
                        "sort": [1609977600000],
                    },
                    {
                        "_index": "gazettes",
                        "_type": "_doc",
                        "_id": "2566f0e0ff98d899ee0633da64bc65e59",
                        "_score": None,
                        "_source": {
                            "source_text": "This is a fake gazette content from ID 8",
                            "date": "2021-01-02",
                            "edition_number": "123.456",
                            "is_extra_edition": False,
                            "power": "executive",
                            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e59",
                            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "url": "http://test.com/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                            "scraped_at": "2020-10-30T07:04:29.796347",
                            "created_at": "2020-10-30T07:05:33.094289",
                            "territory_id": "4205919",
                            "territory_name": "Rio de Janeiro",
                            "state_code": "RJ",
                        },
                        "highlight": {"source_text": []},
                        "sort": [1609545600000],
                    },
                    {
                        "_index": "gazettes",
                        "_type": "_doc",
                        "_id": "2566f0e0ff98d899ee0633da64bc65e512",
                        "_score": None,
                        "_source": {
                            "source_text": "This is a fake gazette content from ID 11",
                            "date": "2021-01-02",
                            "edition_number": "123.456",
                            "is_extra_edition": False,
                            "power": "executive",
                            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e512",
                            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "url": "http://test.com/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                            "scraped_at": "2020-10-30T07:04:29.796347",
                            "created_at": "2020-10-30T07:05:33.094289",
                            "territory_id": "4205920",
                            "territory_name": "Rio de Janeiro",
                            "state_code": "RJ",
                        },
                        "highlight": {"source_text": []},
                        "sort": [1609545600000],
                    },
                    {
                        "_index": "gazettes",
                        "_type": "_doc",
                        "_id": "2566f0e0ff98d899ee0633da64bc65e58",
                        "_score": None,
                        "_source": {
                            "source_text": "This is a fake gazette content from ID 7",
                            "date": "2021-01-01",
                            "edition_number": "123.456",
                            "is_extra_edition": False,
                            "power": "executive",
                            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e58",
                            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "url": "http://test.com/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                            "scraped_at": "2020-10-30T07:04:29.796347",
                            "created_at": "2020-10-30T07:05:33.094289",
                            "territory_id": "4205919",
                            "territory_name": "Rio de Janeiro",
                            "state_code": "RJ",
                        },
                        "highlight": {"source_text": []},
                        "sort": [1609459200000],
                    },
                    {
                        "_index": "gazettes",
                        "_type": "_doc",
                        "_id": "2566f0e0ff98d899ee0633da64bc65e511",
                        "_score": None,
                        "_source": {
                            "source_text": "This is a fake gazette content from ID 10",
                            "date": "2021-01-01",
                            "edition_number": "123.456",
                            "is_extra_edition": False,
                            "power": "executive",
                            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e511",
                            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "url": "http://test.com/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                            "scraped_at": "2020-10-30T07:04:29.796347",
                            "created_at": "2020-10-30T07:05:33.094289",
                            "territory_id": "4205920",
                            "territory_name": "Rio de Janeiro",
                            "state_code": "RJ",
                        },
                        "highlight": {"source_text": []},
                        "sort": [1609459200000],
                    },
                    {
                        "_index": "gazettes",
                        "_type": "_doc",
                        "_id": "2566f0e0ff98d899ee0633da64bc65e57",
                        "_score": None,
                        "_source": {
                            "source_text": "This is a fake gazette content from ID 6",
                            "date": "2020-12-31",
                            "edition_number": "123.456",
                            "is_extra_edition": False,
                            "power": "executive",
                            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e57",
                            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "url": "http://test.com/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                            "scraped_at": "2020-10-30T07:04:29.796347",
                            "created_at": "2020-10-30T07:05:33.094289",
                            "territory_id": "4205919",
                            "territory_name": "Rio de Janeiro",
                            "state_code": "RJ",
                        },
                        "highlight": {"source_text": []},
                        "sort": [1609372800000],
                    },
                    {
                        "_index": "gazettes",
                        "_type": "_doc",
                        "_id": "2566f0e0ff98d899ee0633da64bc65e510",
                        "_score": None,
                        "_source": {
                            "source_text": "This is a fake gazette content from ID 9",
                            "date": "2020-12-31",
                            "edition_number": "123.456",
                            "is_extra_edition": False,
                            "power": "executive",
                            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e510",
                            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "url": "http://test.com/3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
                            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
                            "scraped_at": "2020-10-30T07:04:29.796347",
                            "created_at": "2020-10-30T07:05:33.094289",
                            "territory_id": "4205920",
                            "territory_name": "Rio de Janeiro",
                            "state_code": "RJ",
                        },
                        "highlight": {"source_text": []},
                        "sort": [1609372800000],
                    },
                ],
            },
        }

    def test_elasticsearch_data_mapper_creation(self):
        with patch("elasticsearch.Elasticsearch") as es_mock:
            es = ElasticSearchDataMapper(self.host, self.index)
            es._es.indices.exists.assert_called_once()

    @patch("elasticsearch.Elasticsearch")
    def test_get_total_number_items(self, es_mock):
        es = ElasticSearchDataMapper(self.host, self.index)
        total_items = es.get_total_number_items(self.search_result_json)
        self.assertEqual(total_items, 8)

    @patch("elasticsearch.Elasticsearch")
    def test_total_number_of_items_found_return(self, es_mock):
        es_mock.search.return_value = self.search_result_json
        es = ElasticSearchDataMapper(self.host, self.index)
        es._es = es_mock

        total_items, _ = es.get_gazettes("4205920", None, None, None, 1, 4)
        self.assertEqual(total_items, 8)
