from datetime import date, timedelta
from unittest import TestCase
import os
import unittest
import uuid
import time

import elasticsearch

from database import ElasticSearchDataMapper, create_elasticsearch_data_mapper
from gazettes import GazetteDataGateway, Gazette


FILE_ENDPOINT = "http://test.com"


def is_elasticsearch_status_green(es):
    status = es.cluster.stats()
    if status["status"] == "green":
        return True


def is_elasticsearch_responding():
    for _ in range(10):
        es = elasticsearch.Elasticsearch(hosts=["localhost"])
        if is_elasticsearch_status_green(es):
            return True
        time.sleep(30)
    return False


def setUpModule():
    if not is_elasticsearch_responding():
        raise Exception("Could not connect to Elasticsearch")


class ElasticSearchBaseTestCase(TestCase):

    INDEX = "gazettes"
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
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data[:gazettes_count]
        ]

    def get_expected_document_page(self, page_number, page_size):
        start_slice = 0
        if page_number > 0:
            start_slice = page_number * page_size
        end_slice = start_slice + page_size
        total_documents = len(self._data)
        expected_gazettes = self.get_latest_gazettes_files(total_documents)
        return expected_gazettes[start_slice:end_slice]


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


class ElasticSearchDataMapperTest(ElasticSearchBaseTestCase):

    TERRITORY_ID1 = "3304557"
    TERRITORY_ID2 = "4205902"
    TERRITORY_ID3 = "4205919"
    TERRITORY_ID4 = "4205920"

    def generate_data(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        self._data = [
            {
                "source_text": "This is a fake gazette content",
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
                "territory_id": self.TERRITORY_ID1,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
            },
            {
                "source_text": "This is a fake gazette content",
                "date": date.today() - day,
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
            },
            {
                "source_text": "This is a fake gazette content",
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
                "territory_id": self.TERRITORY_ID2,
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
            },
            {
                "source_text": "This is a fake gazette content. anotherkeyword",
                "date": date.today() - day,
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
            },
            {
                "source_text": "This is a fake gazette content. keyword1",
                "date": date.today() + day,
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
            },
            {
                "source_text": "This is a fake gazette with some keywork which is: 000.000.000-00",
                "date": date.today(),
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
            },
            {
                "source_text": "This is a fake gazette content from ID 6",
                "date": week_ago - day,
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
            },
            {
                "source_text": "This is a fake gazette content from ID 7",
                "date": week_ago,
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
            },
            {
                "source_text": "This is a fake gazette content from ID 8",
                "date": week_ago + day,
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
            },
            {
                "source_text": "This is a fake gazette content from ID 9",
                "date": week_ago - day,
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
            },
            {
                "source_text": "This is a fake gazette content from ID 10",
                "date": week_ago,
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
            },
            {
                "source_text": "This is a fake gazette content from ID 11",
                "date": week_ago + day,
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
            },
        ]

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
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data
        ]
        self.assertGreater(len(gazettes), 0)
        self.assertGreater(gazettes[0].date, gazettes[-1].date)

    def test_search_gazettes_since_date(self):
        gazettes = self._mapper.get_gazettes(since=date.today())
        expected_gazettes = [
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data
            if d["date"] >= date.today()
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_until_date(self):
        yesterday = date.today() - timedelta(days=1)
        gazettes = self._mapper.get_gazettes(until=yesterday)
        expected_gazettes = [
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data
            if d["date"] <= yesterday
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_by_territory_id(self):
        gazettes = list(self._mapper.get_gazettes(territory_id=self.TERRITORY_ID1))
        expected_gazettes = [
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data
            if d["territory_id"] == self.TERRITORY_ID1
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_search_gazettes_by_territory_id_and_dates(self):
        week_ago = date.today() - timedelta(days=7)
        day = timedelta(days=1)
        expected_gazettes = [
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data
            if d["territory_id"] == self.TERRITORY_ID4
            and d["date"] >= (week_ago - day)
            and d["date"] <= (week_ago + day)
        ]

        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID4, since=week_ago - day, until=week_ago + day
        )
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_get_gazettes_by_keywords(self):
        gazettes = self._mapper.get_gazettes(keywords=["000.000.000-00"])
        expected_gazettes = [
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data
            if "000.000.000-00" in d["source_text"]
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

        gazettes = self._mapper.get_gazettes(keywords=["anotherkeyword"])
        expected_gazettes = [
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data
            if "anotherkeyword" in d["source_text"]
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

        gazettes = self._mapper.get_gazettes(keywords=["keyword1"])
        expected_gazettes = [
            Gazette(
                d["territory_id"],
                d["date"],
                d["url"],
                d["territory_name"],
                d["state_code"],
            )
            for d in self._data
            if "keyword1" in d["source_text"]
        ]
        self.assertCountEqual(gazettes, expected_gazettes)

    def test_get_gazettes_by_invalid_since_date(self):
        two_months_future = date.today() + timedelta(weeks=8)
        gazettes = self._mapper.get_gazettes(since=two_months_future)
        self.assertEqual(0, len(list(gazettes)), msg="No gazettes should be return ")

    def test_get_gazettes_by_invalid_until_date(self):
        two_months_ago = date.today() - timedelta(weeks=8)
        gazettes = self._mapper.get_gazettes(until=two_months_ago)
        self.assertEqual(0, len(list(gazettes)), msg="No gazettes should be return ")


class ElasticSearchDataMapperPaginationTest(ElasticSearchBaseTestCase):

    INDEX = "gazettes_pagination"
    TERRITORY_ID = "3304557"

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
            "date": document_date,
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
        }
        self._data.append(gazette)

    def test_page_size(self):
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, page=0, page_size=10
        )
        self.assertEqual(10, len(list(gazettes)), msg="Invalid page size.")
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, page=0, page_size=20
        )
        self.assertEqual(20, len(list(gazettes)), msg="Invalid page size.")
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, page=0, page_size=30
        )
        self.assertEqual(30, len(list(gazettes)), msg="Invalid page size.")

    def test_pages_should_return_gazette_items(self):
        gazettes = list(
            self._mapper.get_gazettes(
                territory_id=self.TERRITORY_ID, page=0, page_size=10
            )
        )
        self.assertNotEqual(0, len(gazettes))
        for gazette in gazettes:
            self.assertIsInstance(gazette, Gazette)

    def test_first_page_should_return_latest_gazettes(self):
        page_size = 10
        gazettes = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, page=0, page_size=page_size
        )
        self.assertCountEqual(gazettes, self.get_expected_document_page(0, page_size))

    def test_consecutive_page_items_should_have_older_dates(self):
        page_size = 10
        first_page = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, page=0, page_size=page_size
        )
        second_page = self._mapper.get_gazettes(
            territory_id=self.TERRITORY_ID, page=1, page_size=page_size
        )
        expected_gazettes = self.get_latest_gazettes_files(20)
        self.assertCountEqual(first_page, expected_gazettes[:page_size])
        self.assertCountEqual(second_page, expected_gazettes[page_size:])

    def test_get_switching_between_gazettes_pages(self):
        page_size = 10
        first_page = list(
            self._mapper.get_gazettes(
                territory_id=self.TERRITORY_ID, page=0, page_size=page_size
            )
        )
        second_page = list(
            self._mapper.get_gazettes(
                territory_id=self.TERRITORY_ID, page=1, page_size=page_size
            )
        )
        first_page_second_time = list(
            self._mapper.get_gazettes(
                territory_id=self.TERRITORY_ID, page=0, page_size=page_size
            )
        )
        second_page_second_time = list(
            self._mapper.get_gazettes(
                territory_id=self.TERRITORY_ID, page=1, page_size=page_size
            )
        )
        expected_second_page = self.get_expected_document_page(1, page_size)
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
        gazettes = self._mapper.get_gazettes(territory_id=self.TERRITORY_ID, page=99)
        self.assertCountEqual(
            [],
            gazettes,
            msg="When requesting a page that does not exists. Not gazettes should be return",
        )

    def test_get_all_pages_available(self):
        page_size = 10
        total_documents = len(self._data)
        for page_number in range(int(total_documents / page_size)):
            page = list(
                self._mapper.get_gazettes(
                    territory_id=self.TERRITORY_ID,
                    page=page_number,
                    page_size=page_size,
                )
            )
            expected_page = self.get_expected_document_page(page_number, page_size)
            self.assertCountEqual(
                page, expected_page, msg=f"Page {page_number} is not right",
            )


class ElasticSearchDataMapperKeywordTest(ElasticSearchBaseTestCase):

    INDEX = "gazettes_keywords"

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
            },
        ]

    def test_get_gazettes_by_keywords_does_not_exist_return_nothing(self):
        gazettes = self._mapper.get_gazettes(keywords=["wasd1234xxx"])
        self.assertEqual(0, len(list(gazettes)), msg="No gazettes should be return ")

    def test_get_gazettes_return_only_documents_containing_all_keywords(self):
        gazettes = self._mapper.get_gazettes(keywords=["prefeitura"])
        self.assertEqual(
            3,
            len(list(gazettes)),
            msg="3 gazettes should be returned because has the keyword 'prefeitura'",
        )

        gazettes = self._mapper.get_gazettes(keywords=["piraporinha"])
        self.assertEqual(
            3,
            len(list(gazettes)),
            msg="3 gazettes should be returned because has the keyword 'piraporinha'",
        )

        gazettes = list(self._mapper.get_gazettes(keywords=["piraporinha", "cafundo"]))
        self.assertEqual(2, len(gazettes), msg="Only 2 gazettes should be return")
