"""
Datenbankhelfer uebernommen aus der Uebung, nur um description ergaenzt
– wird von main.py importiert.
Diese Datei muss nicht veraendert werden.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("buchungen.db")


def get_connection() -> sqlite3.Connection:
    """Oeffnet eine SQLite-Verbindung."""
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db() -> None:
    """Erstellt die Tabelle 'buchungen', falls sie noch nicht existiert."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS buchungen (
            booking_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_date TEXT    NOT NULL,
            booking_type TEXT    NOT NULL,
            category     TEXT    NOT NULL,
            partner_name TEXT    NOT NULL,
            amount_net   REAL    NOT NULL,
            currency     TEXT    NOT NULL DEFAULT 'EUR',
            is_paid      INTEGER NOT NULL DEFAULT 0,
            description  TEXT
        )
        """
    )
    conn.commit()
    conn.close()
