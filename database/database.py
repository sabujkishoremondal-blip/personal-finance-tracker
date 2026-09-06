"""SQLite schema + settings helpers.

Each finance row (expenses, balance_transactions, debts, categories, budgets,
recurring, app_settings) is scoped by user_id so multiple users are fully isolated.
"""
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
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT DEFAULT '',
    whatsapp_number TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    icon TEXT DEFAULT '📦',
    color TEXT DEFAULT '#8F002B',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT DEFAULT '',
    date TEXT NOT NULL,
    merchant TEXT DEFAULT '',
    source TEXT DEFAULT 'manual',
    screenshot_path TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS balance_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount REAL NOT NULL,
    tx_type TEXT NOT NULL,
    source TEXT DEFAULT '',
    description TEXT DEFAULT '',
    date TEXT NOT NULL,
    related_debt_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    direction TEXT NOT NULL,
    person TEXT NOT NULL,
    amount REAL NOT NULL,
    reason TEXT DEFAULT '',
    date TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    settled_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    UNIQUE(user_id, year, month, category)
);

CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT DEFAULT '',
    frequency TEXT NOT NULL,        -- monthly | weekly
    day_of_month INTEGER,
    day_of_week INTEGER,            -- 0=Mon
    start_date TEXT NOT NULL,
    end_date TEXT,
    last_run TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT,
    UNIQUE(user_id, key)
);

CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    direction TEXT NOT NULL,        -- in | out
    body TEXT DEFAULT '',
    parsed_amount REAL,
    parsed_category TEXT,
    expense_id INTEGER,
    status TEXT DEFAULT 'saved',    -- saved | needs_review | failed
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

USER_DEFAULT_SETTINGS = {
    "user_name": "You",
    "currency": "INR",
    "theme": "light",
    "starting_balance": "0",
}


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def get_setting(user_id: int, key: str, default=None):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM app_settings WHERE user_id=? AND key=?",
            (user_id, key),
        ).fetchone()
        if row is not None:
            return row["value"]
        return default


def set_setting(user_id: int, key: str, value):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO app_settings(user_id,key,value) VALUES(?,?,?) "
            "ON CONFLICT(user_id,key) DO UPDATE SET value=excluded.value",
            (user_id, key, str(value)),
        )


def seed_user_defaults(user_id: int, name: str = "You"):
    """Insert default categories and settings for a newly-registered user."""
    from utils.constants import DEFAULT_CATEGORIES
    with get_conn() as conn:
        for c in DEFAULT_CATEGORIES:
            conn.execute(
                "INSERT OR IGNORE INTO categories(user_id,name,icon,color) VALUES(?,?,?,?)",
                (user_id, c["name"], c["icon"], c["color"]),
            )
    for k, v in USER_DEFAULT_SETTINGS.items():
        if k == "user_name":
            v = name
        set_setting(user_id, k, v)


def reset_user_data(user_id: int):
    """Wipe all finance data for a single user (keeps the user account)."""
    with get_conn() as conn:
        for tbl in ["expenses", "balance_transactions", "debts", "budgets",
                    "recurring_expenses", "categories", "app_settings",
                    "whatsapp_messages"]:
            conn.execute(f"DELETE FROM {tbl} WHERE user_id=?", (user_id,))
    seed_user_defaults(user_id)
