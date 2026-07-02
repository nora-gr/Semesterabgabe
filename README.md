Semesterprojekt - ABV Programmieren für WiWiss


Gruppenmitglieder: Nora Grums

Beschreibung der Anwendung:
Dieses Programm wurde für den Kurs "ABV Programmieren für Wirtschaftswissenschaftler" als Semesterprojekt erstellt. Es handelt sich um ein Buchungssystem, das vorhandene Buchungen anzeigen und neue Buchungen erfassen kann. Außerdem können betriebswirtschaftliche Kennzahlen ausgegeben und in einem Diagramm dargestellt werden, sowie eine Bilanz zu einem gewünschten Stichtag ausgegeben werden. Außerdem hat die Anwendung eine Login-Funktion, um auf die Daten zugreifen zu können.
Das Programm besitzt ein Streamlit-Frontend, ein FastAPI-Backend und eine SQLite-Datenbank.


Projektaufbau:
Mein Projekt hat mehrere Bestandteile:
    1. seed.py - befüllt die Datenbank mit Beispieldaten
    2. models.py - Pydantic-Modelle zur Request-Validierung
    3. database.py - Datenbankhelfer, der die Datenbankverbindung verwaltet
    4. main.py - FastAPI-Backend, das neue Buchungen verarbeitet, speichert und Finanzstatistiken berechnen kann
    5. app.py - Streamlit-Frontend (d.h. die Benutzeroberfläche), mit Login-Funktion, Dashboard, Bilanzberechnung und Darstellung in einem Diagramm, Funktion zum Anlegen neuer Buchungen, Option nur für Admins einen neuen User hinzuzufügen


Kreative Erweiterung:
Als kreative Erweiterung habe ich, wie es in den Vorgaben vorgeschlagen wurde, ein Login-System mit Rollenverwaltung erstellt. Hier wird zwischen Admin und User unterschieden. Beide Akteuere können auf alle Grundfunktionen des Frontends zugreifen, der Admin kann zusätzlich aber noch neue User hinzufügen.
Außerdem habe ich noch ein Dashboard erstellt, das die betriebswirtschaftlichen Kennzahlen (Anzahl der Buchungen, Einnahmen, Ausgaben, Gewinn, Anteil der bezahlten Buchungen) der gesamten Buchungen übersichtlich darstellt.


Anleitung zum lokalen Starten der Anwendung:
1. Repository auf eigenen PC klonen
    git clone <Repository-URL>
    cd <Repository-Ordner>
2. uv synchronisieren
    uv sync
3. Beispieldaten laden
    uv run seed.py
4. Fast-API-Backend starten
    uv run uvicorn main:app --reload
    Dokumentation muss manuell geöffnet werden: http://127.0.0.1:8000/docs
5. Streamlit-Frontend starten (öffnet sich automatisch)
    uv run streamlit run app.py

Anmerkung:
Meine Kommentare zum Quellcode sind sehr detailiert verfasst. Das hat mir während des Programmierens sehr geholfen, um die einzelnen Code-Zeilen besser zu verstehen. Aus diesem Grund habe ich sie so ausführlich gelassen und vor der Abgabe nicht noch einmal gekürzt.


KI-Nutzung:
Ich habe für das Semesterprojekt lediglich ChatGPT als KI-Tool benutzt. Hauptsächlich habe ich es hierbei für das Debugging verwendet. So konnte ich Schwachstellen in meinem Programm schneller finden. Für die Ideenfindung brauchte ich kein KI-Tool, weil ich mich bei der kreativen Erweiterung an eins der vorgegebenen Beispielerweiterungen gehalten habe.  
Generell habe ich mich aber stark an unsere Übungen und Vorlesungsfolien gehalten, besonders bei der Strukturierung des Projekts.
Des Weiteren habe ich https://cheat-sheet.streamlit.app/ genutzt, das mir gezeigt hat, wie man st.columns und st.metrics benutzt.
Durch ChatGPT bin ich während des Debuggings auch auf den Befehl st.session_state[] gekommen, den ich besonders während des kreativen Teils oft genutzt habe. Mein Problem war zuerst, dass ich die neuen Login-Daten als normale Variablen erstellen konnten, diese aber nach dem rerun und Neuladen von Stream wieder gelöscht waren. Hier hat mir der neue Befehl deutlich geholfen. Jetzt bleiben die neuen Login-Daten im Speicher, auch wenn es zu einem rerun von Streamlit kommt. Es kommt aber leider immer noch dazu, dass diese Daten gelöscht werden, wenn man manuell die Anwendungsseite neu lädt.
Für bestimmte Code-Snippets habe ich ChatGPT genau an 4 Stellen benutzt, die ich auch im Quellcode deutlich gemacht habe. Ich liste sie aber trotzdem nochmal auf.
1.  In der main.py: booking_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0] 
    Hier kam ich leider nicht auf eine gute Lösung, wie man die Booking_IDs erstellen kann.
2.  In der app.py:  df_bilanz["booking_date"] = pd.to_datetime(df_bilanz["booking_date"])
                    df_bilanz = df_bilanz[df_bilanz["booking_date"] <= stichtag]
    Mein Problem war hier, dass die Dateiformate nicht zusammengepasst hatten und ich keinen guten Ansatz hatte, wie man die Datenpunkte nach dem Stichtagsdatum filtern kann.
3.  In der app.py: return pd.DataFrame()
    Beim Cache wurde während des Debuggings vorgeschlagen, dass man ein leeres DataFrame zurückgeben sollte, wenn es zu Fehlern kommt, weil sonst das Programm crashen könnte. Das erschien mir sinnvoll, deswegen habe ich es in mein Programm aufgenommen.
4.  In der app.py:  if "eingeloggt" not in st.session_state:
                    st.session_state["eingeloggt"] = False
    Der Login-Status musste initialisiert werden, bevor ich ihn nutzen konnte. Hier hatte ich keine guten Ansatz und konnte durch ChatGPT eine gute Lösung finden.
