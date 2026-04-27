import os
import re
import json
import hashlib
from datetime import date, datetime
from urllib.parse import urljoin

import pandas as pd
import requests
import streamlit as st
import pdfplumber
from openai import OpenAI

from bs4 import BeautifulSoup


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(page_title="Communio", page_icon="⛪", layout="wide")

PARISHES_URL = "https://www.diocesepb.org/parishes/parishes.html"
EVENTS_URL_TEMPLATE = "https://www.diocesepb.org/news/events.html/calendar/{year}/{month}"
EVENTS_DATA_FILE = "events_data.json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
.event-card {
    background-color: #17171d;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.9rem;
    border-left: 5px solid #d4a853;
}
.badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 999px;
    background: rgba(212,168,83,0.18);
    border: 1px solid rgba(212,168,83,0.35);
    margin-right: 5px;
    font-size: 0.8rem;
}
.small-muted {
    color: #bfbfbf;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

def clean_text(v):
    return re.sub(r"\s+", " ", v or "").strip()


def infer_category(title):
    t = (title or "").lower()

    if "mass" in t:
        return "Liturgy / Mass"
    if "adoration" in t:
        return "Adoration"
    if "confession" in t or "prayer" in t:
        return "Confession / Prayer"
    if "retreat" in t:
        return "Retreat"
    if "youth" in t:
        return "Youth / Young Adult"
    if "family" in t:
        return "Marriage / Family"
    if "service" in t or "charity" in t:
        return "Service / Charity"
    if "social" in t:
        return "Social / Fellowship"

    return "Adult Formation"


# ============================================================
# LOAD PARISHES
# ============================================================

@st.cache_data
def fetch_parishes():
    res = requests.get(PARISHES_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    names = []

    for line in soup.get_text("\n").split("\n"):
        line = clean_text(line)
        if line and not line.startswith("Next"):
            if any(word in line for word in ["St.", "Cathedral", "Holy", "Our Lady"]):
                names.append(line)

    return pd.DataFrame({"parish": sorted(set(names))})


# ============================================================
# LOAD EVENTS
# ============================================================

def load_events():
    if not os.path.exists(EVENTS_DATA_FILE):
        return pd.DataFrame()

    data = json.load(open(EVENTS_DATA_FILE))

    rows = []

    for parish, content in data.items():
        for e in content.get("events", []):
            rows.append(e)

    return pd.DataFrame(rows)


# ============================================================
# RENDER EVENT CARD (FIXED)
# ============================================================

def render_event_card(row):
    parish_badge = f"<span class='badge'>{row.get('parish','')}</span>"
    source_badge = f"<span class='badge'>{row.get('source','')}</span>"

    html = f"""
    <div class="event-card">
        <div class="small-muted">{row.get('date_label','')} · {row.get('time','')}</div>
        <div style="font-weight:700;font-size:1.1rem">{row.get('title','')}</div>
        <div class="small-muted">{row.get('description','')}</div>
        <br>
        <span class="badge">{row.get('category','')}</span>
        {parish_badge}
        {source_badge}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# AI EXTRACTION
# ============================================================

def extract_events(text, parish):
    if not OPENAI_API_KEY:
        st.error("Missing API key")
        return []

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"Extract events JSON from:\n{text[:8000]}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    try:
        events = json.loads(res.choices[0].message.content)
    except:
        return []

    for e in events:
        e["parish"] = parish
        e["source"] = "Bulletin Upload"
        e["id"] = hashlib.md5((e.get("title","")+parish).encode()).hexdigest()

    return events


# ============================================================
# SAVE EVENTS
# ============================================================

def save_events(parish, events):
    if os.path.exists(EVENTS_DATA_FILE):
        data = json.load(open(EVENTS_DATA_FILE))
    else:
        data = {}

    if parish not in data:
        data[parish] = {"events": []}

    data[parish]["events"].extend(events)

    json.dump(data, open(EVENTS_DATA_FILE, "w"), indent=2)


# ============================================================
# UI
# ============================================================

st.title("⛪ Communio")

view = st.sidebar.radio("View", ["Events", "Upload"])

# ============================================================
# EVENTS VIEW
# ============================================================

if view == "Events":
    df = load_events()

    if df.empty:
        st.info("No events yet.")
    else:
        for _, row in df.iterrows():
            render_event_card(row)


# ============================================================
# UPLOAD VIEW
# ============================================================

if view == "Upload":

    parish = st.text_input("Parish name")
    files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

    if st.button("Process"):

        total = 0

        for f in files:

            text = ""

            with pdfplumber.open(f) as pdf:
                for p in pdf.pages:
                    text += p.extract_text() or ""

            events = extract_events(text, parish)

            save_events(parish, events)

            total += len(events)

        st.success(f"Added {total} events")
