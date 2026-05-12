"""SQLite database layer for the budget tracker."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    amount REAL NOT NULL CHECK(amount > 0),
    category TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transaction(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transaction(category);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transaction(type);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    monthly_limit REAL NOT NULL CHECK(monthly_limit > 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
);
"""

class Database:
    """Thin wrapper around SQLite with proper context management."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Create tables if they don't exist"""
        with self.connect() as conn:
            conn.executescript(SCHEMA)
    
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Context-managed connection that always commits or roll back"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # rows behave like dicts
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()