from datetime import date, datetime
import json
from typing import Dict, List

import elasticsearch

from gazettes import GazetteDataGateway, Gazette


class ElasticSearchDataMapper(GazetteDataGateway):

    GAZETTE_CONTENT_FIELD = "source_text"

    def __init__(self, host: str, index: str):
        self._index = index
        self._es = elasticsearch.Elasticsearch(hosts=[host])
        if not self._es.indices.exists(index=self._index):
            raise Exception("Index does not exist")

    def build_date_query(self, query, since=None, until=None):
        if since is None and until is None:
            return
        date_query = {"date": {}}
        if since is not None:
            date_query["date"]["gte"] = since.strftime("%Y-%m-%d")
        if until is not None:
            date_query["date"]["lte"] = until.strftime("%Y-%m-%d")
        query["must"].append({"range": date_query})

    def build_territory_query(self, query, territory_id=None):
        if territory_id is not None:
            query["must"].append({"term": {"territory_id": territory_id}})

    def build_sort_query(self, query, order):
        query["sort"] = [{"date": {"order": order}}]

    def build_match_query(self, query, keywords):
        if keywords is not None and len(keywords) > 0:
            query["should"].append(
                {
                    "match": {
                        self.GAZETTE_CONTENT_FIELD: {
                            "query": " ".join(keywords),
                            "operator": "AND",
                        }
                    }
                }
            )
            query["minimum_should_match"] = len(query["should"])

    def build_must_query(self, query, territory_id=None, since=None, until=None):
        self.build_date_query(query, since, until)
        self.build_territory_query(query, territory_id)

    def add_pagination_fields(self, query, offset, size):
        query["from"] = offset
        query["size"] = size

    def add_highlight(
        self, query, fragment_size, number_of_fragments, pre_tags, post_tags
    ):
        query["highlight"] = {
            "fields": {
                "source_text": {
                    "fragment_size": fragment_size,
                    "number_of_fragments": number_of_fragments,
                    "type": "unified",
                    "pre_tags": pre_tags,
                    "post_tags": post_tags,
                }
            }
        }

    def build_query(
        self,
        territory_id: str = None,
        since: date = None,
        until: date = None,
        keywords: list = None,
        offset: int = 0,
        size: int = 10,
        fragment_size: int = 150,
        number_of_fragments: int = 1,
        pre_tags: List[str] = [""],
        post_tags: List[str] = [""],
        sort_by: str = "descending_date",
    ):
        if (
            territory_id is None
            and since is None
            and until is None
            and keywords is None
        ):
            return {"query": {"match_none": {}}}

        query = {
            "must": [],
            "should": [],
        }
        self.build_must_query(query, territory_id, since, until)
        self.build_match_query(query, keywords)
        query = {"query": {"bool": query}}
        self.add_pagination_fields(query, offset, size)

        if sort_by == "descending_date":
            self.build_sort_query(query, "desc")
        elif sort_by == "ascending_date":
            self.build_sort_query(query, "asc")
        # or else sort by relevance (score)

        self.add_highlight(
            query, fragment_size, number_of_fragments, pre_tags, post_tags
        )

        return query

    def _assemble_gazette_object(self, gazette):
        return Gazette(
            gazette["_source"]["territory_id"],
            datetime.strptime(gazette["_source"]["date"], "%Y-%m-%d").date(),
            gazette["_source"]["url"],
            gazette["_source"]["file_checksum"],
            gazette["_source"]["territory_name"],
            gazette["_source"]["state_code"],
            gazette["highlight"].get("source_text", [])
            if "highlight" in gazette
            else [],
            gazette["_source"].get("edition_number", None),
            gazette["_source"].get("is_extra_edition", None),
            gazette["_source"].get("file_raw_txt", None),
        )

    def create_list_with_gazette_objects(self, gazette_hits: List[Dict]):
        return [self._assemble_gazette_object(gazette) for gazette in gazette_hits]

    def get_total_number_items(self, search_response_json: Dict):
        return search_response_json["hits"]["total"]["value"]

    def get_gazettes(
        self,
        territory_id=None,
        since=None,
        until=None,
        keywords=None,
        offset=0,
        size=10,
        fragment_size: int = 150,
        number_of_fragments: int = 1,
        pre_tags: List[str] = [""],
        post_tags: List[str] = [""],
        sort_by: str = "descending_date",
    ):
        query = self.build_query(
            territory_id,
            since,
            until,
            keywords,
            offset,
            size,
            fragment_size,
            number_of_fragments,
            pre_tags,
            post_tags,
            sort_by,
        )
        gazettes = self._es.search(body=query, index=self._index)

        return (
            self.get_total_number_items(gazettes),
            self.create_list_with_gazette_objects(gazettes["hits"]["hits"]),
        )


def create_elasticsearch_data_mapper(
    host: str = None, index: str = None
) -> GazetteDataGateway:
    if host is None or len(host.strip()) == 0:
        raise Exception("Missing host")
    if index is None or len(index.strip()) == 0:
        raise Exception("Missing index name")
    return ElasticSearchDataMapper(host.strip(), index.strip())
