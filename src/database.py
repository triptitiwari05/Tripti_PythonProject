import os
import sqlite3
from contextlib import contextmanager


class Database:
    def __init__(self, db_path, schema_path):
        self.db_path = db_path
        self.schema_path = schema_path
        self._ensure_parent_dir()
        self._initialize_db()

    def _ensure_parent_dir(self):
        parent = os.path.dirname(self.db_path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)

    def _initialize_db(self):
        with self.get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            with open(self.schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, query, params=None):
        params = params or ()
        with self.get_connection() as conn:
            try:
                cur = conn.execute(query, params)
                return cur.lastrowid
            except sqlite3.IntegrityError as exc:
                raise ValueError(str(exc)) from exc

    def fetch_all(self, query, params=None):
        params = params or ()
        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return cur.fetchall()

    def fetch_one(self, query, params=None):
        params = params or ()
        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return cur.fetchone()
