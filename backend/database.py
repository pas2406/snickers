import sqlite3
from contextlib import contextmanager

DATABASE = "watchvault.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row   # accès par nom : row["brand"]
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    """Context manager : commit auto, rollback sur erreur, fermeture garantie."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Crée les tables si elles n'existent pas encore."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS watches (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                brand         TEXT    NOT NULL,
                model         TEXT    NOT NULL,
                colorway      TEXT    NOT NULL,
                bracelet      TEXT    NOT NULL,
                reference     TEXT    NOT NULL UNIQUE,
                category      TEXT    NOT NULL,
                size_range    TEXT,
                retail_price  REAL    NOT NULL,
                resale_price  REAL,
                release_year  INTEGER,
                description   TEXT,
                image_url     TEXT,
                is_available  INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL UNIQUE,
                email      TEXT    NOT NULL UNIQUE,
                password   TEXT    NOT NULL,
                is_admin   INTEGER NOT NULL DEFAULT 0
            );
        """)
