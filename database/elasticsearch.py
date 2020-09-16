from datetime import date, datetime

import elasticsearch

from gazettes import GazetteDataGateway, Gazette


class ElasticSearchDataMapper(GazetteDataGateway):
    def __init__(self, host: str, index: str):
        self._index = index
        self._es = elasticsearch.Elasticsearch(hosts=[host])

    def build_date_query(self, must_query, since=None, until=None):
        if since is None and until is None:
            return
        date_query = {"date": {}}
        if since is not None:
            date_query["date"]["gte"] = since.strftime("%Y-%m-%d")
        if until is not None:
            date_query["date"]["lte"] = until.strftime("%Y-%m-%d")
        must_query.append({"range": date_query})

    def build_territory_query(self, must_query, territory_id=None):
        if territory_id is not None:
            must_query.append({"term": {"territory_id": territory_id}})

    def build_sort_query(self, query):
        query["sort"] = [{"date": {"order": "desc"}}, {"id": "asc"}]

    def build_match_query(self, query, keywords):
        if keywords is not None and len(keywords) > 0:
            if "query" not in query:
                query["query"] = {}
            query["query"]["match"] = {"content": " ".join(keywords)}

    def add_must_query_in_query_object(self, query, must_query):
        if len(must_query) > 0:
            if "query" not in query:
                query["query"] = {}
            query["query"]["bool"] = {"must": must_query}

    def build_must_query(self, query, territory_id=None, since=None, until=None):
        must_query = []
        self.build_date_query(must_query, since, until)
        self.build_territory_query(must_query, territory_id)
        self.add_must_query_in_query_object(query, must_query)

    def add_search_after(self, query, search_after):
        if search_after is not None:
            query["search_after"] = search_after

    def build_query(
        self,
        territory_id: str = None,
        since: date = None,
        until: date = None,
        search_after=None,
        keywords: list = None,
    ):
        query = {}
        self.build_must_query(query, territory_id, since, until)
        self.build_sort_query(query)
        self.build_match_query(query, keywords)
        self.add_search_after(query, search_after)

        if "query" not in query:
            query["query"] = {"match_none": {}}

        print(query)
        return query

    def get_gazettes(self, territory_id=None, since=None, until=None, keywords=None):
        query = self.build_query(territory_id, since, until, keywords=keywords)
        gazettes = self._es.search(body=query, index=self._index)
        total_documents = gazettes["hits"]["total"]["value"]

        while total_documents > 0:
            for gazette in gazettes["hits"]["hits"]:
                total_documents -= 1
                yield Gazette(
                    gazette["_source"]["territory_id"],
                    datetime.strptime(gazette["_source"]["date"], "%Y-%m-%d").date(),
                    gazette["_source"]["url"],
                )
            query = self.build_query(
                territory_id,
                since,
                until,
                gazettes["hits"]["hits"][-1]["sort"],
                keywords,
            )
            gazettes = self._es.search(body=query, index=self._index)


def create_elasticsearch_data_mapper(
    host: str = None, index: str = None
) -> GazetteDataGateway:
    if host is None or len(host.strip()) == 0:
        raise Exception("Missing host")
    if index is None or len(index.strip()) == 0:
        raise Exception("Missing index name")
    return ElasticSearchDataMapper(host.strip(), index.strip())