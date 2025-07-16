import sqlite3
import sys
from logger import log


class ChainStorage:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_path)
            self._setup_schema()
            log.success("Database connection established and schema is ready.")
        except sqlite3.Error as e:
            log.error(f"Database connection error: {e}")
            sys.exit(1)

    def _setup_schema(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS chains (
            start TEXT PRIMARY KEY,
            end TEXT NOT NULL,
            length INTEGER NOT NULL
        );
        """

        create_index_query = """
        CREATE INDEX IF NOT EXISTS idx_end ON chains (end, length);
        """
        self.execute(create_table_query)
        self.execute(create_index_query)

    def execute(self, query, params=None):
        if not self.conn:
            return
        try:
            with self.conn:
                cursor = self.conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
        except sqlite3.Error as e:
            log.error(f"Query failed: {e}")

    def add_chains(self, chains_data):
        if not chains_data or not self.conn:
            return

        query = "INSERT OR IGNORE INTO chains (start, end, length) VALUES (?, ?, ?)"

        try:
            with self.conn:
                self.conn.executemany(query, chains_data)
        except sqlite3.Error as e:
            log.error(f"Batch insert failed: {e}")

    def get_start_candidates(self, end, length):
        if not self.conn:
            return None

        query = "SELECT start FROM chains WHERE end = ? AND length = ?"

        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(query, (end, length))

                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            log.error(f"Find query failed: {e}")
            return []

    def get_available_lengths(self):
        if not self.conn:
            return None

        query = "SELECT DISTINCT length FROM chains ORDER BY length DESC"

        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(query)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            log.error(f"Get lengths query failed: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            log.info("Database connection closed.")
