"""
FastAPI Buchungsverwaltung
===================================
Starten:     uvicorn main:app --reload
Swagger UI:  http://127.0.0.1:8000/docs
Redoc:       http://127.0.0.1:8000/redoc

"""
from typing import Optional
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from database import get_connection, init_db
from models import BookingCreate

init_db()   # ← plain sync function, no await needed

app = FastAPI(
    title="Buchungsverwaltung",
    version="1.0",
    description="Uebungs-API fuer das Semesterprojekt",
)

# =============================================================
# GET /bookings - kompletter Abschnitt aus der Uebung uebernommen
# =============================================================
@app.get("/bookings", tags=["Buchungen"], summary="Alle Buchungen abrufen")
def get_bookings(
    category: Optional[str] = Query(default=None, description="Filter nach Kategorie (z. B. 'Marketing')"),
    is_paid: Optional[bool] = Query(default=None, description="Filter nach Zahlungsstatus"),
):
    # Datenbankverbindung aufbauen
    conn = get_connection()

    # Filterfunktion aus der Uebung
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
    
    # Datenbankverbindung schliessen
    conn.close()
    return df.to_dict(orient="records")


# =============================================================
# POST /bookings - bis auf Zeilen 69,70 alles aus der Uebung uebernommen
# =============================================================
@app.post("/bookings", status_code=201, tags=["Buchungen"], summary="Neue Buchung erstellen")
def create_booking(booking: BookingCreate):
    # Datenbankverbindung aufbauen
    conn = get_connection()

    # neue Buchung erstellen
    df_new = pd.DataFrame([booking.model_dump()])
    df_new["is_paid"] = df_new["is_paid"].astype(int)   # bool → 0/1 fuer SQLite
    df_new.to_sql("buchungen", conn, if_exists="append", index=False)

    # Booking ID hinzufügen - Zeilen 72,73 mit ChatGPT erstellt 
    booking_id = conn.execute(
        "SELECT last_insert_rowid()").fetchone()[0] 

    # Datenbankverbindung schliessen    
    conn.commit()
    conn.close()
    return {"message": "Buchung erstellt",
        "booking_id": booking_id
        }


# =============================================================
#  GET /bookings/find?booking_id=... - kompletter Abschnitt aus der Uebung uebernommen
# =============================================================
@app.get("/bookings/find", tags=["Buchungen"], summary="Einzelne Buchung per Query-Parameter abrufen")
def get_booking_by_id(booking_id: int = Query(description="ID der gesuchten Buchung")):
   # Datenbankverbindung aufbauen
   conn = get_connection()

   # Buchung per Pandas laden
   df = pd.read_sql_query( "SELECT * FROM buchungen WHERE booking_id = ?",
    conn, params=[booking_id] )

   # Fehlermeldung wenn DataFrame leer
   if df.empty:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
   
   # Datenbankverbindung schliessen
   conn.close()
   return df.iloc[0].to_dict()
   

# =============================================================
#  PUT /bookings/{booking_id}/pay - kompletter Abschnitt aus der Uebung uebernommen
# =============================================================
@app.put("/bookings/{booking_id}/pay", tags=["Buchungen"], summary="Buchung als bezahlt markieren")
def mark_booking_paid(booking_id: int):
    # Datenbankverbindung aufbauen
    conn = get_connection()

    # Buchung laden
    df = pd.read_sql_query(
        "SELECT * FROM buchungen WHERE booking_id = ?",
        conn, params=[booking_id]
    )

    # Fehlermeldungen 
    if df.empty:
        raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
    if df.iloc[0]["is_paid"] == 1:
        raise HTTPException(status_code=400, detail="Buchung ist bereits als bezahlt markiert")
    
    # Buchung als bezahlt markieren
    conn.execute(
    "UPDATE buchungen SET is_paid = 1 WHERE booking_id = ?", 
    (booking_id,)
    )

    # Datenbankverbindung schliessen
    conn.commit()
    conn.close()
        

# =============================================================
# GET /stats - bis auf return wurde der komplette Abschnitt aus der Uebung uebernommen
# =============================================================
@app.get("/stats", tags=["Statistiken"], summary="Finanzstatistiken abrufen")
def get_stats():
    # Datenbankverbindung aufbauen
    conn = get_connection()

    # alle Buchungsdaten abrufen
    df = pd.read_sql_query("SELECT * FROM buchungen", conn)

    # Datenbankverbindung schliessen
    conn.close()

    # Wichige Werte berechnen und ggf. auf 2 Nachkommastellen runden
    total_bookings = len(df)
    total_revenue  = round(float(df[df["booking_type"] == "revenue"]["amount_net"].sum()), 2)
    total_expenses = round(float(df[df["booking_type"] == "expense"]["amount_net"].sum()), 2)
    net_profit     = round(total_revenue - total_expenses, 2)
    paid_rate_pct  = round(df["is_paid"].mean() * 100, 2) if total_bookings > 0 else 0.0

    # Ausgabe
    return {
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,     
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "paid_rate_pct": paid_rate_pct,
    }
    