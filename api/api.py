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


def trigger_gazettes_search(
    territory_id: str = None,
    since: date = None,
    until: date = None,
    keywords: List[str] = None,
    page: int = 1,
    page_size: int = 10,
):
    if page > 0:
        page -= 1
    gazettes = app.gazettes.get_gazettes(
        GazetteRequest(
            territory_id,
            since=since,
            until=until,
            keywords=keywords,
            page=page,
            page_size=page_size,
        )
    )
    if gazettes:
        return [GazetteItem(**gazette) for gazette in gazettes]
    return []


@app.get(
    "/gazettes/",
    response_model=List[GazetteItem],
    name="Get gazettes",
    description="Get gazettes by date and keyword",
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
    page: Optional[int] = Query(
        1, title="Page", description="Define which page should be return.",
    ),
    page_size: Optional[int] = Query(
        10,
        title="Page size",
        description="Define the number of item on the page returned.",
    ),
):
    return trigger_gazettes_search(None, since, until, keywords, page, page_size)


@app.get(
    "/gazettes/{territory_id}",
    response_model=List[GazetteItem],
    name="Get gazettes by territory ID",
    description="Get gazettes from specific city by date and keywords",
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
    page: Optional[int] = Query(
        1, title="Page", description="Define which page should be return.",
    ),
    page_size: Optional[int] = Query(
        10,
        title="Page size",
        description="Define the number of item on the page returned.",
    ),
):
    return trigger_gazettes_search(
        territory_id, since, until, keywords, page, page_size
    )


def set_gazette_interface(gazettes: GazetteAccessInterface):
    if not isinstance(gazettes, GazetteAccessInterface):
        raise Exception("Only GazetteAccessInterface object are accepted")
    app.gazettes = gazettes
