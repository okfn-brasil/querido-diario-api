from unittest import TestCase
from unittest.mock import MagicMock, patch

import psycopg2

from database.postgresql_scraper import (
    ENSURE_STATE_TERRITORIES_COMMAND,
    PostgreSQLDatabaseScraper,
)


class EnsureStateTerritoriesTests(TestCase):
    def setUp(self):
        patcher = patch("database.postgresql_scraper.psycopg2.connect")
        self.mock_connect = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_cursor.description = None
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )

        execute_values_patcher = patch("database.postgresql_scraper.execute_values")
        execute_values_patcher.start()
        self.addCleanup(execute_values_patcher.stop)

    def make_db(self):
        return PostgreSQLDatabaseScraper("localhost", "test", "user", "password", 5432)

    def test_command_is_idempotent_and_registers_espirito_santo(self):
        self.assertIn(
            "('3299999', 'Governo do Estado do Espírito Santo', 'ES', 'Espírito Santo')",
            ENSURE_STATE_TERRITORIES_COMMAND,
        )
        self.assertIn("ON CONFLICT (id) DO NOTHING", ENSURE_STATE_TERRITORIES_COMMAND)

    def test_init_inserts_state_territories(self):
        db = self.make_db()

        self.mock_cursor.execute.assert_called_once_with(
            ENSURE_STATE_TERRITORIES_COMMAND, {}
        )
        self.mock_connection.commit.assert_called_once()
        self.mock_connection.close.assert_called_once()
        self.assertTrue(db._state_territories_ready)

    def test_init_does_not_fail_when_database_is_unavailable(self):
        self.mock_connect.side_effect = psycopg2.OperationalError("boom")

        db = self.make_db()

        self.assertFalse(db._state_territories_ready)

    def test_sync_spiders_retries_when_init_could_not_insert(self):
        self.mock_cursor.execute.side_effect = psycopg2.errors.UndefinedTable("boom")
        db = self.make_db()
        self.assertFalse(db._state_territories_ready)

        self.mock_cursor.execute.side_effect = None
        db.sync_spiders([("es_governo", "3299999", "2020-01-01")])

        self.assertTrue(db._state_territories_ready)
        self.assertEqual(self.mock_cursor.execute.call_count, 2)

    def test_sync_spiders_does_not_insert_again_once_ready(self):
        db = self.make_db()

        db.sync_spiders([("es_governo", "3299999", "2020-01-01")])

        self.mock_cursor.execute.assert_called_once()
