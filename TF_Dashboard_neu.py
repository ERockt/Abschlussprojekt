import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Journal Metrics Dashboard", layout="wide")
st.title("📊 Journal Metrics Dashboard")

# -------------------------------
# Daten laden mit Caching
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("tandfonline_journals_seleniumAll.xlsx")

df = load_data()

# Dynamisch bestimmen, welche Spalte für Journalnamen genutzt wird
journal_col = "Zeitschrift" if "Zeitschrift" in df.columns else "URL"
journals = df[journal_col].dropna().unique()
selected_journal = st.selectbox("Wähle ein Journal aus:", journals)

# -------------------------------
# Daten für ausgewähltes Journal anzeigen (ohne Scroll)
# -------------------------------

# Daten für ausgewähltes Journal
filtered = df[df[journal_col] == selected_journal]

# "days avg."-Spalten gezielt behandeln
days_avg_cols = [col for col in filtered.columns if "days avg" in col.lower()]
filtered[days_avg_cols] = filtered[days_avg_cols].fillna("keine Werte")

# Zahlen wie 152.0000 schöner anzeigen
def clean_number(val):
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val

filtered = filtered.applymap(clean_number)

# Darstellung ohne Scrollen
st.subheader(f"Daten für: {selected_journal}")
st.table(filtered.dropna(axis=1, how="all"))


# -------------------------------
# Hilfsfunktion zur Umwandlung von Metrik-Werten
# -------------------------------
import re

def parse_metric(val):
    if isinstance(val, str):
        val = val.lower().strip()
        if val in ["n/a", "na", "-", "–", ""]:
            return None
        val = val.replace(",", ".")  # Komma zu Punkt
        val = re.sub(r"[^0-9\.]", "", val)  # Entfernt alles außer Ziffern und Punkt
        try:
            return float(val)
        except:
            return None
    elif isinstance(val, (int, float)):
        return float(val)
    return None


# -------------------------------
# Funktion für Balkendiagramm einer Metrik
# -------------------------------
def plot_overview(metric_name, color):
    if metric_name in df.columns:
        df_metric = df[[journal_col, metric_name]].dropna()
        df_metric[metric_name + "_float"] = df_metric[metric_name].apply(parse_metric)
        df_metric = df_metric.dropna(subset=[metric_name + "_float"])
        
        if not df_metric.empty:
            fig = go.Figure(go.Bar(
                x=df_metric[journal_col],
                y=df_metric[metric_name + "_float"],
                marker_color=color,
                hovertemplate="%{x}: %{y:.2f}"
            ))
            fig.update_layout(
                title=f"Gesamtübersicht: {metric_name}",
                yaxis_title=metric_name,
                xaxis_title="Journal",
                xaxis_tickangle=-45,
                margin=dict(l=40, r=40, t=60, b=150),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"ℹ️ Keine gültigen Daten für '{metric_name}'.")
    else:
        st.info(f"ℹ️ Spalte '{metric_name}' nicht in den Daten vorhanden.")

# -------------------------------
# Gesamtübersichten anzeigen
# -------------------------------
st.header("📈 Gesamtübersichten")

plot_overview("Impact Factor", "steelblue")
plot_overview("CiteScore", "seagreen")
plot_overview("Acceptance Rate", "indianred")

