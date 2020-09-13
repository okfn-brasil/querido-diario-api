import json
import datetime
import elasticsearch

from gazettes import GazetteDataGateway, Gazette


class ElasticSearchDataMapper(GazetteDataGateway):
    def __init__(self, host: str, index: str):
        self._index = index
        self._es = elasticsearch.Elasticsearch(hosts=[host])

    def build_date_query(self, since=None, until=None):
        date_query = {"date": {}}
        if since is not None:
            date_query["date"]["gte"] = since.strftime("%Y-%m-%d")
        if until is not None:
            date_query["date"]["lte"] = until.strftime("%Y-%m-%d")
        return {"range": date_query}

    def build_territory_query(self, territory_id=None):
        return {"term": {"territory_id": territory_id}}

    def build_sort_query(self):
        return [{"date": {"order": "desc"}}, {"id": "asc"}]

    def build_query(self, territory_id=None, since=None, until=None, search_after=None):
        must_query = []
        if since is not None or until is not None:
            must_query.append(self.build_date_query(since, until))
        if territory_id is not None:
            must_query.append(self.build_territory_query(territory_id))
        query = {"query": {"match_none": {}}}
        if len(must_query) > 0:
            query = {"query": {"bool": {"must": must_query}}}
        query["sort"] = self.build_sort_query()
        if search_after is not None:
            query["search_after"] = search_after
        return query

    def get_gazettes(self, territory_id=None, since=None, until=None):
        query = self.build_query(territory_id, since, until)
        gazettes = self._es.search(body=query, index=self._index)
        total_documents = gazettes["hits"]["total"]["value"]

        while total_documents > 0:
            for gazette in gazettes["hits"]["hits"]:
                total_documents -= 1
                yield Gazette(
                    gazette["_source"]["territory_id"],
                    datetime.datetime.strptime(
                        gazette["_source"]["date"], "%Y-%m-%d"
                    ).date(),
                    gazette["_source"]["url"],
                )
            query = self.build_query(
                territory_id, since, until, gazettes["hits"]["hits"][-1]["sort"]
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
