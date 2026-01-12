import abc
import os
import re
from datetime import date
from enum import Enum, unique
from typing import Dict, List, Tuple, Union

import opensearchpy


class SearchEngineInterface(abc.ABC):
    """
    Interface to abstract the interaction with the index system
    """

    @abc.abstractmethod
    def search(self, query: Dict, index: str = "", timeout: int = 30) -> Dict:
        """
        Searches the index with the provided opensearch_dsl.Search
        """

    @abc.abstractmethod
    def index_exists(self, index: str) -> bool:
        """
        Checks if a specific index exists
        """


class OpenSearch(SearchEngineInterface):
    def __init__(
        self,
        host: str,
        credentials: Tuple[str, str] = ("user", "pswd"),
        default_index: str = "",
    ):
        self._search_engine = opensearchpy.OpenSearch(
            hosts=[host], http_auth=credentials
        )
        self._default_index = default_index

    def search(self, query: Dict, index: str = "", timeout: int = 30) -> Dict:
        index_name = self._get_index_name(index)
        response = self._search_engine.search(
            index=index_name, body=query, request_timeout=timeout
        )
        return response

    def index_exists(self, index: str) -> bool:
        return self._search_engine.indices.exists(index=index)

    def _get_index_name(self, index: str) -> str:
        index_name = index if self._is_valid_index_name(index) else self._default_index
        if not self.index_exists(index_name):
            raise Exception(f'Index "{index_name}" does not exist')
        return index_name

    def _is_valid_index_name(self, index: str) -> bool:
        return isinstance(index, str) and len(index) > 0


class QueryBuilderInterface(abc.ABC):
    @abc.abstractmethod
    def build_query(self, **kwargs) -> Dict:
        """
        Method to build queries using functionalities provided by the adequate mixins
        """


class BoolQueryMixin:
    def build_bool_query(
        self,
        must: List[Dict] = [],
        should: List[Dict] = [],
        filter: List[Dict] = [],
        must_not: List[Dict] = [],
    ) -> Union[Dict, None]:
        if must == should == filter == must_not == []:
            return

        return {
            "bool": {
                "must": must,
                "should": should,
                "filter": filter,
                "must_not": must_not,
            }
        }


class MatchNoneQueryMixin:
    def build_match_none_query(self) -> Dict:
        return {"match_none": {}}


class MatchAllQueryMixin:
    def build_match_all_query(self) -> Dict:
        return {"match_all": {}}


class DateRangeQueryMixin:
    def build_date_range_query(
        self,
        field: str,
        since: Union[date, None] = None,
        until: Union[date, None] = None,
    ) -> Union[Dict, None]:
        if since is None and until is None:
            return

        date_range_query = {field: {}}
        if since is not None:
            date_range_query[field]["gte"] = since.isoformat()
        if until is not None:
            date_range_query[field]["lte"] = until.isoformat()

        return {"range": date_range_query}


class TermsQueryMixin:
    def build_terms_query(self, field: str, terms: List[str] = []) -> Union[Dict, None]:
        if terms != []:
            return {"terms": {field: terms}}


class SimpleStringQueryMixin:
    def build_simple_query_string_query(
        self, querystring: str, fields: List[str] = [], exact_field_suffix: str = ""
    ) -> Union[Dict, None]:
        if querystring == "":
            return

        clean_querystring = self._preprocess_querystring(querystring)
        return {
            "simple_query_string": {
                "query": clean_querystring,
                "fields": fields,
                "quote_field_suffix": exact_field_suffix,
            }
        }

    def _preprocess_querystring(self, querystring: str) -> str:
        return self._translate_curly_text_to_straight(querystring)

    def _translate_curly_text_to_straight(self, text: str) -> str:
        translated_double = re.sub(r"[“”]", r'"', text)
        translated_single = re.sub(r"[‘’]", r"'", translated_double)
        return translated_single


class RankFeatureQueryMixin:
    def build_rank_feature_query(self, field: str):
        return {"rank_feature": {"field": field}}


@unique
class FieldSortOrder(str, Enum):
    DESCENDING = "desc"
    ASCENDING = "asc"


class SortMixin:
    def add_sorts(self, query: Dict, sorts: List[Dict] = []) -> None:
        if sorts != []:
            query["sort"] = sorts

    def build_sort(self, field: str, order: FieldSortOrder) -> Dict:
        return {field: {"order": order.value}}


class PaginationMixin:
    def add_pagination_fields(
        self,
        query: Dict,
        offset: Union[int, None] = None,
        size: Union[int, None] = None,
    ) -> None:
        if offset is not None:
            query["from"] = offset

        if size is not None:
            query["size"] = size


class HighlightMixin:
    def add_highlight(self, query: Dict, fields_highlights: List[Dict] = [],) -> None:
        if fields_highlights == []:
            return

        highlight = {"highlight": {"fields": {}}}
        for field_highlight in fields_highlights:
            highlight["highlight"]["fields"].update(field_highlight)

        query.update(highlight)

    def build_field_highlight(
        self,
        field: str,
        fragment_size: Union[int, None] = None,
        number_of_fragments: Union[int, None] = None,
        pre_tags: List[str] = [],
        post_tags: List[str] = [],
        type: str = "unified",
        matched_fields: List[str] = [],
    ) -> Dict:
        field_highlight = {
            "pre_tags": pre_tags,
            "post_tags": post_tags,
            "type": type,
        }

        if fragment_size is not None:
            field_highlight["fragment_size"] = fragment_size

        if number_of_fragments is not None:
            field_highlight["number_of_fragments"] = number_of_fragments

        if type == "fvh" and matched_fields:
            field_highlight["matched_fields"] = matched_fields

        return {field: field_highlight}


def create_search_engine_interface(
    host: str = "",
    credentials: Tuple[str, str] = ("user", "pswd"),
    default_index: str = "",
) -> SearchEngineInterface:
    if not isinstance(host, str) or len(host.strip()) == 0:
        raise Exception("Missing host")
    if not isinstance(default_index, str):
        raise Exception("Invalid index name")
    return OpenSearch(
        host.strip(), credentials=credentials, default_index=default_index.strip()
    )
