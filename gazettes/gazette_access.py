import abc
from datetime import date, datetime
from typing import Dict, List, Union

from index import SearchEngineInterface
from index.opensearch import (
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
        published_since: Union[date, None],
        published_until: Union[date, None],
        scraped_since: Union[datetime, None],
        scraped_until: Union[datetime, None],
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
        self.published_since = published_since
        self.published_until = published_until
        self.scraped_since = scraped_since
        self.scraped_until = scraped_until
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
        scraped_at,
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
        self.scraped_at = scraped_at
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
                self.scraped_at,
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
            and self.scraped_at == other.scraped_at
            and self.url == other.url
            and self.territory_name == other.territory_name
            and self.state_code == other.state_code
            and str(self.excerpts) == str(other.excerpts)
            and self.edition == other.edition
            and self.is_extra_edition == other.is_extra_edition
            and self.txt_url == other.txt_url
        )

    def __repr__(self):
        return f"GazetteSearchResult({self.file_checksum}, {self.territory_id}, {self.date}, {self.scraped_at}, {self.url}, {self.territory_name}, {self.state_code}, {self.excerpts}, {self.edition}, {self.is_extra_edition}, {self.txt_url})"


class GazetteDataGateway(abc.ABC):
    """
    Interface to access storage keeping the gazettes files
    """

    @abc.abstractmethod
    def get_gazettes(
        self,
        territory_ids: List[str],
        published_since: Union[date, None],
        published_until: Union[date, None],
        scraped_since: Union[datetime, None],
        scraped_until: Union[datetime, None],
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
        text_content_exact_field_suffix: str,
        publication_date_field: str,
        scraped_at_field: str,
        territory_id_field: str,
    ):
        self.text_content_field = text_content_field
        self.text_content_exact_field_suffix = text_content_exact_field_suffix
        self.publication_date_field = publication_date_field
        self.scraped_at_field = scraped_at_field
        self.territory_id_field = territory_id_field

    def build_query(
        self,
        territory_ids: List[str],
        published_since: Union[date, None],
        published_until: Union[date, None],
        scraped_since: Union[datetime, None],
        scraped_until: Union[datetime, None],
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
            and published_since is None
            and published_until is None
            and scraped_since is None
            and scraped_until is None
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
            querystring=querystring,
            fields=[self.text_content_field],
            exact_field_suffix=self.text_content_exact_field_suffix,
        )
        must_query = [querystring_query] if querystring_query is not None else []

        territory_query = self.build_terms_query(
            field=self.territory_id_field, terms=territory_ids
        )
        published_date_query = self.build_date_range_query(
            field=self.publication_date_field,
            since=published_since,
            until=published_until,
        )
        scraped_at_query = self.build_date_range_query(
            field=self.scraped_at_field, since=scraped_since, until=scraped_until
        )
        filter_query = [
            q
            for q in [territory_query, published_date_query, scraped_at_query]
            if q is not None
        ]

        query["query"] = self.build_bool_query(must=must_query, filter=filter_query)

        matched_fields = [self.text_content_field]
        if self.text_content_exact_field_suffix:
            matched_fields.append(
                f"{self.text_content_field}{self.text_content_exact_field_suffix}"
            )
        text_highlight = self.build_field_highlight(
            field=self.text_content_field,
            fragment_size=excerpt_size,
            number_of_fragments=number_of_excerpts,
            pre_tags=pre_tags,
            post_tags=post_tags,
            type="fvh",
            matched_fields=matched_fields,
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
        published_since: Union[date, None],
        published_until: Union[date, None],
        scraped_since: Union[datetime, None],
        scraped_until: Union[datetime, None],
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
            published_since=published_since,
            published_until=published_until,
            scraped_since=scraped_since,
            scraped_until=scraped_until,
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

    def _build_file_url(self, path_or_url: str) -> str:
        """
        Builds the complete file URL from a relative path or processes legacy URLs.

        This method supports three scenarios:
        1. New data: relative paths (e.g., "3304557/2019/file.txt")
        2. Old data: full URLs with automatic base URL replacement
        3. Legacy mode: full URLs returned as-is (backward compatibility)

        Environment variables:
        - QUERIDO_DIARIO_FILES_ENDPOINT: New base URL for files
        - REPLACE_FILE_URL_BASE: Boolean flag to enable base URL replacement (true/false)

        Examples:
        - If REPLACE_FILE_URL_BASE=true and
          QUERIDO_DIARIO_FILES_ENDPOINT="https://cdn.queridodiario.ok.org.br"
          Then "https://queridodiario.nyc3.digitaloceanspaces.com/3304557/2019/file.txt"
          becomes "https://cdn.queridodiario.ok.org.br/3304557/2019/file.txt"

        Args:
            path_or_url: Either a relative path or a full URL

        Returns:
            Complete URL to access the file
        """
        import os
        import re

        endpoint = os.environ.get("QUERIDO_DIARIO_FILES_ENDPOINT", "")
        replace_base_enabled = (
            os.environ.get("REPLACE_FILE_URL_BASE", "false").lower() == "true"
        )

        # Check if it's a URL (supports http://, https://, s3://)
        is_url = (
            path_or_url.startswith("http://")
            or path_or_url.startswith("https://")
            or path_or_url.startswith("s3://")
        )

        # Scenario 1: Relative path (new data)
        if not is_url:
            if not endpoint:
                return path_or_url  # No endpoint configured

            endpoint = endpoint.rstrip("/")
            path = path_or_url.lstrip("/")
            return f"{endpoint}/{path}"

        # Scenario 2: Full URL with base replacement enabled
        if replace_base_enabled and endpoint:
            # Extract path from URL using regex
            # Pattern: <protocol>://<domain>/<path>
            # Supports: http://, https://, s3://
            pattern = r"^(https?://|s3://)[^/]+/(.+)$"
            match = re.match(pattern, path_or_url)

            if match:
                relative_path = match.group(2)
                endpoint_clean = endpoint.rstrip("/")
                return f"{endpoint_clean}/{relative_path}"

        # Scenario 3: Legacy mode - return URL as-is
        return path_or_url

    def create_list_with_gazette_objects(self, gazette_hits: List[Dict]):
        return [self._assemble_gazette_object(gazette) for gazette in gazette_hits]

    def _assemble_gazette_object(self, gazette):
        highlight = (
            gazette["highlight"].get("source_text", [])
            if "highlight" in gazette
            else []
        )

        # Build file URL from relative path or process legacy URL
        file_url = gazette["_source"]["url"]
        url = self._build_file_url(file_url)

        file_raw_txt = gazette["_source"].get("file_raw_txt", None)
        txt_url = self._build_file_url(file_raw_txt) if file_raw_txt else None

        return GazetteSearchResult(
            gazette["_source"]["territory_id"],
            datetime.strptime(gazette["_source"]["date"], "%Y-%m-%d").date(),
            datetime.fromisoformat(gazette["_source"]["scraped_at"]),
            url,
            gazette["_source"]["file_checksum"],
            gazette["_source"]["territory_name"],
            gazette["_source"]["state_code"],
            highlight,
            gazette["_source"].get("edition_number", None),
            gazette["_source"].get("is_extra_edition", None),
            txt_url,
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
    gazette_content_exact_field_suffix: str,
    gazette_publication_date_field: str,
    gazette_scraped_at_field: str,
    gazette_territory_id_field: str,
) -> QueryBuilderInterface:
    return GazetteQueryBuilder(
        gazette_content_field,
        gazette_content_exact_field_suffix,
        gazette_publication_date_field,
        gazette_scraped_at_field,
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
