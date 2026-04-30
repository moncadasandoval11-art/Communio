import os
import re
import hashlib
from datetime import datetime

import pandas as pd
import pdfplumber
import streamlit as st

# ============================================================
# CONFIG (UNCHANGED)
# ============================================================

st.set_page_config(page_title="Communio", page_icon="⛪", layout="wide")

BULLETIN_FOLDER = "bulletins"

# ============================================================
# KEEP ALL YOUR CSS + UI EXACTLY AS YOU HAD IT
# (DO NOT TOUCH YOUR DESIGN — leaving placeholder)
# ============================================================

# 👇 KEEP YOUR EXISTING CSS HERE (unchanged)
# st.markdown(""" your css """, unsafe_allow_html=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def make_event_id(parish, title, date_label, time_label):
    raw = f"{parish}-{title}-{date_label}-{time_label}"
    return hashlib.md5(raw.encode()).hexdigest()


# ============================================================
# 🔥 MASS EXTRACTION (NEW — CRITICAL FIX)
# ============================================================

def extract_mass_events(text, parish, source_file):
    events = []
    lines = [clean_text(l) for l in text.splitlines() if clean_text(l)]

    for line in lines:
        l = line.lower()

        # DAILY MASS
        if "daily mass" in l or "mon - fri" in l or "monday through friday" in l:
            matches = re.findall(r"\d{1,2}:\d{2}\s*(?:am|pm)", l)

            for time_str in matches:
                events.append({
                    "id": make_event_id(parish, f"Daily Mass {time_str}", "Weekdays", time_str),
                    "title": "Daily Mass",
                    "date_label": "Monday–Friday",
                    "time": time_str,
                    "parish": parish,
                    "category": "Liturgy / Mass",
                    "description": "Weekday Mass",
                    "source_file": source_file,
                })

        # VIGIL MASS
        if "vigil" in l:
            matches = re.findall(r"\d{1,2}:\d{2}\s*(?:am|pm)", l)

            for time_str in matches:
                events.append({
                    "id": make_event_id(parish, f"Vigil Mass {time_str}", "Saturday", time_str),
                    "title": "Saturday Vigil Mass",
                    "date_label": "Saturday",
                    "time": time_str,
                    "parish": parish,
                    "category": "Liturgy / Mass",
                    "description": "Sunday Vigil Mass",
                    "source_file": source_file,
                })

        # SUNDAY MASSES
        if "sunday" in l and "mass" in l:
            matches = re.findall(r"\d{1,2}:\d{2}\s*(?:am|pm)", l)

            for time_str in matches:
                events.append({
                    "id": make_event_id(parish, f"Sunday Mass {time_str}", "Sunday", time_str),
                    "title": "Sunday Mass",
                    "date_label": "Sunday",
                    "time": time_str,
                    "parish": parish,
                    "category": "Liturgy / Mass",
                    "description": "Sunday Mass",
                    "source_file": source_file,
                })

        # CONFESSION
        if "confession" in l:
            matches = re.findall(r"\d{1,2}:\d{2}\s*(?:am|pm)", l)

            for time_str in matches:
                events.append({
                    "id": make_event_id(parish, f"Confession {time_str}", "Weekly", time_str),
                    "title": "Confession",
                    "date_label": "Weekly",
                    "time": time_str,
                    "parish": parish,
                    "category": "Confession / Prayer",
                    "description": "Sacrament of Reconciliation",
                    "source_file": source_file,
                })

    return events


# ============================================================
# GENERAL EVENT DETECTION (YOUR OLD SYSTEM)
# ============================================================

def looks_like_event_line(line):
    keywords = [
        "study", "workshop", "meeting", "retreat", "youth",
        "bible", "rosary", "adoration", "gathering", "festival"
    ]
    text = line.lower()
    return any(k in text for k in keywords)


def extract_events_from_text(text, parish, source_file):
    events = []

    # 🔥 MASS EVENTS FIRST
    events.extend(extract_mass_events(text, parish, source_file))

    # NORMAL EVENTS
    lines = [clean_text(line) for line in text.splitlines() if clean_text(line)]

    for line in lines:
        if not looks_like_event_line(line):
            continue

        time_match = re.search(r"\d{1,2}:\d{2}\s*(am|pm)", line.lower())
        time_val = time_match.group(0) if time_match else "See bulletin"

        events.append({
            "id": make_event_id(parish, line, "See bulletin", time_val),
            "title": line[:100],
            "date_label": "See bulletin",
            "time": time_val,
            "parish": parish,
            "category": "Adult Formation",
            "description": line,
            "source_file": source_file,
        })

    return list({e["id"]: e for e in events}.values())


# ============================================================
# PDF LOADING
# ============================================================

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += "\n" + t
    return text


def infer_parish(filename):
    return filename.replace("_", " ").replace(".pdf", "")


@st.cache_data
def load_events():
    events = []

    if not os.path.exists(BULLETIN_FOLDER):
        return pd.DataFrame()

    for file in os.listdir(BULLETIN_FOLDER):
        if not file.endswith(".pdf"):
            continue

        path = os.path.join(BULLETIN_FOLDER, file)

        text = extract_text_from_pdf(path)
        parish = infer_parish(file)

        extracted = extract_events_from_text(text, parish, file)
        events.extend(extracted)

    if not events:
        return pd.DataFrame()

    return pd.DataFrame(events)


# ============================================================
# LOAD DATA
# ============================================================

df = load_events()

# ============================================================
# 🔍 FIND EVENTS GUI (UNCHANGED)
# ============================================================

st.header("Find an Event")

category = st.selectbox("Category", ["All"] + sorted(df["category"].dropna().unique().tolist()) if not df.empty else ["All"])
parish = st.selectbox("Parish", ["All"] + sorted(df["parish"].dropna().unique().tolist()) if not df.empty else ["All"])
search = st.text_input("Search")

filtered = df.copy()

if not df.empty:
    if category != "All":
        filtered = filtered[filtered["category"] == category]

    if parish != "All":
        filtered = filtered[filtered["parish"] == parish]

    if search:
        filtered = filtered[
            filtered.apply(
                lambda r: search.lower() in str(r.values).lower(),
                axis=1
            )
        ]

# ============================================================
# DISPLAY EVENTS (UNCHANGED STYLE)
# ============================================================

if filtered.empty:
    st.warning("No events found")
else:
    for _, row in filtered.iterrows():
        st.write(f"**{row['title']}**")
        st.write(f"{row['date_label']} • {row['time']}")
        st.write(f"{row['parish']} • {row['category']}")
        st.write("---")
