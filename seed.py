"""
Seed-Skript uebernommen aus der Uebung - befuellt die Datenbank mit Beispieldaten.

Ausfuehren mit:
    uv run seed.py
"""
from database import get_connection, init_db

SAMPLE_BOOKINGS = [
    # (booking_date, booking_type, category, partner_name, amount_net, currency, is_paid)
    ("2025-01-10", "revenue",  "Beratung",  "Kunde Alpha GmbH",    4200.00, "EUR", 1),
    ("2025-01-18", "expense",  "Software",  "Adobe Inc.",            599.00, "EUR", 1),
    ("2025-01-25", "revenue",  "Marketing", "Kunde Beta AG",        3100.00, "EUR", 1),
    ("2025-02-05", "expense",  "Buero",     "Landlord KG",          1200.00, "EUR", 1),
    ("2025-02-14", "revenue",  "Beratung",  "Kunde Gamma Ltd",      8500.00, "EUR", 0),
    ("2025-02-20", "expense",  "Software",  "Microsoft",             299.00, "EUR", 0),
    ("2025-03-03", "revenue",  "Support",   "Kunde Delta Inc.",     2700.00, "EUR", 1),
    ("2025-03-15", "expense",  "Marketing", "Agentur Epsilon",      1800.00, "EUR", 1),
    ("2025-03-28", "revenue",  "Marketing", "Kunde Zeta GmbH",      5600.00, "EUR", 0),
    ("2025-04-02", "expense",  "Buero",     "Strom AG",              420.00, "EUR", 1),
    ("2025-04-11", "revenue",  "Support",   "Kunde Eta Corp",       1950.00, "EUR", 1),
    ("2025-04-22", "expense",  "Software",  "GitHub Inc.",           192.00, "EUR", 1),
    ("2025-05-07", "revenue",  "Beratung",  "Kunde Theta GmbH",     6300.00, "EUR", 0),
    ("2025-05-19", "expense",  "Buero",     "Internet Provider",     480.00, "EUR", 0),
    ("2025-06-01", "revenue",  "Marketing", "Kunde Iota Ltd",       3800.00, "EUR", 1),
]


def seed() -> None:
    init_db()
    conn = get_connection()
    conn.execute("DELETE FROM buchungen")
    conn.executemany(
        """INSERT INTO buchungen
           (booking_date, booking_type, category, partner_name, amount_net, currency, is_paid)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        SAMPLE_BOOKINGS,
    )
    conn.commit()
    conn.close()
    print(f"{len(SAMPLE_BOOKINGS)} Beispiel-Buchungen wurden in die Datenbank geschrieben.")


if __name__ == "__main__":
    seed()
