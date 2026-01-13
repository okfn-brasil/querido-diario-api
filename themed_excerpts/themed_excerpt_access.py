import abc
import json
import os
from datetime import date, datetime
from typing import Dict, List, Tuple, Union

from index import SearchEngineInterface
from index.opensearch import (
    QueryBuilderInterface,
    DateRangeQueryMixin,
    SimpleStringQueryMixin,
    SortMixin,
    TermsQueryMixin,
    BoolQueryMixin,
    MatchAllQueryMixin,
    FieldSortOrder,
    PaginationMixin,
    HighlightMixin,
    RankFeatureQueryMixin,
)


class ThemedExcerptRequest:
    """
    Object containing the data to filter themed excerpts
    """

    def __init__(
        self,
        theme: str,
        entities: List[str],
        subthemes: List[str],
        territory_ids: List[str],
        published_since: Union[date, None],
        published_until: Union[date, None],
        scraped_since: Union[datetime, None],
        scraped_until: Union[datetime, None],
        querystring: str,
        pre_tags: List[str],
        post_tags: List[str],
        size: int,
        offset: int,
        sort_by: str,
    ):
        self.theme = theme
        self.entities = entities
        self.subthemes = subthemes
        self.territory_ids = territory_ids
        self.published_since = published_since
        self.published_until = published_until
        self.scraped_since = scraped_since
        self.scraped_until = scraped_until
        self.querystring = querystring
        self.offset = offset
        self.size = size
        self.pre_tags = pre_tags
        self.post_tags = post_tags
        self.sort_by = sort_by


class ThemedExcerptSearchResult:
    """
    Item to represent a themed excerpt in memory inside the module
    """

    def __init__(
        self,
        excerpt_id,
        territory_id,
        date,
        scraped_at,
        url,
        territory_name,
        state_code,
        subthemes,
        excerpt,
        theme,
        edition=None,
        is_extra_edition=None,
        txt_url=None,
        entities=[],
    ):
        self.excerpt_id = excerpt_id
        self.territory_id = territory_id
        self.date = date
        self.scraped_at = scraped_at
        self.url = url
        self.territory_name = territory_name
        self.state_code = state_code
        self.subthemes = subthemes
        self.excerpt = excerpt
        self.theme = theme
        self.edition = edition
        self.is_extra_edition = is_extra_edition
        self.txt_url = txt_url
        self.entities = entities

    def __hash__(self):
        return hash(
            (
                self.excerpt_id,
                self.territory_id,
                self.date,
                self.scraped_at,
                self.url,
                self.territory_name,
                self.state_code,
                str(self.subthemes),
                self.excerpt,
                self.theme,
                self.edition,
                self.is_extra_edition,
                self.txt_url,
                str(self.entities),
            )
        )

    def __eq__(self, other):
        return (
            self.excerpt_id == other.excerpt_id
            and self.territory_id == other.territory_id
            and self.date == other.date
            and self.scraped_at == other.scraped_at
            and self.url == other.url
            and self.territory_name == other.territory_name
            and self.state_code == other.state_code
            and set(self.subthemes) == set(other.subthemes)
            and self.excerpt == other.excerpt
            and self.theme == other.theme
            and self.edition == other.edition
            and self.is_extra_edition == other.is_extra_edition
            and self.txt_url == other.txt_url
            and set(self.entities) == set(other.entities)
        )

    def __repr__(self):
        return f"ThemedExcerptSearchResult({self.excerpt_id}, {self.territory_id}, {self.date}, {self.scraped_at}, {self.url}, {self.territory_name}, {self.state_code}, {self.subthemes}, {self.excerpt}, {self.theme}, {self.edition}, {self.is_extra_edition}, {self.txt_url}, {self.entities})"


class ThemedExcerptDataGateway(abc.ABC):
    """
    Interface to access storage keeping the themed excerpts
    """

    @abc.abstractmethod
    def get_themed_excerpts(
        self,
        theme_index: str,
        theme: str,
        entities: List[str],
        subthemes: List[str],
        territory_ids: List[str],
        published_since: Union[date, None],
        published_until: Union[date, None],
        scraped_since: Union[datetime, None],
        scraped_until: Union[datetime, None],
        querystring: str,
        pre_tags: List[str],
        post_tags: List[str],
        size: int,
        offset: int,
        sort_by: str,
    ):
        """
        Method to get the themed excerpt from storage
        """


class ThemesDatabaseGateway(abc.ABC):
    """
    Interface to access database keeping theme infos
    """

    @abc.abstractmethod
    def get_available_themes(self):
        """
        Method to get the available themes from the database
        """

    @abc.abstractmethod
    def get_theme_index(self, theme: str):
        """
        Method to get the index corresponding to the theme from the database
        """

    @abc.abstractmethod
    def get_available_subthemes(self, theme: str):
        """
        Method to get the available subthemes from the database
        """

    @abc.abstractmethod
    def get_available_entities(self, theme: str):
        """
        Method to get the available entities from the database
        """


class ThemedExcerptAccessInterface(abc.ABC):
    """
    Rules to interact with the themed excerpts
    """

    @abc.abstractmethod
    def get_themed_excerpts(self, filters: ThemedExcerptRequest):
        """
        Method to get the themed excerpts
        """

    @abc.abstractmethod
    def get_available_themes(self):
        """
        Method to get the available themes
        """

    @abc.abstractmethod
    def get_available_subthemes(self, theme: str):
        """
        Method to get the available subthemes
        """

    @abc.abstractmethod
    def get_available_entities(self, theme: str):
        """
        Method to get the available entities
        """


class ThemedExcerptQueryBuilder(
    DateRangeQueryMixin,
    TermsQueryMixin,
    SimpleStringQueryMixin,
    SortMixin,
    MatchAllQueryMixin,
    BoolQueryMixin,
    PaginationMixin,
    HighlightMixin,
    RankFeatureQueryMixin,
    QueryBuilderInterface,
):
    def __init__(
        self,
        text_content_field: str,
        text_content_exact_field_suffix: str,
        publication_date_field: str,
        scraped_at_field: str,
        territory_id_field: str,
        entities_field: str,
        subthemes_field: str,
        embedding_score_field: str,
        tfidf_score_field: str,
        fragment_size: int,
        number_of_fragments: int,
    ):
        self.text_content_field = text_content_field
        self.text_content_exact_field_suffix = text_content_exact_field_suffix
        self.publication_date_field = publication_date_field
        self.scraped_at_field = scraped_at_field
        self.territory_id_field = territory_id_field
        self.entities_field = entities_field
        self.subthemes_field = subthemes_field
        self.embedding_score_field = embedding_score_field
        self.tfidf_score_field = tfidf_score_field
        self.fragment_size = fragment_size
        self.number_of_fragments = number_of_fragments

    def build_query(
        self,
        entities: List[str],
        subthemes: List[str],
        territory_ids: List[str],
        published_since: Union[date, None],
        published_until: Union[date, None],
        scraped_since: Union[datetime, None],
        scraped_until: Union[datetime, None],
        querystring: str,
        pre_tags: List[str],
        post_tags: List[str],
        size: int,
        offset: int,
        sort_by: str,
    ) -> Dict:
        query = {"query": {}}

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

        if (
            territory_ids == []
            and entities == []
            and subthemes == []
            and published_since is None
            and published_until is None
            and scraped_since is None
            and scraped_until is None
            and querystring == ""
        ):
            query["query"] = self.build_match_all_query()
            return query

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
        entities_query = self.build_terms_query(
            field=self.entities_field, terms=entities
        )
        subthemes_query = self.build_terms_query(
            field=self.subthemes_field, terms=subthemes
        )
        filter_query = [
            q
            for q in [
                territory_query,
                published_date_query,
                scraped_at_query,
                entities_query,
                subthemes_query,
            ]
            if q is not None
        ]

        tfidf_score_query = self.build_rank_feature_query(self.tfidf_score_field)
        embedding_score_query = self.build_rank_feature_query(
            self.embedding_score_field
        )
        should_query = [tfidf_score_query, embedding_score_query]

        query["query"] = self.build_bool_query(
            must=must_query, should=should_query, filter=filter_query
        )

        matched_fields = [self.text_content_field]
        if self.text_content_exact_field_suffix:
            matched_fields.append(
                f"{self.text_content_field}{self.text_content_exact_field_suffix}"
            )
        text_highlight = self.build_field_highlight(
            field=self.text_content_field,
            fragment_size=self.fragment_size,
            number_of_fragments=self.number_of_fragments,
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


class ThemedExcerptSearchEngineGateway(ThemedExcerptDataGateway):
    def __init__(
        self,
        search_engine: SearchEngineInterface,
        query_builder: QueryBuilderInterface,
    ):
        self._engine = search_engine
        self._query_builder = query_builder

    def get_themed_excerpts(
        self,
        theme_index: str,
        theme: str,
        entities: List[str],
        subthemes: List[str],
        territory_ids: List[str],
        published_since: Union[date, None],
        published_until: Union[date, None],
        scraped_since: Union[datetime, None],
        scraped_until: Union[datetime, None],
        querystring: str,
        pre_tags: List[str],
        post_tags: List[str],
        size: int,
        offset: int,
        sort_by: str,
    ):
        query = self._query_builder.build_query(
            entities=entities,
            subthemes=subthemes,
            territory_ids=territory_ids,
            published_since=published_since,
            published_until=published_until,
            scraped_since=scraped_since,
            scraped_until=scraped_until,
            querystring=querystring,
            pre_tags=pre_tags,
            post_tags=post_tags,
            size=size,
            offset=offset,
            sort_by=sort_by,
        )
        excerpts = self._engine.search(query=query, index=theme_index)

        return (
            self.get_total_number_items(excerpts),
            self.create_list_with_themed_excerpt_objects(
                excerpts["hits"]["hits"], theme
            ),
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

    def create_list_with_themed_excerpt_objects(
        self, themed_excerpt_hits: List[Dict], theme: str
    ):
        return [
            self._assemble_themed_excerpt_object(excerpt, theme)
            for excerpt in themed_excerpt_hits
        ]

    def _assemble_themed_excerpt_object(self, excerpt: Dict, theme: str):
        highlight = (
            excerpt["highlight"]["excerpt"][0]
            if "highlight" in excerpt
            else excerpt["_source"]["excerpt"]
        )

        # Build file URL from relative path or process legacy URL
        file_url = excerpt["_source"]["source_url"]
        url = self._build_file_url(file_url)

        file_raw_txt = excerpt["_source"].get("source_file_raw_txt", None)
        txt_url = self._build_file_url(file_raw_txt) if file_raw_txt else None

        return ThemedExcerptSearchResult(
            excerpt["_source"]["excerpt_id"],
            excerpt["_source"]["source_territory_id"],
            datetime.strptime(excerpt["_source"]["source_date"], "%Y-%m-%d").date(),
            datetime.fromisoformat(excerpt["_source"]["source_scraped_at"]),
            url,
            excerpt["_source"]["source_territory_name"],
            excerpt["_source"]["source_state_code"],
            excerpt["_source"]["excerpt_subthemes"],
            highlight,
            theme,
            excerpt["_source"].get("source_edition_number", None),
            excerpt["_source"].get("source_is_extra_edition", None),
            txt_url,
            excerpt["_source"].get("excerpt_entities", []),
        )


class ThemesJSONDatabaseGateway(ThemesDatabaseGateway):
    """
    A gateway to interact with the themes configuration JSON that is also
    used in the data-processing project.
    """

    def __init__(self, database_file: str):
        self._database_file = database_file
        if not os.path.exists(self._database_file):
            raise Exception("Missing databasefile")

    def get_available_themes(self):
        themes = []
        with open(self._database_file) as database:
            themes_json = json.load(database)
            for theme_config in themes_json["themes"]:
                themes.append(theme_config["name"])
        return themes

    def get_theme_index(self, theme: str):
        index = None
        with open(self._database_file) as database:
            themes_json = json.load(database)
            for theme_config in themes_json["themes"]:
                if theme_config["name"] == theme:
                    index = theme_config["index"]
                    break
        return index

    def get_available_subthemes(self, theme: str):
        subthemes = None
        with open(self._database_file) as database:
            themes_json = json.load(database)
            for theme_config in themes_json["themes"]:
                if theme_config["name"] == theme:
                    queries = theme_config["queries"]
                    subthemes = [q["title"] for q in queries]
                    break
        return subthemes

    def get_available_entities(self, theme: str):
        cases = None
        categories = None
        with open(self._database_file) as database:
            themes_json = json.load(database)
            for theme_config in themes_json["themes"]:
                if theme_config["name"] == theme:
                    cases = theme_config["entities"]["cases"]
                    categories = theme_config["entities"]["categories"]
                    break

        if cases is None or categories is None:
            return None

        entities = []
        for category in categories:
            entity_category = {
                "entity_type": category["name"],
                "entity_type_description": category["description"],
                "entities": [],
            }
            for case in cases:
                if case["category"] != category["name"]:
                    continue
                entity_category["entities"].append(case["title"])
            entities.append(entity_category)

        return entities


class ThemedExcerptAccess(ThemedExcerptAccessInterface):
    def __init__(
        self,
        data_gateway: ThemedExcerptDataGateway,
        theme_database_gateway: ThemesDatabaseGateway,
    ):
        self._data_gateway = data_gateway
        self._theme_database_gateway = theme_database_gateway

    def get_themed_excerpts(self, filters: ThemedExcerptRequest):
        theme_index = self._theme_database_gateway.get_theme_index(filters.theme)
        if theme_index is None:
            raise Exception(f"Theme not found.")

        total_number_excerpts, excerpts = self._data_gateway.get_themed_excerpts(
            theme_index=theme_index,
            **vars(filters),
        )
        return (total_number_excerpts, [vars(excerpt) for excerpt in excerpts])

    def get_available_themes(self):
        themes = self._theme_database_gateway.get_available_themes()
        return themes

    def get_available_subthemes(self, theme: str):
        subthemes = self._theme_database_gateway.get_available_subthemes(theme)
        return subthemes

    def get_available_entities(self, theme: str):
        entities = self._theme_database_gateway.get_available_entities(theme)
        return entities


def create_themed_excerpts_query_builder(
    themed_excerpt_text_content_field: str,
    themed_excerpt_content_exact_field_suffix: str,
    themed_excerpt_publication_date_field: str,
    themed_excerpt_scraped_at_field: str,
    themed_excerpt_territory_id_field: str,
    themed_excerpt_entities_field: str,
    themed_excerpt_subthemes_field: str,
    themed_excerpt_embedding_score_field: str,
    themed_excerpt_tfidf_score_field: str,
    themed_excerpt_fragment_size: int,
    themed_excerpt_number_of_fragments: int,
) -> QueryBuilderInterface:
    return ThemedExcerptQueryBuilder(
        themed_excerpt_text_content_field,
        themed_excerpt_content_exact_field_suffix,
        themed_excerpt_publication_date_field,
        themed_excerpt_scraped_at_field,
        themed_excerpt_territory_id_field,
        themed_excerpt_entities_field,
        themed_excerpt_subthemes_field,
        themed_excerpt_embedding_score_field,
        themed_excerpt_tfidf_score_field,
        themed_excerpt_fragment_size,
        themed_excerpt_number_of_fragments,
    )


def create_themed_excerpts_data_gateway(
    search_engine: SearchEngineInterface,
    query_builder: QueryBuilderInterface,
) -> ThemedExcerptDataGateway:
    if not isinstance(search_engine, SearchEngineInterface):
        raise Exception(
            "Search engine should implement the SearchEngineInterface interface"
        )
    if not isinstance(query_builder, QueryBuilderInterface):
        raise Exception(
            "Query builder should implement the QueryBuilderInterface interface"
        )

    return ThemedExcerptSearchEngineGateway(search_engine, query_builder)


def create_themes_database_gateway(themes_database_file: str) -> ThemesDatabaseGateway:
    return ThemesJSONDatabaseGateway(themes_database_file)


def create_themed_excerpts_interface(
    data_gateway: ThemedExcerptDataGateway,
    themes_database_gateway: ThemesDatabaseGateway,
) -> ThemedExcerptAccessInterface:
    if not isinstance(data_gateway, ThemedExcerptDataGateway):
        raise Exception(
            "Data gateway should implement the ThemedExcerptDataGateway interface"
        )
    if not isinstance(themes_database_gateway, ThemesDatabaseGateway):
        raise Exception(
            "Database gateway should implement the ThemesDatabaseGateway interface"
        )

    return ThemedExcerptAccess(data_gateway, themes_database_gateway)
