from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel

from gazettes import GazetteAccessInterface, GazetteRequest

app = FastAPI(
    title="Querido Diário",
    description="API to access the gazettes from all Brazilian cities",
    version="0.9.0",
)


class GazetteItem(BaseModel):
    territory_id: str
    date: date
    url: str
    territory_name: str
    state_code: str
    highlight_text: str
    edition: Optional[str]
    is_extra_edition: Optional[bool]


class GazetteSearchResponse(BaseModel):
    total_gazettes: int
    gazettes: List[GazetteItem]


def trigger_gazettes_search(
    territory_id: str = None,
    since: date = None,
    until: date = None,
    keywords: List[str] = None,
    offset: int = 0,
    size: int = 10,
    fragment_size: int = 150,
    pre_tags: List[str] = [""],
    post_tags: List[str] = [""],
):
    gazettes_count, gazettes = app.gazettes.get_gazettes(
        GazetteRequest(
            territory_id,
            since=since,
            until=until,
            keywords=keywords,
            offset=offset,
            size=size,
            fragment_size=fragment_size,
            pre_tags=pre_tags,
            post_tags=post_tags,
        )
    )
    response = {
        "total_gazettes": 0,
        "gazettes": [],
    }
    if gazettes_count > 0 and gazettes:
        response["gazettes"] = gazettes
        response["total_gazettes"] = gazettes_count
    return response


@app.get(
    "/gazettes/",
    response_model=GazetteSearchResponse,
    name="Get gazettes",
    description="Get gazettes by date and keyword",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_gazettes(
    since: Optional[date] = Query(
        None,
        title="Since date",
        description="Look for gazettes where the date is greater or equal than given date",
    ),
    until: Optional[date] = Query(
        None,
        title="Until date",
        description="Look for gazettes where the date is less or equal than given date",
    ),
    keywords: Optional[List[str]] = Query(
        None,
        title="Keywords should be present in the gazette",
        description="Look for gazettes containing the given keywords",
    ),
    offset: Optional[int] = Query(
        0, title="Offset", description="Number of item to skip in the result search",
    ),
    size: Optional[int] = Query(
        10,
        title="Number of item to return",
        description="Define the number of item should be returned",
    ),
    fragment_size: Optional[int] = Query(
        150,
        title="Number of fragments (characters) of highlight to return.",
        description="Define the fragments (characters)  of highlight of the item should be returned",
    ),
    pre_tags: List[str] = Query(
        [""],
        title="Pre tags of fragments of highlight",
        description="Pre tags of fragments of highlight. This is a list of strings (usually HTML tags) that will appear before the text which matches the query",
    ),
    post_tags: List[str] = Query(
        [""],
        title="Post tags of fragments of highlight.",
        description="Post tags of fragments of highlight. This is a list of strings (usually HTML tags) that will appear after the text which matches the query",
    ),
):
    return trigger_gazettes_search(None, since, until, keywords, offset, size, fragment_size, pre_tags, post_tags)


@app.get(
    "/gazettes/{territory_id}",
    response_model=GazetteSearchResponse,
    name="Get gazettes by territory ID",
    description="Get gazettes from specific city by date and keywords",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_gazettes_by_territory_id(
    territory_id: str = Path(..., description="City's IBGE ID"),
    since: Optional[date] = Query(
        None,
        title="Since date",
        description="Look for gazettes where the date is greater or equal than given date",
    ),
    until: Optional[date] = Query(
        None,
        title="Until date",
        description="Look for gazettes where the date is less or equal than given date",
    ),
    keywords: Optional[List[str]] = Query(
        None,
        title="Keywords should be present in the gazette",
        description="Look for gazettes containing the given keywords",
    ),
    offset: Optional[int] = Query(
        0, title="Offset", description="Number of item to skip in the result search",
    ),
    size: Optional[int] = Query(
        10,
        title="Number of item to return",
        description="Define the number of item should be returned",
    ),
    fragment_size: Optional[int] = Query(
        150,
        title="Number of fragments (characters) of highlight to return.",
        description="Define the fragments (characters)  of highlight of the item should be returned",
    ),
    pre_tags: List[str] = Query(
        [""],
        title="Pre tags of fragments of highlight",
        description="Pre tags of fragments of highlight. This is a list of strings (usually HTML tags) that will appear before the text which matches the query",
    ),
    post_tags: List[str] = Query(
        [""],
        title="Post tags of fragments of highlight.",
        description="Post tags of fragments of highlight. This is a list of strings (usually HTML tags) that will appear after the text which matches the query",
    ),
):
    return trigger_gazettes_search(territory_id, since, until, keywords, offset, size, fragment_size, pre_tags, post_tags)


def configure_api_app(gazettes: GazetteAccessInterface, api_root_path=None):
    if not isinstance(gazettes, GazetteAccessInterface):
        raise Exception("Only GazetteAccessInterface object are accepted")
    if api_root_path is not None and type(api_root_path) != str:
        raise Exception("Invalid api_root_path")
    app.gazettes = gazettes
    app.root_path = api_root_path
