from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Query
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


@app.get("/gazettes/{territory_id}", response_model=List[GazetteItem])
async def get_gazettes(
    territory_id: str,
    since: Optional[date] = Query(None, title="Since date"),
    until: Optional[date] = Query(None, title="Until date"),
    keywords: Optional[List[str]] = Query(
        None, title="Keywords should be present in the gazette"
    ),
):
    gazettes = app.gazettes.get_gazettes(
        GazetteRequest(territory_id, since=since, until=until, keywords=keywords)
    )
    if gazettes:
        return [GazetteItem(**gazette) for gazette in gazettes]
    return []


def set_gazette_interface(gazettes: GazetteAccessInterface):
    if not isinstance(gazettes, GazetteAccessInterface):
        raise Exception("Only GazetteAccessInterface object are accepted")
    app.gazettes = gazettes
