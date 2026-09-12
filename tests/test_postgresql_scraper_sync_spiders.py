from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from database.postgresql_scraper import PostgreSQLDatabaseScraper


def make_scraper_db():
    db = PostgreSQLDatabaseScraper.__new__(PostgreSQLDatabaseScraper)
    db.database = "test"
    db.user = "user"
    db.password = "password"
    db.host = "localhost"
    db.port = 5432
    return db


class SyncSpidersTests(TestCase):
    def setUp(self):
        patcher = patch("database.postgresql_scraper.psycopg2.connect")
        self.mock_connect = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )

        execute_values_patcher = patch(
            "database.postgresql_scraper.execute_values"
        )
        self.mock_execute_values = execute_values_patcher.start()
        self.addCleanup(execute_values_patcher.stop)

        self.db = make_scraper_db()

    def test_empty_map_does_not_open_a_connection(self):
        result = self.db.sync_spiders([])

        self.assertEqual(result, 0)
        self.mock_connect.assert_not_called()

    def test_uses_a_single_connection_regardless_of_spider_count(self):
        territory_spider_map = [
            (f"spider_{i}", "1234567", "2020-01-01") for i in range(450)
        ]

        self.db.sync_spiders(territory_spider_map)

        self.mock_connect.assert_called_once()
        self.mock_connection.commit.assert_called_once()
        self.mock_connection.close.assert_called_once()

    def test_dedups_spiders_by_name_before_the_upsert(self):
        # o mesmo spider pode aparecer mais de uma vez, uma entrada por
        # território que ele cobre
        territory_spider_map = [
            ("spider_a", "1111111", "2020-01-01"),
            ("spider_a", "2222222", "2020-01-01"),
            ("spider_b", "1111111", "2021-06-15"),
        ]

        result = self.db.sync_spiders(territory_spider_map)

        self.assertEqual(result, 3)

        spiders_call, territory_call = self.mock_execute_values.call_args_list

        _cursor, _sql, spiders_values = spiders_call.args
        self.assertCountEqual(
            spiders_values,
            [("spider_a", "2020-01-01", False), ("spider_b", "2021-06-15", False)],
        )

        _cursor, _sql, territory_values = territory_call.args
        self.assertCountEqual(
            territory_values,
            [
                ("spider_a", "1111111"),
                ("spider_a", "2222222"),
                ("spider_b", "1111111"),
            ],
        )

    def test_connection_is_closed_even_if_the_upsert_fails(self):
        self.mock_execute_values.side_effect = Exception("boom")

        with self.assertRaises(Exception):
            self.db.sync_spiders([("spider_a", "1234567", "2020-01-01")])

        self.mock_connection.close.assert_called_once()
        self.mock_connection.commit.assert_not_called()
