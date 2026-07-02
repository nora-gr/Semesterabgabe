"""
Streamlit & API-Integration

Starten mit:
    uv run streamlit run app.py
"""
import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"

# =============================================================
# Cache, damit Streamlit nicht nach jeder Änderung neu lädt
# Grundaufbau aus der Uebung uebernommen, aber eigenstaendig except hinzugefuegt
# =============================================================
@st.cache_data()
def lade_buchungen():
    try:
        # alle Buchungen geben
        response = requests.get(f"{API_URL}/bookings")
        # Daten als DataFrame zurückgegeben
        return pd.DataFrame(response.json())
    except requests.exceptions.ConnectionError:
        st.error("Backend nicht erreichbar – ist der FastAPI-Server gestartet?")
        # leeres Dataframe wird zurueckgegeben, damit es zu keinen Crashs kommt - von ChatGPT vorgeschlagen 
        return pd.DataFrame()

# Hauptueberschrift
st.title("Semesterprojekt - Buchungssystem")


# =============================================================
# Zusatzfunktion - User-Login - eigenstaendig programmiert
# =============================================================
# Wenn User im Speicher noch nicht vorhanden, dann Dictionary für User anlegen und 2 Accounts speichern
if "users" not in st.session_state:
    st.session_state["users"] = [
        # Benutzeraccount 1
        {
        "user_id": 1,
        "username": "admin",
        "password": "1234",
        "rolle": "Admin"
    },
        # Benutzeraccount 2
        {
        "user_id": 2,
        "username": "user",
        "password": "5678",
        "rolle": "User"
    }    
    ]

# Login-Funktion 
def login():
    # Ueberschriften
    st.header("Login")
    st.markdown("**Bitte einloggen, um Daten einzusehen.**")

    # Eingabefelder (mit type, damit Passwort bei der Eingabe nicht zu sehen ist)
    username_input = st.text_input("Benutzername")
    password_input = st.text_input("Passwort", type = "password")

    # Lokale Variable fuer die Schleife
    eingeloggt = False

    # Wenn der Anmelde-Knopf gedrückt wurde
    if st.button("Jetzt anmelden."):
        # Komplettes Dictionary wird durchgegangen
        for user in st.session_state["users"]:
        # Wenn Anmeldedaten korrekt, dann einloggen.
            if username_input == user["username"] and password_input == user["password"]:
                # Eingeloggt, Username, Rolle werden gesichert, damit sie beim rerun nicht geloescht werden
                st.session_state["eingeloggt"] = True
                st.session_state["username"] = user["username"]
                st.session_state["rolle"] = user["rolle"] 
                # Lokale Variable zeigt an, dass Schleife beendet werden kann, wenn Anmeldedaten korrekt waren
                eingeloggt = True
                # Erfolgsmeldung
                st.success("Login erfolgreich!")
                # Programm wird nach dem Login neu gestartet
                st.rerun()
        # Wenn keine der Anmeldedaten gepasst hat, dann rote Fehlermeldung anzeigen.    
        if not eingeloggt:
                st.error("Der Benutzername oder das Passwort ist falsch.")


# Login-Status muss einmal initialisiert werden - Zeilen 90,91 mit ChatGPT erstellt
if "eingeloggt" not in st.session_state:
    st.session_state["eingeloggt"] = False


# Wenn man nicht eingeloggt ist, dann soll das Programm "login" laufen
if not st.session_state["eingeloggt"]:
    login()
    # die restlichen Daten sollen vor dem Login noch nicht angezeigt werden
    st.stop()

# Wenn man eingeloggt ist, dann wird noch ein neuer Button zum Abmelden hinzugefügt
if st.session_state["eingeloggt"]:
    if st.button("Abmelden"):
        st.session_state["eingeloggt"] = False
        # die restlichen Daten werden abgerufen
        st.rerun()


# =============================================================
# Buchungen laden
# =============================================================
df = lade_buchungen()
# Warnung, falls keine Buchungen vorhanden sind
if df.empty:
    st.warning("Keine Buchungen vorhanden") 

# =============================================================
# Visualisierung - Dashboard - eigenstaendig programmiert
# =============================================================
st.header("Dashboard")
# Statistik-Werte abfragen
stats = requests.get(f"{API_URL}/stats").json()
# Ausgabe der Daten nebeneinander
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Buchungen", f"{stats["total_bookings"]} Stk.")
with col2:
    st.metric("Einnahmen", f"{stats["total_revenue"]} €")
with col3:
    st.metric("Ausgaben", f"{stats["total_expenses"]} €")
with col4:
    st.metric("Gewinn", f"{stats["net_profit"]} €")
st.metric("Bezahlte Buchungen", f"{stats["paid_rate_pct"]} %")


# =============================================================
# Visualisierung - Bilanz zum Stichtag - eigenstaendig programmiert
# =============================================================
# Ueberschrift
st.header("Bilanz zu einem Stichtag")

# Stichtag wird als Text eingegeben und sofort als Datum umgewandelt
stichtag = pd.to_datetime(st.date_input("Bitte Stichtag auswählen."))

# Datensatz kopieren
df_bilanz = df.copy()
# nur Daten verweden, die ein Datum bis zum Stichtag besitzen - Zeilen 147,148 mit ChatGPT erstellt
df_bilanz["booking_date"] = pd.to_datetime(df_bilanz["booking_date"])
df_bilanz = df_bilanz[df_bilanz["booking_date"] <= stichtag]


# Berechnungen fuer die Bilanz - Gleiche Code-Logik wie in main.py GET /stats
einnahmen = round(float(df_bilanz[df_bilanz["booking_type"] == "revenue"]["amount_net"].sum()), 2)
ausgaben = round(float(df_bilanz[df_bilanz["booking_type"] == "expense"]["amount_net"].sum()), 2)
gewinn = einnahmen - ausgaben

# Ueberschrift
st.subheader(f"Bilanz zum Stichtag {stichtag}")

# Ausgabe der Daten nebeneinander
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Einnahmen", f"{einnahmen} €")
with col2:
    st.metric("Ausgaben", f"{ausgaben} €")
with col3:
    st.metric("Gewinn", f"{gewinn} €")

# Visualisierung der Daten in einem Balkendiagramm
st.subheader("Bilanzgrafik")
chart_data = ( pd.DataFrame(
    {
    "Bilanzposition": ["Einnahmen", "Ausgaben", "Gewinn"],
    "Betrag in €": [einnahmen, ausgaben, gewinn]
    }
)).set_index("Bilanzposition")
st.bar_chart(chart_data, color = "green")

# Beruecksichtigte Daten erneut in einer Tabelle anzeigen
st.subheader("Berücksichtigte Buchungen:")
st.dataframe(df_bilanz)


# =============================================================
# Neue Buchung erstellen - kompletter Abschnitt aus der Uebung uebernommen
# =============================================================
st.subheader("Neue Buchung erstellen")

with st.form("neue_buchung"):
    col1, col2 = st.columns(2)
    with col1:
        booking_date = st.date_input("Buchungsdatum")
        booking_type = st.selectbox("Typ", ["revenue", "expense"])
        category = st.text_input("Kategorie")
    with col2:
        partner_name = st.text_input("Geschäftspartner")
        amount_net = st.number_input("Betrag (netto)", min_value=0.01, step=0.01)
        currency = st.text_input("Währung", value="EUR")
        is_paid = st.checkbox("Bezahlt")

    submitted = st.form_submit_button("Buchung erstellen")

if submitted:
    buchung = {
        "booking_date": booking_date.isoformat(),
        "booking_type": booking_type,
        "category": category,
        "partner_name": partner_name,
        "amount_net": amount_net,
        "currency": currency,
        "is_paid": is_paid,
    }
    response = requests.post(f"{API_URL}/bookings", json=buchung)

    if response.status_code == 201:
        neue_id = response.json().get("booking_id")
        st.success(f"Buchung wurde gespeichert (ID: {neue_id})")
        # ergaenzt, damit neue Buchung sofort geladen wird
        st.rerun()  
    else:
        st.error(f"Fehler {response.status_code}: {response.json()}")


# =============================================================
# Aktuelle Daten anzeigen - kompletter Abschnitt aus der Uebung uebernommen
# =============================================================
st.subheader("Aktueller Datensatz")

try:
    response = requests.get(f"{API_URL}/bookings")
    df = pd.DataFrame(response.json())
    st.dataframe(df)
    st.write(f"Insgesamt {len(df)} Buchungen")
except requests.exceptions.ConnectionError:
    st.error("Backend nicht erreichbar – ist der FastAPI-Server gestartet?")

# =============================================================
# Zusatzfunktion - Logindaten fuer neuen User anlegen - eigenstaendig programmiert
# statt "users" wird st.session_state["users"] benutzt, damit die Daten beim Neuladen nicht geloescht werden
# =============================================================
if st.session_state["eingeloggt"]:
    # Darf nur der Admin ausfuehren
    if st.session_state["rolle"] == "Admin":
        st.subheader("Neuen User anlegen:")

        username_new = st.text_input("Benutzername")
        password_new = st.text_input("Passwort", type = "password")
        rolle_new = st.selectbox("Rolle", ["User", "Admin"])

        if st.button("Jetzt neuen User anlegen:"):
            user_id = len(st.session_state["users"]) + 1
            neuer_user = {
                "user_id": user_id,
                "username": username_new,
                "password": password_new,
                "rolle": rolle_new
            }
            st.session_state["users"].append(neuer_user)
            st.success(f"Benutzer '{username_new}' wurde angelegt.")
