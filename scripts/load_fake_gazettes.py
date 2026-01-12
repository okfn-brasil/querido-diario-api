from datetime import date, timedelta
import time

import opensearchpy

TERRITORY_ID1 = "3304557"
TERRITORY_ID2 = "4205902"
TERRITORY_ID3 = "4205919"
TERRITORY_ID4 = "4205920"
INDEX = "querido-diario"


def delete_index(search_engine):
    for attempt in range(3):
        try:
            search_engine.indices.delete(
                index=INDEX, ignore_unavailable=True, timeout=30
            )
            search_engine.indices.refresh()
            print("Index deleted")
            return
        except Exception as e:
            print("Index deletion failed")
            time.sleep(10)


def create_index(search_engine):
    for attempt in range(3):
        try:
            search_engine.indices.create(
                index=INDEX,
                timeout=30,
                body={
                    "mappings": {
                        "properties": {
                            "created_at": {"type": "date"},
                            "date": {"type": "date"},
                            "edition_number": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "file_checksum": {"type": "keyword"},
                            "file_path": {"type": "keyword"},
                            "file_url": {"type": "keyword"},
                            "id": {"type": "keyword"},
                            "is_extra_edition": {"type": "boolean"},
                            "power": {"type": "keyword"},
                            "processed": {"type": "boolean"},
                            "scraped_at": {"type": "date"},
                            "source_text": {
                                "type": "text",
                                "analyzer": "brazilian",
                                "index_options": "offsets",
                                "term_vector": "with_positions_offsets",
                                "fields": {
                                    "with_stopwords": {
                                        "type": "text",
                                        "analyzer": "brazilian_with_stopwords",
                                        "index_options": "offsets",
                                        "term_vector": "with_positions_offsets",
                                    },
                                    "exact": {
                                        "type": "text",
                                        "analyzer": "exact",
                                        "index_options": "offsets",
                                        "term_vector": "with_positions_offsets",
                                    },
                                },
                            },
                            "state_code": {"type": "keyword"},
                            "territory_id": {"type": "keyword"},
                            "territory_name": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "url": {"type": "keyword"},
                        }
                    },
                    "settings": {
                        "index": {
                            "sort.field": ["territory_id", "date"],
                            "sort.order": ["asc", "desc"],
                        },
                        "analysis": {
                            "filter": {
                                "brazilian_stemmer": {
                                    "type": "stemmer",
                                    "language": "brazilian",
                                }
                            },
                            "analyzer": {
                                "brazilian_with_stopwords": {
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "brazilian_stemmer"],
                                },
                                "exact": {
                                    "tokenizer": "standard",
                                    "filter": ["lowercase"],
                                },
                            },
                        },
                    },
                },
            )
            search_engine.indices.refresh()
            print(f"Index {INDEX} created")
            return
        except Exception as e:
            print(f"Index creation failed: {e}")
            time.sleep(10)


def recreate_index(search_engine):
    delete_index(search_engine)
    create_index(search_engine)


def try_push_data_to_index(search_engine, bulk_data):
    for attempt in range(3):
        try:
            search_engine.bulk(bulk_data, index=INDEX, refresh=True, timeout=30)
            return
        except Exception as e:
            print(f"Failed populating index: {e}")
            time.sleep(10)


def add_data_on_index(data, search_engine):
    bulk_data = []
    for gazette in data:
        bulk_data.append({"index": {"_index": INDEX, "_id": gazette["file_checksum"]}})
        bulk_data.append(gazette)
    try_push_data_to_index(search_engine, bulk_data)
    print("Index populated")


def get_data():
    week_ago = date.today() - timedelta(days=7)
    day = timedelta(days=1)
    return [
        {
            "source_text": "This is a fake gazette content",
            "date": date.today(),
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e5",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID1,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content",
            "date": date.today() - day,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e52",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID2,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content",
            "date": date.today() + day,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e53",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID2,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content. anotherkeyword",
            "date": date.today() - day,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e54",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID1,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content. keyword1",
            "date": date.today() + day,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e55",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID2,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette with some keywork which is: 000.000.000-00",
            "date": date.today(),
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e56",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID1,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content from ID 6",
            "date": week_ago - day,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e57",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID3,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content from ID 7",
            "date": week_ago,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e58",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID3,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content from ID 8",
            "date": week_ago + day,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e59",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID3,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content from ID 9",
            "date": week_ago - day,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e510",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID4,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content from ID 10",
            "date": week_ago,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e511",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID4,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content from ID 11",
            "date": week_ago + day,
            "is_extra_edition": False,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e512",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID4,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
            "edition_number": "123.45",
            "is_extra_edition": False,
        },
        {
            "source_text": "This is a fake gazette content from ID 11",
            "date": week_ago + day,
            "power": "executive",
            "file_checksum": "2566f0e0ff98d899ee0633da64bc65e512",
            "file_path": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee",
            "file_raw_txt": "3304557/2019-02-26/c942328486185aa09ec19a7c723b3a33847258ee.txt",
            "file_url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "url": "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067",
            "scraped_at": "2020-10-30T07:04:29.796347",
            "created_at": "2020-10-30T07:05:33.094289",
            "territory_id": TERRITORY_ID4,
            "territory_name": "Rio de Janeiro",
            "state_code": "RJ",
        },
    ]


def main():
    search_engine = opensearchpy.OpenSearch(
        hosts=["localhost"], http_auth=("admin", "admin")
    )
    recreate_index(search_engine)
    add_data_on_index(get_data(), search_engine)


if __name__ == "__main__":
    main()
