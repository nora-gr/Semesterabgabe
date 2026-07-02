"""
ABV 8 – FastAPI Buchungsverwaltung
===================================
Starten:     uvicorn main:app --reload
Swagger UI:  http://127.0.0.1:8000/docs
Redoc:       http://127.0.0.1:8000/redoc

Lesen Sie AUFGABE.md fuer die vollstaendigen Aufgabenstellungen.
"""
from typing import Optional
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from database import get_connection, init_db
from models import BookingCreate

init_db()   # ← plain sync function, no await needed

app = FastAPI(
    title="Buchungsverwaltung",
    version="1.0.0",
    description="Uebungs-API",
)

@app.get("/")
def root():
    return {"Nachricht": "Willkommen beim Buchungssystem!"}


# @app.get gibt alle Buchungen zurueck

@app.get("/bookings", tags=["Buchungen"], summary="Alle Buchungen abrufen")
def get_bookings(
    category: Optional[str] = Query(default=None, description="Filter nach Kategorie (z. B. 'Marketing')"),
    is_paid: Optional[bool] = Query(default=None, description="Filter nach Zahlungsstatus"),
):
    """
    Ergaenzung um Filter.
    """
    conn = get_connection()

    if category is not None and is_paid is not None:
        df = pd.read_sql_query(
             "SELECT * FROM buchungen WHERE category = ? AND is_paid = ?",
             conn, params=[category, int(is_paid)]
        )
    elif category is not None:
        df = pd.read_sql_query(
            "SELECT * FROM buchungen WHERE category = ?",
            conn, params=[category]
        )
    elif is_paid is not None:
        df = pd.read_sql_query(
            "SELECT * FROM buchungen WHERE is_paid = ?",
            conn, params=[int(is_paid)]
        )
    else:
        df = pd.read_sql_query("SELECT * FROM buchungen", conn)
    conn.close()
    return df.to_dict(orient="records")


# neue Buchung erstellen

@app.post("/bookings", status_code=201, tags=["Buchungen"], summary="Neue Buchung erstellen")
def create_booking(booking: BookingCreate):
    conn = get_connection()
    df_new = pd.DataFrame([booking.model_dump()])
    df_new["is_paid"] = df_new["is_paid"].astype(int)   # bool → 0/1 fuer SQLite
    df_new.to_sql("buchungen", conn, if_exists="append", index=False)
    conn.close()
    return {"message": "Buchung erstellt"}


# =============================================================
#  GET /bookings/find?booking_id=...
# =============================================================

@app.get("/bookings/find", tags=["Buchungen"], summary="Einzelne Buchung per Query-Parameter abrufen")
def get_booking_by_id(booking_id: int = Query(description="ID der gesuchten Buchung")):
   # Verbindung zur Datenbank
   conn = get_connection()
   # Buchung per Pandas laden
   df = pd.read_sql_query( "SELECT * FROM buchungen WHERE booking_id = ?",
    conn, params=[booking_id] )
   # Fehlermeldungen
   if df.empty:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
   # Verbindung zur Datenbank schliessen
   conn.close()
   return df.iloc[0].to_dict()
   
# noch implementieren:    raise HTTPException(status_code=501, detail="Noch nicht implementiert")


# Markiert eine Buchung als bezahlt (is_paid = 1).

@app.put("/bookings/{booking_id}/pay", tags=["Buchungen"], summary="Buchung als bezahlt markieren")
def mark_booking_paid(booking_id: int):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM buchungen WHERE booking_id = ?",
        conn, params=[booking_id]
    )

    if df.empty:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")

    if df.iloc[0]["is_paid"] == 1:
        raise HTTPException(status_code=400, detail="Buchung ist bereits als bezahlt markiert")
    conn.execute(
    "UPDATE buchungen SET is_paid = 1 WHERE booking_id = ?", 
    (booking_id,)
    )
    conn.commit()
    conn.close()
        
## raise HTTPException(status_code=501, detail="Noch nicht implementiert")


# =============================================================
# HAUSAUFGABE – GET /stats
# =============================================================


#@app.get("/stats", tags=["Statistiken"], summary="Finanzstatistiken abrufen")
#def get_stats():
    """
    Gibt aggregierte Finanzstatistiken zurueck.

    ╔══════════════════════════════════════════╗
    ║  HAUSAUFGABE – Statistik-Endpunkt        ║
    ╚══════════════════════════════════════════╝
    Implementiere diesen Endpunkt so, dass er folgendes Dictionary liefert:

    {
        "total_bookings":  <int>,     Gesamtanzahl aller Buchungen
        "total_revenue":   <float>,   Summe aller Einnahmen (booking_type='revenue')
        "total_expenses":  <float>,   Summe aller Ausgaben  (booking_type='expense')
        "net_profit":      <float>,   Einnahmen - Ausgaben
        "paid_rate_pct":   <float>,   Anteil bezahlter Buchungen in % (2 Nachkommastellen)
        "by_category": [
            {
                "category": <str>,
                "revenue":  <float>,
                "expenses": <float>,
                "net":      <float>,
                "count":    <int>
            },
#            ...                       sortiert nach net absteigend
        ]
    }

    Hinweise:
    - Lade alle Buchungen mit pd.read_sql_query() in einen DataFrame.
    - Nutze pandas-Operationen (groupby, agg, sum, mean) fuer die Berechnungen.
    - Alle float-Werte sollen auf 2 Nachkommastellen gerundet sein.
    - Der Endpunkt soll auch bei einer leeren Datenbank ohne Fehler laufen
      (z. B. paid_rate_pct = 0.0 wenn keine Buchungen vorhanden).

    WICHTIG fuer naechste Woche:
    Dieser Endpunkt wird von einer Streamlit-App direkt aufgerufen.
    Halte dich exakt an das Schema oben – Feldnamen und Typen muessen stimmen.
    """
#    # TODO: Implementierung hier
#    raise HTTPException(status_code=501, detail="Noch nicht implementiert")
