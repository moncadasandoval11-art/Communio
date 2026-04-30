import os
import re
import hashlib
from datetime import datetime

import pandas as pd
import pdfplumber
import streamlit as st


# ============================================================
# BASIC SETUP
# ============================================================

st.set_page_config(
    page_title="Communio",
    page_icon="⛪",
    layout="wide"
)

BULLETIN_FOLDER = "bulletins"


# ============================================================
# BEACHY PALM BEACH CATHOLIC STYLE
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eaf8fb 0%, #fffdf7 55%, #d7f1f6 100%);
}

.main-title {
    font-size: 3.3rem;
    font-weight: 900;
    color: #073b4c;
    letter-spacing: 0.08em;
}

.subtitle {
    color: #3f6473;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
}

.logo-box {
    width: 84px;
    height: 84px;
    border-radius: 22px;
    background: linear-gradient(135deg, #087e8b, #5ac8d8, #f5e6b8);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.3rem;
    color: white;
    font-weight: 800;
    box-shadow: 0 10px 25px rgba(7, 59, 76, 0.22);
}

.hero-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(8,126,139,0.18);
    border-radius: 26px;
    padding: 1.5rem;
    box-shadow: 0 14px 35px rgba(7,59,76,0.10);
}

.quick-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-top: 20px;
}

.quick-card {
    background: linear-gradient(135deg, #073b4c, #087e8b);
    padding: 20px;
    border-radius: 18px;
    color: white;
    box-shadow: 0 12px 28px rgba(7,59,76,0.18);
}

.quick-card a {
    color: white !important;
    font-weight: 800;
    font-size: 1.05rem;
    text-decoration: none;
}

.quick-card p {
    color: #e9fbff;
    margin-top: 0.45rem;
}

.bishop-card {
    display: flex;
    gap: 22px;
    align-items: center;
    margin-top: 24px;
    background: linear-gradient(135deg, #ffffff, #e6f8fb);
    border: 1px solid rgba(8,126,139,0.18);
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 12px 28px rgba(7,59,76,0.10);
}

.bishop-img {
    width: 150px;
    border-radius: 20px;
    box-shadow: 0 10px 24px rgba(7,59,76,0.22);
}

.bishop-kicker {
    color: #087e8b;
    text-transform: uppercase;
    font-size: 0.82rem;
    font-weight: 900;
    letter-spacing: 0.12em;
}

.bishop-quote {
    color: #173f4c;
    font-size: 1.05rem;
    line-height: 1.55;
    margin-top: 0.4rem;
}

.event-card {
    background: rgba(255,255,255,0.94);
    padding: 18px;
    border-radius: 18px;
    border-left: 6px solid #087e8b;
    margin-bottom: 14px;
    box-shadow: 0 8px 20px rgba(7,59,76,0.08);
}

.event-title {
    color: #073b4c;
    font-weight: 850;
    font-size: 1.15rem;
}

.event-meta {
    color: #4f6f7a;
    font-size: 0.95rem;
    margin-top: 0.2rem;
}

.badge {
    display: inline-block;
    background: #dff6f8;
    color: #075763;
    border: 1px solid #bfe9ee;
    padding: 0.22rem 0.58rem;
    border-radius: 999px;
    font-size: 0.78rem;
    margin-right: 0.3rem;
    margin-top: 0.45rem;
}

.slide-box {
    background: linear-gradient(135deg, #073b4c, #087e8b, #39b8c8);
    color: white;
    padding: 28px;
    border-radius: 24px;
    margin-top: 16px;
    box-shadow: 0 14px 35px rgba(7,59,76,0.20);
}

.slide-title {
    font-size: 1.55rem;
    font-weight: 900;
}

.small-muted {
    color: #5f7c86;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# PARISH DIRECTORY
# ============================================================

PARISHES = [
    {"parish": "Saint Sebastian", "city": "Sebastian", "deanery": "Northern Deanery"},
    {"parish": "Our Lady of Guadalupe Mission", "city": "Fellsmere", "deanery": "Northern Deanery"},
    {"parish": "Holy Cross", "city": "Vero Beach", "deanery": "Northern Deanery"},
    {"parish": "Saint Helen", "city": "Vero Beach", "deanery": "Northern Deanery"},
    {"parish": "Saint John of the Cross", "city": "Vero Beach", "deanery": "Northern Deanery"},
    {"parish": "Notre Dame Catholic Mission", "city": "Fort Pierce", "deanery": "Northern Deanery"},
    {"parish": "Saint Anastasia", "city": "Fort Pierce", "deanery": "Northern Deanery"},
    {"parish": "San Juan Diego Hispanic Pastoral Center", "city": "Fort Pierce", "deanery": "Northern Deanery"},
    {"parish": "Saint Mark the Evangelist", "city": "Fort Pierce", "deanery": "Northern Deanery"},
    {"parish": "Holy Family", "city": "Port St. Lucie", "deanery": "Northern Deanery"},
    {"parish": "Saint Lucie", "city": "Port St. Lucie", "deanery": "Northern Deanery"},
    {"parish": "Saint Elizabeth Ann Seton", "city": "Port St. Lucie", "deanery": "Northern Deanery"},
    {"parish": "Saint Bernadette", "city": "Port St. Lucie", "deanery": "Northern Deanery"},
    {"parish": "Sacred Heart", "city": "Okeechobee", "deanery": "Northern Deanery"},

    {"parish": "Saint Martin de Porres", "city": "Jensen Beach", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Joseph", "city": "Stuart", "deanery": "Cathedral Deanery"},
    {"parish": "Holy Redeemer", "city": "Palm City", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Andrew", "city": "Stuart", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Christopher", "city": "Hobe Sound", "deanery": "Cathedral Deanery"},
    {"parish": "Holy Cross", "city": "Indiantown", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Jude", "city": "Tequesta", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Peter", "city": "Jupiter", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Patrick", "city": "Palm Beach Gardens", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Paul of the Cross", "city": "North Palm Beach", "deanery": "Cathedral Deanery"},
    {"parish": "Cathedral of Saint Ignatius Loyola", "city": "Palm Beach Gardens", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Clare", "city": "North Palm Beach", "deanery": "Cathedral Deanery"},
    {"parish": "Saint Francis of Assisi", "city": "Riviera Beach", "deanery": "Cathedral Deanery"},
    {"parish": "Saint John Fisher", "city": "West Palm Beach", "deanery": "Cathedral Deanery"},

    {"parish": "Mary Immaculate", "city": "West Palm Beach", "deanery": "Central Deanery"},
    {"parish": "Basilica of Saint Edward", "city": "Palm Beach", "deanery": "Central Deanery"},
    {"parish": "Saint Ann", "city": "West Palm Beach", "deanery": "Central Deanery"},
    {"parish": "Our Lady Queen of Apostles", "city": "Royal Palm Beach", "deanery": "Central Deanery"},
    {"parish": "Saint Rita", "city": "Wellington", "deanery": "Central Deanery"},
    {"parish": "Saint Therese de Lisieux", "city": "Wellington", "deanery": "Central Deanery"},
    {"parish": "Saint Mary", "city": "Pahokee", "deanery": "Central Deanery"},
    {"parish": "Saint Philip Benizi", "city": "Belle Glade", "deanery": "Central Deanery"},
    {"parish": "Holy Name of Jesus", "city": "West Palm Beach", "deanery": "Central Deanery"},
    {"parish": "Saint Juliana", "city": "West Palm Beach", "deanery": "Central Deanery"},
    {"parish": "Saint Luke", "city": "Palm Springs", "deanery": "Central Deanery"},
    {"parish": "Sacred Heart", "city": "Lake Worth", "deanery": "Central Deanery"},
    {"parish": "Holy Spirit", "city": "Lantana", "deanery": "Central Deanery"},
    {"parish": "Saint Matthew", "city": "Lantana", "deanery": "Central Deanery"},

    {"parish": "Saint Mark", "city": "Boynton Beach", "deanery": "Southern Deanery"},
    {"parish": "Saint Thomas More", "city": "Boynton Beach", "deanery": "Southern Deanery"},
    {"parish": "Emmanuel", "city": "Delray Beach", "deanery": "Southern Deanery"},
    {"parish": "Saint Vincent Ferrer", "city": "Delray Beach", "deanery": "Southern Deanery"},
    {"parish": "Our Lady of Perpetual Help Mission", "city": "Delray Beach", "deanery": "Southern Deanery"},
    {"parish": "Our Lady Queen of Peace", "city": "Delray Beach", "deanery": "Southern Deanery"},
    {"parish": "Saint Lucy", "city": "Highland Beach", "deanery": "Southern Deanery"},
    {"parish": "Ascension", "city": "Boca Raton", "deanery": "Southern Deanery"},
    {"parish": "Saint Joan of Arc", "city": "Boca Raton", "deanery": "Southern Deanery"},
    {"parish": "Saint Jude", "city": "Boca Raton", "deanery": "Southern Deanery"},
    {"parish": "Our Lady of Lourdes", "city": "Boca Raton", "deanery": "Southern Deanery"},
    {"parish": "Saint John the Evangelist", "city": "Boca Raton", "deanery": "Southern Deanery"},
]

parish_df = pd.DataFrame(PARISHES)


# ============================================================
# EVENT CATEGORIES
# ============================================================

CATEGORY_OPTIONS = [
    "Liturgy / Mass",
    "Confession / Prayer",
    "Adoration",
    "Retreat",
    "Youth / Young Adult",
    "Marriage / Family",
    "School / Open House",
    "Service / Charity",
    "Adult Formation",
    "Social / Fellowship",
    "Holiday / Holy Day",
    "Ministry / Volunteer",
    "Fundraiser",
    "Other",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def normalize(text):
    text = clean_text(text).lower()
    text = text.replace("saint", "st")
    text = text.replace(".", "")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def infer_parish_from_filename(filename):
    name = normalize(filename)

    best_match = ""
    best_score = 0

    for parish in parish_df["parish"]:
        parish_norm = normalize(parish)
        words = parish_norm.split()
        score = sum(1 for word in words if word in name)

        if score > best_score:
            best_score = score
            best_match = parish

    if best_score >= 2:
        return best_match

    return "Unknown Parish"


def infer_category(title, description=""):
    text = normalize(title + " " + description)

    if any(w in text for w in ["mass", "eucharist", "first communion", "communion", "vigil", "liturgy"]):
        return "Liturgy / Mass"

    if any(w in text for w in ["confession", "rosary", "novena", "prayer", "stations", "divine mercy"]):
        return "Confession / Prayer"

    if "adoration" in text or "blessed sacrament" in text:
        return "Adoration"

    if "retreat" in text:
        return "Retreat"

    if any(w in text for w in ["youth", "young adult", "world youth day", "teen"]):
        return "Youth / Young Adult"

    if any(w in text for w in ["marriage", "couple", "pareja", "family", "families", "matrimonial"]):
        return "Marriage / Family"

    if any(w in text for w in ["school", "academy", "open house"]):
        return "School / Open House"

    if any(w in text for w in ["pantry", "food", "charity", "donation", "outreach", "homeless", "drive", "service"]):
        return "Service / Charity"

    if any(w in text for w in ["bible study", "faith formation", "study", "formation", "catechism", "oica", "rcia", "speaker", "workshop"]):
        return "Adult Formation"

    if any(w in text for w in ["social", "fellowship", "luncheon", "gathering", "festival", "guild", "coffee"]):
        return "Social / Fellowship"

    if any(w in text for w in ["easter", "christmas", "advent", "lent", "holy day", "pentecost"]):
        return "Holiday / Holy Day"

    if any(w in text for w in ["minister", "volunteer", "lector", "usher", "ministry"]):
        return "Ministry / Volunteer"

    if any(w in text for w in ["fundraiser", "sale", "raffle", "treasures"]):
        return "Fundraiser"

    return "Other"


def extract_text_from_pdf(pdf_path):
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += "\n" + page_text
    except Exception as e:
        st.warning(f"Could not read {pdf_path}: {e}")

    return text


def find_date_near_line(line, context):
    date_patterns = [
        r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}",
        r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+[A-Z][a-z]+\s+\d{1,2}",
        r"[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}",
        r"[A-Z][a-z]+\s+\d{1,2}(st|nd|rd|th)?",
        r"\d{1,2}/\d{1,2}/\d{2,4}",
    ]

    combined = line + " " + context

    for pattern in date_patterns:
        match = re.search(pattern, combined)
        if match:
            return clean_text(match.group(0))

    return ""


def find_time_near_line(line, context):
    time_patterns = [
        r"\d{1,2}:\d{2}\s*(am|pm|AM|PM)\s*[-–]\s*\d{1,2}:\d{2}\s*(am|pm|AM|PM)",
        r"\d{1,2}\s*(am|pm|AM|PM)\s*[-–]\s*\d{1,2}\s*(am|pm|AM|PM)",
        r"\d{1,2}:\d{2}\s*(am|pm|AM|PM)",
        r"\d{1,2}\s*(am|pm|AM|PM)",
    ]

    combined = line + " " + context

    for pattern in time_patterns:
        match = re.search(pattern, combined)
        if match:
            return clean_text(match.group(0))

    return ""


def looks_like_event_line(line):
    text = normalize(line)

    event_keywords = [
        "workshop", "gathering", "study", "bible", "rosary", "novena",
        "adoration", "revival", "retreat", "youth", "world youth day",
        "luncheon", "meeting", "guild", "ministry", "volunteer",
        "first communion", "confirmation", "mass", "confession",
        "prayer", "festival", "fundraiser", "sale", "speaker",
        "formation", "oica", "rcia", "carmelite", "knights of columbus",
        "columbiettes", "legion of mary", "parents", "pareja",
        "marriage", "food pantry", "outreach"
    ]

    has_keyword = any(keyword in text for keyword in event_keywords)
    has_time = bool(re.search(r"\d{1,2}(:\d{2})?\s*(am|pm)", text))
    has_date_word = any(day in text for day in [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "may", "june", "july", "august", "september", "october", "november", "december",
        "january", "february", "march", "april"
    ])

    if has_keyword and (has_time or has_date_word):
        return True

    if has_keyword and len(line) < 140:
        return True

    return False


def make_event_id(parish, title, date_label, time_label):
    raw = f"{parish}-{title}-{date_label}-{time_label}"
    return hashlib.md5(raw.encode()).hexdigest()


def extract_events_from_text(text, parish, source_file):
    lines = [clean_text(line) for line in text.splitlines() if clean_text(line)]

    events = []

    for i, line in enumerate(lines):
        if not looks_like_event_line(line):
            continue

        previous_line = lines[i - 1] if i > 0 else ""
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        second_next_line = lines[i + 2] if i + 2 < len(lines) else ""

        context = " ".join([previous_line, next_line, second_next_line])

        title = line

        if len(title) > 110:
            title = title[:110] + "..."

        date_label = find_date_near_line(line, context)
        time_label = find_time_near_line(line, context)

        description = clean_text(" ".join([line, next_line, second_next_line]))
        category = infer_category(title, description)

        event = {
            "id": make_event_id(parish, title, date_label, time_label),
            "title": title,
            "date_label": date_label if date_label else "See bulletin",
            "time": time_label if time_label else "See bulletin",
            "parish": parish,
            "category": category,
            "description": description,
            "source_file": source_file,
        }

        events.append(event)

    unique = {}
    for event in events:
        unique[event["id"]] = event

    return list(unique.values())


@st.cache_data(show_spinner=True)
def load_events_from_bulletins():
    all_events = []

    if not os.path.exists(BULLETIN_FOLDER):
        os.makedirs(BULLETIN_FOLDER, exist_ok=True)
        return pd.DataFrame(columns=[
            "id", "title", "date_label", "time", "parish",
            "category", "description", "source_file"
        ])

    pdf_files = [
        file for file in os.listdir(BULLETIN_FOLDER)
        if file.lower().endswith(".pdf")
    ]

    for file in pdf_files:
        pdf_path = os.path.join(BULLETIN_FOLDER, file)
        parish = infer_parish_from_filename(file)
        text = extract_text_from_pdf(pdf_path)
        events = extract_events_from_text(text, parish, file)
        all_events.extend(events)

    if not all_events:
        return pd.DataFrame(columns=[
            "id", "title", "date_label", "time", "parish",
            "category", "description", "source_file"
        ])

    return pd.DataFrame(all_events)


# ============================================================
# OPTIONAL SEED EVENTS
# These make the app look populated even before you upload PDFs.
# You can delete these later if you want.
# ============================================================

seed_events = pd.DataFrame([
    {
        "id": "seed-1",
        "title": "Final Guild Gathering and May Crowning",
        "date_label": "May 6, 2026",
        "time": "11:00 AM",
        "parish": "Basilica of Saint Edward",
        "category": "Social / Fellowship",
        "description": "Final Guild gathering with May procession, Crowning of the Blessed Mother, music, and luncheon.",
        "source_file": "Seeded from bulletin",
    },
    {
        "id": "seed-2",
        "title": "Extraordinary Ministers of Holy Communion Workshop",
        "date_label": "May 23, 2026",
        "time": "9:00 AM - 11:45 AM",
        "parish": "Holy Name of Jesus",
        "category": "Ministry / Volunteer",
        "description": "Workshop for existing Eucharistic Ministers and anyone wishing to become a new Eucharistic Minister.",
        "source_file": "Seeded from bulletin",
    },
    {
        "id": "seed-3",
        "title": "Unbound Revival Fire",
        "date_label": "May 24, 2026",
        "time": "5:00 PM - 8:00 PM",
        "parish": "Holy Name of Jesus",
        "category": "Confession / Prayer",
        "description": "Holy Mass, praise and worship, Eucharistic adoration, and laying on of hands.",
        "source_file": "Seeded from bulletin",
    },
    {
        "id": "seed-4",
        "title": "Mid-Morning Bible Study",
        "date_label": "Every Wednesday",
        "time": "10:00 AM - 12:00 PM",
        "parish": "Holy Name of Jesus",
        "category": "Adult Formation",
        "description": "Weekly Bible study using videos, Scripture, and the Catechism of the Catholic Church.",
        "source_file": "Seeded from bulletin",
    },
])


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns([0.08, 0.92])

with header_left:
    st.markdown('<div class="logo-box">✛</div>', unsafe_allow_html=True)

with header_right:
    st.markdown('<div class="main-title">COMMUNIO</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">A coastal Catholic guide to parish life across the Diocese of Palm Beach.</div>',
        unsafe_allow_html=True
    )


# ============================================================
# HERO / QUICK LINKS / BISHOP SECTION
# ============================================================

st.markdown('<div class="hero-card">', unsafe_allow_html=True)

st.markdown("""
<div class="quick-grid">
    <div class="quick-card">
        <a href="https://www.diocesepb.org/" target="_blank">Diocese Website</a>
        <p>Official diocesan homepage, ministries, news, and resources.</p>
    </div>
    <div class="quick-card">
        <a href="https://www.diocesepb.org/news/events.html" target="_blank">Diocesan Calendar</a>
        <p>Quick jump to official diocesan events.</p>
    </div>
    <div class="quick-card">
        <a href="https://www.diocesepb.org/about-us/office-of-the-bishop.html" target="_blank">Office of the Bishop</a>
        <p>Pastoral updates, diocesan leadership, and messages from the bishop.</p>
    </div>
</div>
""", unsafe_allow_html=True)

bishop_image_path = "Headshot2-Chosen-FrRodriguez.jpg.webp"

if os.path.exists(bishop_image_path):
    import base64
    with open(bishop_image_path, "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()

    img_html = f"data:image/webp;base64,{encoded_img}"
else:
    img_html = ""

st.markdown(f"""
<div class="bishop-card">
    {'<img class="bishop-img" src="' + img_html + '">' if img_html else ''}
    <div>
        <div class="bishop-kicker">Welcome from the Bishop</div>
        <div class="bishop-quote">
            Dear brothers and sisters in Christ,<br><br>
            How beautiful is our Church! How beautiful it is to walk in the path of Christ Jesus
            in the company of so many beloved brothers and sisters! How beautiful is the Diocese of Palm Beach!
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# LOAD EVENTS
# ============================================================

pdf_events = load_events_from_bulletins()
events_df = pd.concat([seed_events, pdf_events], ignore_index=True)

if not events_df.empty:
    events_df = events_df.drop_duplicates(subset=["id"])


# ============================================================
# FEATURED EVENT SLIDESHOW-LIKE SECTION
# ============================================================

st.markdown("## Featured Parish Life")

featured_events = events_df.head(5)

if featured_events.empty:
    st.info("Upload PDFs into the `bulletins/` folder on GitHub, then redeploy the app.")
else:
    featured_index = int(datetime.now().timestamp() / 5) % len(featured_events)
    featured = featured_events.iloc[featured_index]

    st.markdown(f"""
    <div class="slide-box">
        <div class="slide-title">{featured['title']}</div>
        <p>{featured['date_label']} • {featured['time']}</p>
        <p>{featured['parish']} · {featured['category']}</p>
        <p>{featured['description']}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FIND AN EVENT GUI
# ============================================================

st.markdown("## Find an Event")

filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1.4])

with filter_col1:
    selected_category = st.selectbox(
        "Event type",
        ["All"] + CATEGORY_OPTIONS
    )

with filter_col2:
    parish_options = ["All"] + sorted(events_df["parish"].dropna().unique().tolist())
    selected_parish = st.selectbox(
        "Parish",
        parish_options
    )

with filter_col3:
    search_query = st.text_input(
        "Search by keyword",
        placeholder="Try: rosary, youth, Bible study, adoration..."
    )


filtered_df = events_df.copy()

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if selected_parish != "All":
    filtered_df = filtered_df[filtered_df["parish"] == selected_parish]

if search_query.strip():
    q = search_query.lower().strip()

    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: q in " ".join([
                str(row.get("title", "")),
                str(row.get("description", "")),
                str(row.get("parish", "")),
                str(row.get("category", "")),
                str(row.get("date_label", "")),
                str(row.get("time", "")),
            ]).lower(),
            axis=1
        )
    ]


st.markdown(f"### {len(filtered_df)} event(s) found")

if filtered_df.empty:
    st.warning("No events matched your filters.")
else:
    for _, row in filtered_df.iterrows():
        st.markdown(f"""
        <div class="event-card">
            <div class="event-title">{row['title']}</div>
            <div class="event-meta">{row['date_label']} • {row['time']}</div>
            <span class="badge">{row['category']}</span>
            <span class="badge">{row['parish']}</span>
            <p style="margin-top:0.75rem;color:#244b58;">{row['description']}</p>
            <div class="small-muted">Source: {row['source_file']}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# PDF STATUS / ADMIN INFO
# ============================================================

with st.expander("PDF bulletin status"):
    if not os.path.exists(BULLETIN_FOLDER):
        st.write("No `bulletins/` folder found yet.")
    else:
        pdf_files = [f for f in os.listdir(BULLETIN_FOLDER) if f.lower().endswith(".pdf")]

        if not pdf_files:
            st.write("No PDFs found in the `bulletins/` folder.")
        else:
            st.write(f"Found {len(pdf_files)} PDF bulletin(s):")
            for file in pdf_files:
                st.write(f"- {file}")

    st.markdown("""
    **How to add more bulletins:**

    1. In GitHub, create a folder named `bulletins`.
    2. Upload bulletin PDFs into that folder.
    3. Name them clearly, for example:
       - `Holy_Name_of_Jesus_2026_05_03.pdf`
       - `Basilica_of_Saint_Edward_2026_04_26.pdf`
       - `Saint_Thomas_More_2026_04.pdf`
    4. Redeploy or reboot Streamlit.
    """)
