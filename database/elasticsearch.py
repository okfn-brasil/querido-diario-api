from datetime import date, datetime

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

    def build_sort_query(self, query):
        query["sort"] = [{"date": {"order": "desc"}}]

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

    def add_pagination_fields(self, query, page, page_size):
        query["from"] = page * page_size
        query["size"] = page_size

    def build_query(
        self,
        territory_id: str = None,
        since: date = None,
        until: date = None,
        keywords: list = None,
        page: int = 0,
        page_size: int = 10,
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
        self.add_pagination_fields(query, page, page_size)
        self.build_sort_query(query)

        return query

    def get_gazettes(
        self,
        territory_id=None,
        since=None,
        until=None,
        keywords=None,
        page=0,
        page_size=10,
    ):
        query = self.build_query(territory_id, since, until, keywords, page, page_size,)
        gazettes = self._es.search(body=query, index=self._index)

        for gazette in gazettes["hits"]["hits"]:
            yield Gazette(
                gazette["_source"]["territory_id"],
                datetime.strptime(gazette["_source"]["date"], "%Y-%m-%d").date(),
                gazette["_source"]["file_path"],
            )


def create_elasticsearch_data_mapper(
    host: str = None, index: str = None
) -> GazetteDataGateway:
    if host is None or len(host.strip()) == 0:
        raise Exception("Missing host")
    if index is None or len(index.strip()) == 0:
        raise Exception("Missing index name")
    return ElasticSearchDataMapper(host.strip(), index.strip())
