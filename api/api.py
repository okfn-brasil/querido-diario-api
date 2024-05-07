import logging
from enum import Enum, unique
from datetime import date, datetime
from typing import List, Optional

from fastapi import FastAPI, Query, Path, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from gazettes import GazetteAccessInterface, GazetteRequest
from cities import CityAccessInterface
from suggestions import Suggestion, SuggestionServiceInterface
from companies import InvalidCNPJException, CompaniesAccessInterface
from config.config import load_configuration
from themed_excerpts import ThemedExcerptAccessInterface, ThemedExcerptAccessInterface
from themed_excerpts.themed_excerpt_access import ThemedExcerptRequest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config = load_configuration()

app = FastAPI(
    title="Querido Diário",
    description="API to access the gazettes from all Brazilian cities",
    version="0.17.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allow_origins,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=config.cors_allow_methods,
    allow_headers=config.cors_allow_headers,
)


class GazetteItem(BaseModel):
    territory_id: str
    date: date
    scraped_at: datetime
    url: str
    territory_name: str
    state_code: str
    excerpts: List[str]
    edition: Optional[str]
    is_extra_edition: Optional[bool]
    txt_url: Optional[str]


class GazetteSearchResponse(BaseModel):
    total_gazettes: int
    gazettes: List[GazetteItem]


class ThemedExcerptItem(BaseModel):
    territory_id: str
    date: date
    scraped_at: datetime
    url: str
    territory_name: str
    state_code: str
    excerpt: str
    subthemes: List[str]
    entities: Optional[List[str]]
    edition: Optional[str]
    is_extra_edition: Optional[bool]
    txt_url: Optional[str]


class ThemedExcerptSearchResponse(BaseModel):
    total_excerpts: int
    excerpts: List[ThemedExcerptItem]


class ThemesSearchResponse(BaseModel):
    themes: List[str]


class SubthemesSearchResponse(BaseModel):
    subthemes: List[str]


class Entity(BaseModel):
    entity_type: str
    entity_type_description: str
    entities: List[str]


class EntitiesSearchResponse(BaseModel):
    entities: List[Entity]


@unique
class CityLevel(str, Enum):
    ALL = ""
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"


class City(BaseModel):
    territory_id: str
    territory_name: str
    state_code: str
    publication_urls: Optional[List[str]]
    level: CityLevel


class CitiesSearchResponse(BaseModel):
    cities: List[City]


class CitySearchResponse(BaseModel):
    city: City


@unique
class SortBy(str, Enum):
    RELEVANCE = "relevance"
    DESCENDING_DATE = "descending_date"
    ASCENDING_DATE = "ascending_date"


class HTTPExceptionMessage(BaseModel):
    detail: str


class CreateSuggestionBody(BaseModel):
    email_address: str = Field(
        title="Email address", description="Email address who is sending email"
    )
    name: str = Field(
        title="Name", description="Name who is sending email",
    )
    content: str = Field(
        title="Email content", description="Email content with suggestion",
    )


class CreatedSuggestionResponse(BaseModel):
    status: str


class Company(BaseModel):
    cnpj_basico: str
    cnpj_ordem: str
    cnpj_dv: str
    cnpj_completo: str
    cnpj_completo_apenas_numeros: str
    identificador_matriz_filial: Optional[str]
    nome_fantasia: Optional[str]
    situacao_cadastral: Optional[str]
    data_situacao_cadastral: Optional[str]
    motivo_situacao_cadastral: Optional[str]
    nome_cidade_exterior: Optional[str]
    data_inicio_atividade: Optional[str]
    cnae_fiscal_secundario: Optional[str]
    tipo_logradouro: Optional[str]
    logradouro: Optional[str]
    numero: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    cep: Optional[str]
    uf: Optional[str]
    ddd_telefone_1: Optional[str]
    ddd_telefone_2: Optional[str]
    ddd_telefone_fax: Optional[str]
    correio_eletronico: Optional[str]
    situacao_especial: Optional[str]
    data_situacao_especial: Optional[str]
    pais: Optional[str]
    municipio: Optional[str]
    razao_social: Optional[str]
    natureza_juridica: Optional[str]
    qualificacao_do_responsavel: Optional[str]
    capital_social: Optional[str]
    porte: Optional[str]
    ente_federativo_responsavel: Optional[str]
    opcao_pelo_simples: Optional[str]
    data_opcao_pelo_simples: Optional[str]
    data_exclusao_pelo_simples: Optional[str]
    opcao_pelo_mei: Optional[str]
    data_opcao_pelo_mei: Optional[str]
    data_exclusao_pelo_mei: Optional[str]
    cnae: Optional[str]


class CompanySearchResponse(BaseModel):
    cnpj_info: Company


class Partner(BaseModel):
    cnpj_basico: str
    cnpj_ordem: str
    cnpj_dv: str
    cnpj_completo: str
    cnpj_completo_apenas_numeros: str
    identificador_socio: Optional[str]
    razao_social: Optional[str]
    cnpj_cpf_socio: Optional[str]
    qualificacao_socio: Optional[str]
    data_entrada_sociedade: Optional[str]
    pais_socio_estrangeiro: Optional[str]
    numero_cpf_representante_legal: Optional[str]
    nome_representante_legal: Optional[str]
    qualificacao_representante_legal: Optional[str]
    faixa_etaria: Optional[str]


class PartnersSearchResponse(BaseModel):
    total_partners: int
    partners: List[Partner]


@app.get(
    "/gazettes",
    response_model=GazetteSearchResponse,
    name="Search for content in gazettes",
    description="Search for content in published gazettes from available cities. Each search result is an individual gazette.",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_gazettes(
    territory_ids: List[str] = Query(
        [],
        description="Search in gazettes published by cities with the given 7-digit IBGE IDs (an empty field searches in all available cities).",
    ),
    published_since: date = Query(
        None,
        description="Search in gazettes published on given date or after (format: YYYY-MM-DD).",
    ),
    published_until: date = Query(
        None,
        description="Search in gazettes published on given date or before (format: YYYY-MM-DD).",
    ),
    scraped_since: datetime = Query(
        None,
        description="Search in gazettes scraped on given datetime or after (format: YYYY-MM-DDTHH:MM:SS).",
    ),
    scraped_until: datetime = Query(
        None,
        description="Search in gazettes scraped on given datetime or before (format: YYYY-MM-DDTHH:MM:SS).",
    ),
    querystring: str = Query(
        "",
        description='Search in gazettes using OpenSearch\'s "simple query string syntax" (an empty field returns no excerpts, only the results metadata).',
    ),
    excerpt_size: int = Query(
        500,
        description="Maximum number of characters that an excerpt should display (use with caution).",
    ),
    number_of_excerpts: int = Query(
        1,
        description="Maximum number of excerpts of a gazette to be returned (use with caution).",
    ),
    pre_tags: List[str] = Query(
        [""],
        description="List of strings (usually HTML tags) to be inserted before the text which matches the query in the excerpts.",
    ),
    post_tags: List[str] = Query(
        [""],
        description="List of strings (usually HTML tags) to be inserted after the text which matches the query in the excerpts.",
    ),
    size: int = Query(
        10,
        description="Maximum number of results to be returned in the response (use with caution).",
    ),
    offset: int = Query(
        default=0,
        description="Number of search results to be skipped in the response.",
    ),
    sort_by: SortBy = Query(
        SortBy.RELEVANCE, description="How to sort the search results.",
    ),
):
    gazette_request = GazetteRequest(
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
        sort_by=sort_by.value,
    )
    gazettes_count, gazettes = app.gazettes.get_gazettes(gazette_request)
    logger.info("DALE")
    logger.warning("CUIDADO")
    logger.error("EITA")
    return {
        "total_gazettes": gazettes_count,
        "gazettes": gazettes,
    }


@app.get(
    "/gazettes/by_theme/{theme}",
    response_model=ThemedExcerptSearchResponse,
    name="Search for content in gazette excerpts associated with a theme",
    description="Search for content in excerpts from available cities that are related to an available theme. Each search result is an excerpt from a gazette.",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    responses={
        404: {"model": HTTPExceptionMessage, "description": "Theme not found."},
    },
)
async def get_themed_excerpts(
    theme: str = Path(
        ...,
        description="Search in excerpts from gazettes that are associated to the given theme.",
    ),
    entities: List[str] = Query(
        [],
        description="Search in excerpts which contains any of the given entities (entities are theme-specific).",
    ),
    subthemes: List[str] = Query(
        [],
        description="Search in excerpts which contains any of the given subthemes (subthemes are theme-specific).",
    ),
    territory_ids: List[str] = Query(
        [],
        description="Search in excerpts from gazettes published by cities with the given 7-digit IBGE IDs (an empty field searches in all available cities).",
    ),
    published_since: date = Query(
        None,
        description="Search in excerpts from gazettes published on given date or after (format: YYYY-MM-DD).",
    ),
    published_until: date = Query(
        None,
        description="Search in excerpts from gazettes published on given date or before (format: YYYY-MM-DD).",
    ),
    scraped_since: datetime = Query(
        None,
        description="Search in excerpts from gazettes scraped on given datetime or after (format: YYYY-MM-DDTHH:MM:SS).",
    ),
    scraped_until: datetime = Query(
        None,
        description="Search in excerpts from gazettes scraped on given datetime or before (format: YYYY-MM-DDTHH:MM:SS).",
    ),
    querystring: str = Query(
        "",
        description='Search in excerpts using OpenSearch\'s "simple query string syntax".',
    ),
    pre_tags: List[str] = Query(
        [""],
        description="List of strings (usually HTML tags) to be inserted before the text which matches the query in the excerpts.",
    ),
    post_tags: List[str] = Query(
        [""],
        description="List of strings (usually HTML tags) to be inserted after the text which matches the query in the excerpts.",
    ),
    size: int = Query(
        10,
        description="Maximum number of results to be returned in the response (use with caution).",
    ),
    offset: int = Query(
        default=0,
        description="Number of search results to be skipped in the response.",
    ),
    sort_by: SortBy = Query(
        SortBy.RELEVANCE, description="How to sort the search results.",
    ),
):
    themed_excerpt_request = ThemedExcerptRequest(
        theme=theme,
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
        sort_by=sort_by.value,
    )
    try:
        excerpts_count, excerpts = app.themed_excerpts.get_themed_excerpts(
            themed_excerpt_request
        )
    except Exception as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    return {
        "total_excerpts": excerpts_count,
        "excerpts": excerpts,
    }


@app.get(
    "/gazettes/by_theme/themes/",
    response_model=ThemesSearchResponse,
    name="Get all available themes",
    description="Get all available themes that can be used to search in gazettes by theme.",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_available_themes():
    themes = app.themed_excerpts.get_available_themes()
    return {"themes": themes}


@app.get(
    "/gazettes/by_theme/subthemes/{theme}",
    response_model=SubthemesSearchResponse,
    name="Get all available subthemes of a theme",
    description="Get all available subthemes of a theme that can be used to search in gazettes by theme and further filtering by subthemes.",
    responses={
        404: {"model": HTTPExceptionMessage, "description": "Theme not found."},
    },
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_available_subthemes(
    theme: str = Path(
        ..., description="Theme that can be used to search in gazettes by theme.",
    ),
):
    subthemes = app.themed_excerpts.get_available_subthemes(theme)
    if subthemes is None:
        return JSONResponse(status_code=404, content={"detail": "Theme not found."})
    return {"subthemes": subthemes}


@app.get(
    "/gazettes/by_theme/entities/{theme}",
    response_model=EntitiesSearchResponse,
    name="Get all available entities of a theme",
    description="Get all available entities of a theme that can be used to search in gazettes by theme and further filtering by entities.",
    responses={
        404: {"model": HTTPExceptionMessage, "description": "Theme not found."},
    },
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_available_entities(
    theme: str = Path(
        ..., description="Theme that can be used to search in gazettes by theme.",
    ),
):
    entities = app.themed_excerpts.get_available_entities(theme)
    if entities is None:
        return JSONResponse(status_code=404, content={"detail": "Theme not found."})
    return {"entities": entities}


@app.get(
    "/cities",
    response_model=CitiesSearchResponse,
    name="Search for cities by name.",
    description="Search for cities with a name similar to the city_name query.",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_cities(
    city_name: Optional[str] = Query(
        "",
        description="Search for cities with a similar name (empty field returns all cities).",
    ),
    levels: Optional[List[CityLevel]] = Query(
        [CityLevel.ALL],
        description="Search for cities within the same openness level (empty field returns from all levels)",
    ),
):
    cities = app.cities.get_cities(city_name, levels)
    return {"cities": cities}


@app.get(
    "/cities/{territory_id}",
    response_model=CitySearchResponse,
    name="Get city by IBGE ID",
    description="Get general info from specific city with 7-digit IBGE ID.",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    responses={404: {"model": HTTPExceptionMessage, "description": "City not found"}},
)
async def get_city(
    territory_id: str = Path(..., description="City's 7-digit IBGE ID.")
):
    city_info = app.cities.get_city(territory_id)
    if city_info is None:
        return JSONResponse(status_code=404, content={"detail": "City not found."})
    return {"city": city_info}


@app.post(
    "/suggestions",
    response_model=CreatedSuggestionResponse,
    name="Send a suggestion",
    description="Send a suggestion to the project",
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def add_suggestion(response: Response, body: CreateSuggestionBody):
    suggestion = Suggestion(
        email_address=body.email_address, name=body.name, content=body.content,
    )
    suggestion_sent = app.suggestion_service.add_suggestion(suggestion)
    response.status_code = (
        status.HTTP_200_OK if suggestion_sent.success else status.HTTP_400_BAD_REQUEST
    )
    return {"status": suggestion_sent.status}


@app.get(
    "/company/info/{cnpj:path}",
    response_model=CompanySearchResponse,
    name="Get company info by CNPJ number",
    description="Get info from specific company by its CNPJ number.",
    responses={
        404: {"model": HTTPExceptionMessage, "description": "Company not found."},
        400: {"model": HTTPExceptionMessage, "description": "CNPJ is not valid."},
    },
)
async def get_company(
    cnpj: str = Path(
        ..., description="Company's CNPJ number (may include non-digit characters)."
    )
):
    try:
        company_info = app.companies.get_company(cnpj)
    except InvalidCNPJException as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    if company_info is None:
        return JSONResponse(status_code=404, content={"detail": "Company not found."})

    return {"cnpj_info": company_info}


@app.get(
    "/company/partners/{cnpj:path}",
    response_model=PartnersSearchResponse,
    name="Get company partners infos by CNPJ number",
    description="Get info of partners of a company by its CNPJ number.",
    responses={
        400: {"model": HTTPExceptionMessage, "description": "CNPJ is not valid."},
    },
)
async def get_partners(
    cnpj: str = Path(
        ..., description="Company's CNPJ number (may include non-digit characters)."
    )
):
    try:
        total_partners, partners = app.companies.get_partners(cnpj)
    except InvalidCNPJException as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    return {"total_partners": total_partners, "partners": partners}


def configure_api_app(
    gazettes: GazetteAccessInterface,
    themed_excerpts: ThemedExcerptAccessInterface,
    cities: CityAccessInterface,
    suggestion_service: SuggestionServiceInterface,
    companies: CompaniesAccessInterface,
    api_root_path=None,
):
    if not isinstance(gazettes, GazetteAccessInterface):
        raise Exception(
            "Only GazetteAccessInterface object are accepted for gazettes parameter"
        )
    if not isinstance(themed_excerpts, ThemedExcerptAccessInterface):
        raise Exception(
            "Only ThemedExcerptAccessInterface object are accepted for themed_excerpts parameter"
        )
    if not isinstance(cities, CityAccessInterface):
        raise Exception(
            "Only CityAccessInterface object are accepted for cities parameter"
        )
    if not isinstance(suggestion_service, SuggestionServiceInterface):
        raise Exception(
            "Only SuggestionServiceInterface object are accepted for suggestion_service parameter"
        )
    if not isinstance(companies, CompaniesAccessInterface):
        raise Exception(
            "Only CompaniesAccessInterface object are accepted for companies parameter"
        )
    if api_root_path is not None and type(api_root_path) != str:
        raise Exception("Invalid api_root_path")
    app.gazettes = gazettes
    app.themed_excerpts = themed_excerpts
    app.cities = cities
    app.suggestion_service = suggestion_service
    app.companies = companies
    app.root_path = api_root_path
