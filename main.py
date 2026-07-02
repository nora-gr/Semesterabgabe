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
# GET /stats - gibt aggregierte Finanzstatistiken zurück.
# =============================================================
@app.get("/stats", tags=["Statistiken"], summary="Finanzstatistiken abrufen")
def get_stats():
    # Datenbank aufrufen
    conn = get_connection()
    # alle Buchungen in einen Dataframe laden
    df = pd.read_sql_query(
        "SELECT * FROM buchungen",
        conn
    )
    
    # Gesamtzahl aller Buchungen berechnen
    total_bookings = len(df)

    totals = df.groupby("booking_type")["amount_net"].sum()
    # Summe aller Einnahmen berechnen
    total_revenue = totals.get("revenue", 0)
    # Summe aller Ausgaben berechnen
    total_expenses = totals.get("expense", 0)
    
    # Gewinn berechnen
    net_profit = total_revenue - total_expenses

    # Anteil bezahlter Buchungen in % (2 Nachkommastellen)
    # Werte sind 1 oder 0, deshalb Mittelwert und dann mal 100
    paid_rate_pct = df["is_paid"].mean() * 100

    # Gruppen sortiert nach net absteigend auflisten
    categories = df["category"].unique()
    by_category = []
    for category in categories:
        revenue = df[(df["category"] == category) & (df["booking_type"] == "revenue")]["amount_net"].sum()
        expenses = df[(df["category"] == category) & (df["booking_type"] == "expense")]["amount_net"].sum()

        by_category.append({
            "category": category,
            "revenue": round(revenue, 2),
            "expenses": round(expenses, 2),
            "net": round(revenue - expenses, 2),
            "count": len(df[df["category"] == category])
        })
        
    # Kategorien sortieren
    by_category.sort(
        key = lambda x: x["net"],
        reverse = True
    )

    # Ausgabe
    return {
        "total_bookings": total_bookings,
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(net_profit, 2),
        "paid_rate_pct": round(paid_rate_pct, 2),
        "by_category": by_category
    }

    # Leere Datenbank abfangen
    if df.empty: 
        return {
            "total_bookings": 0,
            "total_revenue": 0.0,
            "total_expenses": 0.0,
            "net_profit": 0.0,
            "paid_rate_pct": 0.0,
            "by_category": []
        }

    conn.close()
 
#    raise HTTPException(status_code=501, detail="Noch nicht implementiert")
