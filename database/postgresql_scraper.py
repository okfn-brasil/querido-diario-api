import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import Json, execute_values

from scraper import InvalidTerritoryIDException, ScraperDatabaseInterface

from .postgresql import PostgreSQLDatabase


CREATE_JOB_STATS_TABLE_COMMAND = """
CREATE TABLE IF NOT EXISTS job_stats (
    id SERIAL PRIMARY KEY,
    spider_name TEXT NOT NULL,
    job_id TEXT,
    stats JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

MIGRATE_JOB_STATS_TABLE_COMMAND = """
DO $$
BEGIN
    -- Renomeia colunas do schema legado
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='job_stats'
    ) THEN
        ALTER TABLE job_stats RENAME COLUMN job_stats TO stats;
    END IF;
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='start_time'
    ) THEN
        ALTER TABLE job_stats RENAME COLUMN start_time TO created_at;
    END IF;

    -- Garante colunas canônicas (instalações novas sem schema legado)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='spider_name'
    ) THEN
        ALTER TABLE job_stats ADD COLUMN spider_name TEXT;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='job_id'
    ) THEN
        ALTER TABLE job_stats ADD COLUMN job_id TEXT;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='stats'
    ) THEN
        ALTER TABLE job_stats ADD COLUMN stats JSONB;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='created_at'
    ) THEN
        ALTER TABLE job_stats ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- Backfill e remoção da coluna legada spider (idempotente)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='spider'
    ) THEN
        UPDATE job_stats SET spider_name = spider WHERE spider_name IS NULL AND spider IS NOT NULL;
        ALTER TABLE job_stats DROP COLUMN spider;
    END IF;
END $$;

-- Uniformiza tipos para bater com o schema canônico
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='stats' AND data_type='json'
    ) THEN
        ALTER TABLE job_stats ALTER COLUMN stats TYPE JSONB USING stats::jsonb;
    END IF;
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='created_at'
        AND data_type='timestamp without time zone'
    ) THEN
        ALTER TABLE job_stats ALTER COLUMN created_at TYPE TIMESTAMPTZ
            USING created_at AT TIME ZONE 'UTC';
    END IF;
END $$;

-- Adiciona NOT NULL após backfill e conversão de tipos
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='spider_name' AND is_nullable='YES'
    ) THEN
        ALTER TABLE job_stats ALTER COLUMN spider_name SET NOT NULL;
    END IF;
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='job_stats' AND column_name='stats' AND is_nullable='YES'
    ) THEN
        ALTER TABLE job_stats ALTER COLUMN stats SET NOT NULL;
    END IF;
END $$;
"""


class PostgreSQLDatabaseScraper(PostgreSQLDatabase, ScraperDatabaseInterface):
    _job_stats_table_ready = False

    def _execute(self, command: str, data: Dict = {}) -> List[Tuple]:
        """
        Execute a write command, commit it and return the rows produced by a
        RETURNING clause (if any).
        """
        connection = psycopg2.connect(
            dbname=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(command, data)
                logging.debug(f"Executed command: {cursor.query}")
                results = cursor.fetchall() if cursor.description is not None else []
            connection.commit()
            return results
        finally:
            connection.close()

    def get_enabled_spiders(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Dict]:
        command = """
        SELECT
            spider_name, date_from, date_to
        FROM
            querido_diario_spiders
        WHERE
            enabled IS TRUE
            AND (%(start_date)s IS NULL OR date_to IS NULL OR date_to >= %(start_date)s)
            AND (%(end_date)s IS NULL OR date_from <= %(end_date)s)
        ORDER BY spider_name
        ;
        """
        data = {"start_date": start_date, "end_date": end_date}
        return [
            self._format_spider_data(result) for result in self._select(command, data)
        ]

    def insert_gazette(self, gazette: Dict) -> Optional[int]:
        command = """
        INSERT INTO gazettes (
            source_text, date, edition_number, is_extra_edition, power,
            file_checksum, file_path, file_url, scraped_at, created_at,
            territory_id, processed
        ) VALUES (
            %(source_text)s, %(date)s, %(edition_number)s, %(is_extra_edition)s,
            %(power)s, %(file_checksum)s, %(file_path)s, %(file_url)s,
            %(scraped_at)s, NOW(), %(territory_id)s, FALSE
        )
        ON CONFLICT (territory_id, date, file_checksum) DO NOTHING
        RETURNING id
        ;
        """
        try:
            results = self._execute(command, gazette)
        except psycopg2.errors.ForeignKeyViolation:
            raise InvalidTerritoryIDException(
                f'Territory "{gazette["territory_id"]}" does not exist.'
            )
        if not results:
            return None
        return results[0][0]

    def insert_job_stats(
        self, spider_name: str, job_id: Optional[str], stats: Dict
    ) -> int:
        self._ensure_job_stats_table()
        command = """
        INSERT INTO job_stats (spider_name, job_id, stats)
        VALUES (%(spider_name)s, %(job_id)s, %(stats)s)
        RETURNING id
        ;
        """
        data = {"spider_name": spider_name, "job_id": job_id, "stats": Json(stats)}
        results = self._execute(command, data)
        return results[0][0]

    def get_job_stats(
        self,
        spider: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict]:
        self._ensure_job_stats_table()
        command = """
        SELECT
            id, spider_name, job_id, stats, created_at
        FROM
            job_stats
        WHERE
            (%(spider)s IS NULL OR spider_name = %(spider)s)
            AND (%(since)s IS NULL OR created_at >= %(since)s)
        ORDER BY created_at DESC
        LIMIT %(limit)s
        ;
        """
        data = {"spider": spider, "since": since, "limit": limit}
        return [
            self._format_job_stats_data(result)
            for result in self._select(command, data)
        ]

    def set_spider_enabled(self, spider_name: str, enabled: bool) -> bool:
        command = """
        UPDATE querido_diario_spiders
        SET enabled = %(enabled)s
        WHERE spider_name = %(spider_name)s
        RETURNING spider_name
        ;
        """
        data = {"spider_name": spider_name, "enabled": enabled}
        results = self._execute(command, data)
        return bool(results)

    def sync_spiders(self, territory_spider_map: List[tuple]) -> int:
        """Register/update spiders and their territory mapping in bulk.

        Uses a single connection and two batched upserts (instead of one
        connection + two statements *per spider*) — with 400+ spiders, the
        per-row round trips (each opening/closing its own connection) were
        slow enough to blow past callers' HTTP read timeouts.
        """
        if not territory_spider_map:
            return 0

        # Um spider pode aparecer mais de uma vez (uma entrada por território
        # que ele cobre) — dedup por spider_name antes do upsert em lote,
        # já que um único INSERT ... ON CONFLICT DO UPDATE não pode afetar a
        # mesma linha duas vezes (CardinalityViolation).
        spiders_by_name = {
            spider_name: date_from
            for spider_name, _territory_id, date_from in territory_spider_map
        }

        connection = psycopg2.connect(
            dbname=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        try:
            with connection.cursor() as cursor:
                execute_values(
                    cursor,
                    """
                    INSERT INTO querido_diario_spiders (spider_name, date_from, enabled)
                    VALUES %s
                    ON CONFLICT (spider_name) DO UPDATE
                        SET date_from = EXCLUDED.date_from
                        WHERE querido_diario_spiders.date_from <> EXCLUDED.date_from
                    """,
                    [
                        (spider_name, date_from, False)
                        for spider_name, date_from in spiders_by_name.items()
                    ],
                )
                execute_values(
                    cursor,
                    """
                    INSERT INTO territory_spider_map (spider_name, territory_id)
                    VALUES %s
                    ON CONFLICT DO NOTHING
                    """,
                    [
                        (spider_name, territory_id)
                        for spider_name, territory_id, _date_from in territory_spider_map
                    ],
                )
            connection.commit()
            return len(territory_spider_map)
        finally:
            connection.close()

    def _ensure_job_stats_table(self) -> None:
        if not self._job_stats_table_ready:
            self._execute(CREATE_JOB_STATS_TABLE_COMMAND)
            self._execute(MIGRATE_JOB_STATS_TABLE_COMMAND)
            self._job_stats_table_ready = True

    def _format_spider_data(self, data: Tuple) -> Dict:
        return {
            "spider_name": data[0],
            "date_from": data[1],
            "date_to": data[2],
        }

    def _format_job_stats_data(self, data: Tuple) -> Dict:
        return {
            "id": data[0],
            "spider_name": data[1],
            "job_id": data[2],
            "stats": data[3],
            "created_at": data[4],
        }
