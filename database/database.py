import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "finance.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon TEXT DEFAULT '📦',
    color TEXT DEFAULT '#8F002B',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT DEFAULT '',
    date TEXT NOT NULL,
    merchant TEXT DEFAULT '',
    source TEXT DEFAULT 'manual',   -- manual | screenshot
    screenshot_path TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS balance_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    tx_type TEXT NOT NULL,          -- balance_addition | borrowed_received | borrowed_repaid | friend_repaid | starting_balance
    source TEXT DEFAULT '',
    description TEXT DEFAULT '',
    date TEXT NOT NULL,
    related_debt_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT NOT NULL,        -- borrowed | lent
    person TEXT NOT NULL,
    amount REAL NOT NULL,
    reason TEXT DEFAULT '',
    date TEXT NOT NULL,
    status TEXT DEFAULT 'open',     -- open | settled
    settled_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    category TEXT NOT NULL,         -- 'TOTAL' or category name
    amount REAL NOT NULL,
    UNIQUE(year, month, category)
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        # seed default categories
        cur = conn.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            from utils.constants import DEFAULT_CATEGORIES
            for c in DEFAULT_CATEGORIES:
                conn.execute(
                    "INSERT INTO categories(name,icon,color) VALUES(?,?,?)",
                    (c["name"], c["icon"], c["color"]),
                )
        # seed default settings
        defaults = {
            "user_name": "You",
            "currency": "INR",
            "theme": "light",
            "starting_balance": "2000",
            "onboarded": "0",
        }
        for k, v in defaults.items():
            conn.execute(
                "INSERT OR IGNORE INTO app_settings(key,value) VALUES(?,?)", (k, v)
            )


def get_setting(key, default=None):
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO app_settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )


def reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
