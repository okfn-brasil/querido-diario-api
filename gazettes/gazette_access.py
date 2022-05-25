import abc
from datetime import date, datetime
from typing import Dict, List, Union

from index import SearchEngineInterface
from index.elasticsearch import (
    QueryBuilderInterface,
    DateRangeQueryMixin,
    SimpleStringQueryMixin,
    SortMixin,
    TermsQueryMixin,
    BoolQueryMixin,
    MatchNoneQueryMixin,
    FieldSortOrder,
    PaginationMixin,
    HighlightMixin,
)


class GazetteRequest:
    """
    Object containing the data to filter gazettes
    """

    def __init__(
        self,
        territory_ids: List[str],
        since: Union[date, None],
        until: Union[date, None],
        querystring: str,
        excerpt_size: int,
        number_of_excerpts: int,
        pre_tags: List[str],
        post_tags: List[str],
        size: int,
        offset: int,
        sort_by: str,
    ):
        self.territory_ids = territory_ids
        self.since = since
        self.until = until
        self.querystring = querystring
        self.excerpt_size = excerpt_size
        self.number_of_excerpts = number_of_excerpts
        self.pre_tags = pre_tags
        self.post_tags = post_tags
        self.size = size
        self.offset = offset
        self.sort_by = sort_by


class GazetteSearchResult:
    """
    Item to represent a gazette search result in memory inside the module
    """

    def __init__(
        self,
        territory_id,
        date,
        url,
        checksum,
        territory_name,
        state_code,
        excerpts,
        edition=None,
        is_extra_edition=None,
        txt_url=None,
    ):
        self.territory_id = territory_id
        self.date = date
        self.url = url
        self.territory_name = territory_name
        self.state_code = state_code
        self.excerpts = excerpts
        self.edition = edition
        self.is_extra_edition = is_extra_edition
        self.file_checksum = checksum
        self.txt_url = txt_url

    def __hash__(self):
        return hash(
            (
                self.territory_id,
                self.date,
                self.url,
                self.territory_name,
                self.state_code,
                str(self.excerpts),
                self.edition,
                self.is_extra_edition,
                self.file_checksum,
                self.txt_url,
            )
        )

    def __eq__(self, other):
        return (
            self.file_checksum == other.file_checksum
            and self.territory_id == other.territory_id
            and self.date == other.date
            and self.url == other.url
            and self.territory_name == other.territory_name
            and self.state_code == other.state_code
            and str(self.excerpts) == str(other.excerpts)
            and self.edition == other.edition
            and self.is_extra_edition == other.is_extra_edition
            and self.txt_url == other.txt_url
        )

    def __repr__(self):
        return f"GazetteSearchResult({self.file_checksum}, {self.territory_id}, {self.date}, {self.url}, {self.territory_name}, {self.state_code}, {self.excerpts}, {self.edition}, {self.is_extra_edition}, {self.txt_url})"


class GazetteDataGateway(abc.ABC):
    """
    Interface to access storage keeping the gazettes files
    """

    @abc.abstractmethod
    def get_gazettes(
        self,
        territory_ids: List[str],
        since: Union[date, None],
        until: Union[date, None],
        querystring: str,
        excerpt_size: int,
        number_of_excerpts: int,
        pre_tags: List[str],
        post_tags: List[str],
        size: int,
        offset: int,
        sort_by: str,
    ):
        """
        Method to get the gazette from storage
        """


class GazetteAccessInterface(abc.ABC):
    """
    Rules to interact with the gazettes
    """

    @abc.abstractmethod
    def get_gazettes(self, filters: GazetteRequest):
        """
        Method to get the gazettes
        """


class GazetteQueryBuilder(
    DateRangeQueryMixin,
    TermsQueryMixin,
    SimpleStringQueryMixin,
    SortMixin,
    MatchNoneQueryMixin,
    BoolQueryMixin,
    PaginationMixin,
    HighlightMixin,
    QueryBuilderInterface,
):
    def __init__(
        self,
        text_content_field: str,
        publication_date_field: str,
        territory_id_field: str,
    ):
        self.text_content_field = text_content_field
        self.publication_date_field = publication_date_field
        self.territory_id_field = territory_id_field

    def build_query(
        self,
        territory_ids: List[str],
        since: Union[date, None],
        until: Union[date, None],
        querystring: str,
        excerpt_size: int,
        number_of_excerpts: int,
        pre_tags: List[str],
        post_tags: List[str],
        size: int,
        offset: int,
        sort_by: str,
    ) -> Dict:
        query = {"query": {}}

        if (
            territory_ids == []
            and since is None
            and until is None
            and querystring == ""
        ):
            query["query"] = self.build_match_none_query()
            return query

        order = None
        if sort_by == "ascending_date":
            order = FieldSortOrder.ASCENDING
        elif sort_by == "descending_date" or querystring is None:
            order = FieldSortOrder.DESCENDING
        # or else sort by relevance (score)

        if order is not None:
            self.add_sorts(
                query=query,
                sorts=[
                    self.build_sort(
                        field=self.publication_date_field,
                        order=order,
                    )
                ],
            )

        self.add_pagination_fields(query=query, offset=offset, size=size)

        querystring_query = self.build_simple_query_string_query(
            querystring=querystring, fields=[self.text_content_field]
        )
        must_query = [querystring_query] if querystring_query is not None else []

        territory_query = self.build_terms_query(
            field=self.territory_id_field, terms=territory_ids
        )
        date_query = self.build_date_range_query(
            field=self.publication_date_field, since=since, until=until
        )
        filter_query = [q for q in [territory_query, date_query] if q is not None]

        query["query"] = self.build_bool_query(must=must_query, filter=filter_query)

        text_highlight = self.build_field_highlight(
            field=self.text_content_field,
            fragment_size=excerpt_size,
            number_of_fragments=number_of_excerpts,
            pre_tags=pre_tags,
            post_tags=post_tags,
        )
        self.add_highlight(
            query=query,
            fields_highlights=[text_highlight],
        )

        return query


class GazetteSearchEngineGateway(GazetteDataGateway):
    def __init__(
        self,
        search_engine: SearchEngineInterface,
        query_builder: QueryBuilderInterface,
        index: str,
    ):
        self._engine = search_engine
        self._query_builder = query_builder
        self._index = index
        if not self._engine.index_exists(index):
            raise Exception(f'Index "{index}" does not exist')

    def get_gazettes(
        self,
        territory_ids: List[str],
        since: Union[date, None],
        until: Union[date, None],
        querystring: str,
        excerpt_size: int,
        number_of_excerpts: int,
        pre_tags: List[str],
        post_tags: List[str],
        size: int,
        offset: int,
        sort_by: str,
    ):
        query = self._query_builder.build_query(
            territory_ids=territory_ids,
            since=since,
            until=until,
            querystring=querystring,
            excerpt_size=excerpt_size,
            number_of_excerpts=number_of_excerpts,
            pre_tags=pre_tags,
            post_tags=post_tags,
            size=size,
            offset=offset,
            sort_by=sort_by,
        )
        gazettes = self._engine.search(query=query, index=self._index)

        return (
            self.get_total_number_items(gazettes),
            self.create_list_with_gazette_objects(gazettes["hits"]["hits"]),
        )

    def get_total_number_items(self, search_response_json: Dict):
        return search_response_json["hits"]["total"]["value"]

    def create_list_with_gazette_objects(self, gazette_hits: List[Dict]):
        return [self._assemble_gazette_object(gazette) for gazette in gazette_hits]

    def _assemble_gazette_object(self, gazette):
        highlight = (
            gazette["highlight"].get("source_text", [])
            if "highlight" in gazette
            else []
        )
        return GazetteSearchResult(
            gazette["_source"]["territory_id"],
            datetime.strptime(gazette["_source"]["date"], "%Y-%m-%d").date(),
            gazette["_source"]["url"],
            gazette["_source"]["file_checksum"],
            gazette["_source"]["territory_name"],
            gazette["_source"]["state_code"],
            highlight,
            gazette["_source"].get("edition_number", None),
            gazette["_source"].get("is_extra_edition", None),
            gazette["_source"].get("file_raw_txt", None),
        )


class GazetteAccess(GazetteAccessInterface):
    def __init__(self, data_gateway: GazetteDataGateway):
        self._data_gateway = data_gateway

    def get_gazettes(self, filters: GazetteRequest):
        total_number_gazettes, gazettes = self._data_gateway.get_gazettes(
            **vars(filters)
        )
        return (total_number_gazettes, [vars(gazette) for gazette in gazettes])


def create_gazettes_query_builder(
    gazette_content_field: str,
    gazette_publication_date_field: str,
    gazette_territory_id_field: str,
) -> QueryBuilderInterface:
    return GazetteQueryBuilder(
        gazette_content_field,
        gazette_publication_date_field,
        gazette_territory_id_field,
    )


def create_gazettes_data_gateway(
    search_engine: SearchEngineInterface,
    query_builder: QueryBuilderInterface,
    index: str,
) -> GazetteDataGateway:
    if not isinstance(search_engine, SearchEngineInterface):
        raise Exception(
            "Search engine should implement the SearchEngineInterface interface"
        )
    if not isinstance(query_builder, QueryBuilderInterface):
        raise Exception(
            "Query builder should implement the QueryBuilderInterface interface"
        )

    return GazetteSearchEngineGateway(search_engine, query_builder, index)


def create_gazettes_interface(
    data_gateway: GazetteDataGateway,
) -> GazetteAccessInterface:
    if not isinstance(data_gateway, GazetteDataGateway):
        raise Exception(
            "Data gateway should implement the GazetteDataGateway interface"
        )

    return GazetteAccess(data_gateway)
