"""
Testes de integração do território de governo estadual (ADR-0006), usando o
Espírito Santo (`3299999`) como caso piloto.

Diferente dos demais testes, estes usam o OpenSearch e o PostgreSQL de verdade
(os mesmos serviços do `docker-compose.test.yml`), porque o que se quer garantir
é o comportamento do filtro *terms* e da chave estrangeira de `gazettes`, e não
o repasse de parâmetros entre camadas. Só rodam com `RUN_INTEGRATION_TESTS=1`.
"""

import os
import uuid
from unittest import TestCase, skipUnless
from unittest.mock import patch

import opensearchpy
import psycopg2
from fastapi.testclient import TestClient

from api import app, configure_api_app
from database import create_scraper_database_interface
from gazettes import (
    create_gazettes_data_gateway,
    create_gazettes_interface,
    create_gazettes_query_builder,
)
from index import create_search_engine_interface
from scraper import create_scraper_interface

from tests.test_helpers import create_default_mocks
from tests.test_scraper_api import (
    TEST_API_KEY,
    TEST_API_KEY_HEADERS,
    build_gazette_payload,
)

RUN_INTEGRATION_TESTS = os.environ.get("RUN_INTEGRATION_TESTS") == "1"

ES_STATE_ID = "3299999"
ES_STATE_NAME = "Governo do Estado do Espírito Santo"
VITORIA_ID = "3205309"
SERRA_ID = "3205002"
RJ_STATE_ID = "3399999"

INDEX_BODY = {
    "mappings": {
        "properties": {
            "date": {"type": "date"},
            "scraped_at": {"type": "date"},
            "territory_id": {"type": "keyword"},
            "source_text": {
                "type": "text",
                "term_vector": "with_positions_offsets",
                "fields": {
                    "exact": {
                        "type": "text",
                        "term_vector": "with_positions_offsets",
                    }
                },
            },
        }
    }
}

# Mesmo schema criado pelos raspadores (querido-diario, gazette/database/models.py)
CREATE_SCRAPER_TABLES_COMMAND = """
CREATE TABLE territories (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    state_code VARCHAR,
    state VARCHAR
);
CREATE TABLE gazettes (
    id SERIAL PRIMARY KEY,
    source_text TEXT,
    date DATE,
    edition_number VARCHAR,
    is_extra_edition BOOLEAN,
    power VARCHAR,
    file_checksum VARCHAR,
    file_path VARCHAR,
    file_url VARCHAR,
    scraped_at TIMESTAMP,
    created_at TIMESTAMP,
    territory_id VARCHAR REFERENCES territories (id),
    processed BOOLEAN,
    UNIQUE (territory_id, date, file_checksum)
);
INSERT INTO territories (id, name, state_code, state)
VALUES ('3205309', 'Vitória', 'ES', 'Espírito Santo');
"""


def build_indexed_gazette(territory_id, territory_name, checksum, day, state_code="ES"):
    return {
        "source_text": "DECRETO Nº 1234-R nomeia servidores",
        "date": f"2026-09-{day:02d}",
        "scraped_at": "2026-10-01T03:04:05",
        "url": f"{territory_id}/2026-09-{day:02d}/{checksum}.pdf",
        "file_checksum": checksum,
        "territory_id": territory_id,
        "territory_name": territory_name,
        "state_code": state_code,
        "edition_number": str(26800 + day),
        "is_extra_edition": False,
    }


@skipUnless(RUN_INTEGRATION_TESTS, "RUN_INTEGRATION_TESTS != 1")
class StateTerritoryGazettesSearchTests(TestCase):
    @classmethod
    def setUpClass(cls):
        host = os.environ.get("QUERIDO_DIARIO_OPENSEARCH_HOST", "localhost")
        credentials = (
            os.environ.get("QUERIDO_DIARIO_OPENSEARCH_USER", "admin"),
            os.environ.get("QUERIDO_DIARIO_OPENSEARCH_PASSWORD", "admin"),
        )
        cls.index = f"test-state-territory-{uuid.uuid4().hex}"
        cls.opensearch = opensearchpy.OpenSearch(hosts=[host], http_auth=credentials)
        cls.opensearch.indices.create(index=cls.index, body=INDEX_BODY)
        cls.addClassCleanup(
            cls.opensearch.indices.delete, index=cls.index, ignore_unavailable=True
        )

        gazettes = [
            build_indexed_gazette(ES_STATE_ID, ES_STATE_NAME, "es-estado-1", 1),
            build_indexed_gazette(ES_STATE_ID, ES_STATE_NAME, "es-estado-2", 2),
            build_indexed_gazette(VITORIA_ID, "Vitória", "es-vitoria-1", 1),
            build_indexed_gazette(SERRA_ID, "Serra", "es-serra-1", 1),
            build_indexed_gazette(
                RJ_STATE_ID,
                "Governo do Estado do Rio de Janeiro",
                "rj-estado-1",
                1,
                state_code="RJ",
            ),
        ]
        bulk_data = []
        for gazette in gazettes:
            bulk_data.append({"index": {"_id": gazette["file_checksum"]}})
            bulk_data.append(gazette)
        cls.opensearch.bulk(bulk_data, index=cls.index, refresh=True)

        search_engine = create_search_engine_interface(host, credentials, cls.index)
        query_builder = create_gazettes_query_builder(
            "source_text", ".exact", "date", "scraped_at", "territory_id"
        )
        cls.gazettes_interface = create_gazettes_interface(
            create_gazettes_data_gateway(search_engine, query_builder, cls.index)
        )

    def setUp(self):
        mocks = create_default_mocks()
        configure_api_app(self.gazettes_interface, *mocks[1:])
        self.client = TestClient(app)

    def _search(self, **params):
        response = self.client.get("/gazettes", params=params)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_search_by_state_territory_id_returns_only_state_gazettes(self):
        result = self._search(territory_ids=ES_STATE_ID)

        self.assertEqual(result["total_gazettes"], 2)
        self.assertEqual(len(result["gazettes"]), 2)
        for gazette in result["gazettes"]:
            self.assertEqual(gazette["territory_id"], ES_STATE_ID)
            self.assertEqual(gazette["territory_name"], ES_STATE_NAME)
            self.assertEqual(gazette["state_code"], "ES")

    def test_search_by_state_territory_id_with_querystring_returns_only_state_gazettes(
        self,
    ):
        result = self._search(territory_ids=ES_STATE_ID, querystring="decreto")

        self.assertEqual(result["total_gazettes"], 2)
        self.assertEqual(
            {gazette["territory_id"] for gazette in result["gazettes"]},
            {ES_STATE_ID},
        )

    def test_search_by_city_territory_id_does_not_return_state_gazettes(self):
        result = self._search(territory_ids=VITORIA_ID)

        self.assertEqual(result["total_gazettes"], 1)
        self.assertEqual(result["gazettes"][0]["territory_id"], VITORIA_ID)

    def test_search_by_state_and_city_territory_ids_returns_both(self):
        result = self._search(territory_ids=[ES_STATE_ID, VITORIA_ID])

        self.assertEqual(result["total_gazettes"], 3)
        self.assertEqual(
            {gazette["territory_id"] for gazette in result["gazettes"]},
            {ES_STATE_ID, VITORIA_ID},
        )


@skipUnless(RUN_INTEGRATION_TESTS, "RUN_INTEGRATION_TESTS != 1")
class StateTerritoryScraperGazettesTests(TestCase):
    def setUp(self):
        self.connection_data = {
            "host": os.environ.get("POSTGRES_COMPANIES_HOST", "localhost"),
            "dbname": os.environ.get("POSTGRES_COMPANIES_DB", "companiesdb"),
            "user": os.environ.get("POSTGRES_COMPANIES_USER", "companies"),
            "password": os.environ.get("POSTGRES_COMPANIES_PASSWORD", "companies"),
            "port": os.environ.get("POSTGRES_COMPANIES_PORT", "5432"),
        }
        # Schema descartável: o search_path via PGOPTIONS faz as conexões abertas
        # pelo gateway enxergarem só as tabelas criadas aqui.
        self.schema = f"test_state_territory_{uuid.uuid4().hex}"
        self._run_sql(f"CREATE SCHEMA {self.schema}", use_schema=False)
        self.addCleanup(
            self._run_sql, f"DROP SCHEMA {self.schema} CASCADE", use_schema=False
        )
        env_patcher = patch.dict(
            os.environ,
            {
                "PGOPTIONS": f"-c search_path={self.schema}",
                "QUERIDO_DIARIO_SCRAPER_API_KEYS": TEST_API_KEY,
            },
        )
        env_patcher.start()
        self.addCleanup(env_patcher.stop)
        self._run_sql(CREATE_SCRAPER_TABLES_COMMAND)

        # Instanciar o gateway é o "startup" da API: é aqui que os territórios
        # estaduais são inseridos.
        scraper_database = create_scraper_database_interface(
            db_host=self.connection_data["host"],
            db_name=self.connection_data["dbname"],
            db_user=self.connection_data["user"],
            db_pass=self.connection_data["password"],
            db_port=self.connection_data["port"],
        )
        mocks = create_default_mocks()
        configure_api_app(*mocks[:6], create_scraper_interface(scraper_database))
        self.client = TestClient(app)

    def _run_sql(self, command, use_schema=True):
        options = f"-c search_path={self.schema}" if use_schema else ""
        connection = psycopg2.connect(options=options, **self.connection_data)
        try:
            with connection.cursor() as cursor:
                cursor.execute(command)
                results = cursor.fetchall() if cursor.description is not None else []
            connection.commit()
            return results
        finally:
            connection.close()

    def _post_state_gazette(self):
        return self.client.post(
            "/scraper/gazettes",
            headers=TEST_API_KEY_HEADERS,
            json=build_gazette_payload(
                territory_id=ES_STATE_ID,
                file_path=f"{ES_STATE_ID}/2024-06-01/abc123",
            ),
        )

    def test_startup_registers_state_territory(self):
        territories = self._run_sql(
            f"SELECT name, state_code FROM territories WHERE id = '{ES_STATE_ID}'"
        )

        self.assertEqual(territories, [(ES_STATE_NAME, "ES")])

    def test_gazette_of_state_territory_is_accepted(self):
        response = self._post_state_gazette()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "created")
        self.assertEqual(
            self._run_sql("SELECT id, territory_id, processed FROM gazettes"),
            [(response.json()["gazette_id"], ES_STATE_ID, False)],
        )

    def test_repeated_gazette_of_state_territory_is_reported_as_duplicate(self):
        self._post_state_gazette()

        response = self._post_state_gazette()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "duplicate"})
        self.assertEqual(self._run_sql("SELECT COUNT(*) FROM gazettes"), [(1,)])

    def test_gazette_is_rejected_when_state_territory_does_not_exist(self):
        self._run_sql(f"DELETE FROM territories WHERE id = '{ES_STATE_ID}'")

        response = self._post_state_gazette()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"detail": f'Territory "{ES_STATE_ID}" does not exist.'},
        )
        self.assertEqual(self._run_sql("SELECT COUNT(*) FROM gazettes"), [(0,)])
