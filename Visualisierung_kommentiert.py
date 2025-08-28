# Importiere notwendige Bibliotheken
import streamlit as st                    # Für die Erstellung des interaktiven Web-Dashboards
import pandas as pd                      # Für Datenmanipulation und -analyse
import plotly.graph_objects as go        # Für interaktive Diagramme

# Konfiguration der Streamlit-Seite: Titel und Layout (z.B. breite Darstellung)
st.set_page_config(page_title="Journal Metrics Dashboard", layout="wide")
st.title("Journal Metrics Dashboard")  # Überschrift der Seite

# Daten laden mit Caching

# Diese Funktion lädt die Excel-Datei und speichert sie zwischengespeichert im Cache,
# damit sie beim erneuten Aufruf nicht erneut geladen wird.
@st.cache_data
def load_data():
    return pd.read_excel("tandfonline_journals_final.xlsx")

# Lade die Daten in einen DataFrame
df = load_data()

# Dynamisches Auswahlfeld für Journalnamen

# Ermittelt, welche Spalte die Journalnamen enthält
journal_col = "Zeitschrift" if "Zeitschrift" in df.columns else "URL"

# Extrahiere eindeutige Journalnamen (keine NaN-Werte)
journals = df[journal_col].dropna().unique()

# Streamlit-Auswahlbox zur Auswahl eines Journals
selected_journal = st.selectbox("Wähle ein Journal aus:", journals)

# Daten für das ausgewählte Journal anzeigen

# Filtert alle Zeilen für das ausgewählte Journal
filtered = df[df[journal_col] == selected_journal]

# Finde alle Spalten, die Durchschnittswerte in Tagen enthalten
days_avg_cols = [col for col in filtered.columns if "days avg" in col.lower()]

# Füllt fehlende Werte in diesen Spalten mit einem Platzhalter
filtered[days_avg_cols] = filtered[days_avg_cols].fillna("keine Werte")

# Hilfsfunktion, um Zahlen optisch schöner darzustellen (z.B. 152.0 → 152)
def clean_number(val):
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val

# Wendet diese Formatierung auf alle Zellen an
filtered = filtered.applymap(clean_number)

# Zeigt die gefilterten Daten als Tabelle in Streamlit an (ohne Scroll)
st.subheader(f"Daten für: {selected_journal}")
st.table(filtered.dropna(axis=1, how="all"))  # Entfernt leere Spalten

# Hilfsfunktion zur Umwandlung von Metrik-Werten in Zahlen

import re  # Für reguläre Ausdrücke

# Konvertiert Metrik-Werte (z. B. "15,6%", "n/a", etc.) in Float-Werte
def parse_metric(val):
    if isinstance(val, str):
        val = val.lower().strip()
        if val in ["n/a", "na", "-", "–", ""]:
            return None  # Ungültige Einträge ignorieren
        val = val.replace(",", ".")  # Deutsche Kommas durch Punkte ersetzen
        val = re.sub(r"[^0-9\.]", "", val)  # Entfernt alles außer Zahlen und Punkten
        try:
            return float(val)
        except:
            return None
    elif isinstance(val, (int, float)):
        return float(val)
    return None

# Funktion für interaktive Balkendiagramme

# Erstellt ein Balkendiagramm für eine bestimmte Metrik (z. B. "Impact Factor")
def plot_overview(metric_name, color):
    if metric_name in df.columns:
        # Entfernt Zeilen mit leeren Werten für die gewählte Metrik
        df_metric = df[[journal_col, metric_name]].dropna()

        # Konvertiert Metrik-Werte in Float-Zahlen
        df_metric[metric_name + "_float"] = df_metric[metric_name].apply(parse_metric)

        # Entfernt weiterhin ungültige Einträge
        df_metric = df_metric.dropna(subset=[metric_name + "_float"])
        
        # Falls nach der Filterung noch Daten vorhanden sind
        if not df_metric.empty:
            # Erzeuge ein interaktives Balkendiagramm mit Plotly
            fig = go.Figure(go.Bar(
                x=df_metric[journal_col],  # Journalnamen auf X-Achse
                y=df_metric[metric_name + "_float"],  # Metrikwerte auf Y-Achse
                marker_color=color,
                hovertemplate="%{x}: %{y:.2f}"  # Tooltip-Formatierung
            ))

            # Layout des Diagramms anpassen
            fig.update_layout(
                title=f"Gesamtübersicht: {metric_name}",
                yaxis_title=metric_name,
                xaxis_title="Journal",
                xaxis_tickangle=-45,  # X-Achsenbeschriftung schräg
                margin=dict(l=40, r=40, t=60, b=150),
                height=500
            )

            # Zeige das Diagramm in Streamlit an
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"ℹ️ Keine gültigen Daten für '{metric_name}'.")
    else:
        st.info(f"ℹ️ Spalte '{metric_name}' nicht in den Daten vorhanden.")

# Abschnitt: Gesamtübersicht

st.header("📈 Gesamtübersichten")

# Erstellt Diagramme für drei verschiedene Metriken
plot_overview("Impact Factor", "steelblue")
plot_overview("CiteScore (Scopus)", "seagreen")
plot_overview("acceptance rate", "indianred")
