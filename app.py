import os
import re
import hashlib
from datetime import datetime
from urllib.parse import quote_plus

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
.detail-card {
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(8,126,139,0.18);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 12px 28px rgba(7,59,76,0.10);
    margin-top: 20px;
}

.detail-title {
    color: #073b4c;
    font-size: 2rem;
    font-weight: 900;
    margin-bottom: 0.25rem;
}

.detail-map {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid rgba(8,126,139,0.18);
    box-shadow: 0 10px 24px rgba(7,59,76,0.12);
}

.stButton > button {
    border-radius: 999px;
    border: 1px solid rgba(8,126,139,0.35);
    background: linear-gradient(135deg, #087e8b, #39b8c8);
    color: white;
    font-weight: 800;
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
# EVENT DETAIL PAGE HELPERS
# ============================================================

def get_parish_info(parish_name):
    matches = parish_df[parish_df["parish"] == parish_name]
    if matches.empty:
        return {"parish": parish_name, "city": "", "deanery": ""}
    return matches.iloc[0].to_dict()


def detect_event_language(text):
    low = normalize(text)

    spanish_words = [
        "espanol", "español", "misa en espanol", "misa en español", "sabado",
        "sábado", "domingo", "jueves", "viernes", "miercoles", "miércoles",
        "confesiones", "adoracion", "adoración", "parejas", "matrimonial",
        "rosario", "oracion", "oración", "comunion", "comunión"
    ]

    haitian_creole_words = [
        "haitian", "creole", "kreyol", "créole", "lekty", "lekti", "semèn", "ayisyen"
    ]

    if any(word in low for word in spanish_words):
        return "Spanish / Español"
    if any(word in low for word in haitian_creole_words):
        return "Haitian Creole"
    return "Not specified"


def build_event_summary(row):
    title = clean_text(row.get("title", "Event"))
    parish = clean_text(row.get("parish", "the parish"))
    category = clean_text(row.get("category", "event"))
    date_label = clean_text(row.get("date_label", "See bulletin"))
    time_label = clean_text(row.get("time", "See bulletin"))
    description = clean_text(row.get("description", ""))
    language = detect_event_language(" ".join([title, description, category]))

    if description and description.lower() not in {"see bulletin", ""}:
        sentence = description
    else:
        sentence = f"{title} is listed in the parish bulletin as a {category.lower()} event."

    extra = ""
    if language != "Not specified":
        extra = f" The bulletin text suggests this event may be in {language}."

    return f"{sentence} This listing is for {parish}, scheduled for {date_label} at {time_label}.{extra}"


def render_event_detail_page(event_row):
    parish_name = clean_text(event_row.get("parish", ""))
    parish_info = get_parish_info(parish_name)
    city = clean_text(parish_info.get("city", ""))
    deanery = clean_text(parish_info.get("deanery", ""))
    category = clean_text(event_row.get("category", ""))
    title = clean_text(event_row.get("title", "Event Detail"))
    date_label = clean_text(event_row.get("date_label", "See bulletin"))
    time_label = clean_text(event_row.get("time", "See bulletin"))
    source_file = clean_text(event_row.get("source_file", ""))
    description = build_event_summary(event_row)
    language = detect_event_language(" ".join([title, event_row.get("description", ""), category]))

    map_query = quote_plus(f"{parish_name} Catholic Church {city} Florida")
    maps_embed_url = f"https://www.google.com/maps?q={map_query}&output=embed"
    maps_open_url = f"https://www.google.com/maps/search/?api=1&query={map_query}"

    if st.button("← Back to events", key="back_to_events_top"):
        st.query_params.clear()
        st.rerun()

    st.markdown(f"""
    <div class="detail-card">
        <div class="detail-title">{title}</div>
        <div class="event-meta">{date_label} • {time_label}</div>
        <span class="badge">{category}</span>
        <span class="badge">{parish_name}</span>
        <span class="badge">{deanery}</span>
        <p style="margin-top:1rem;color:#244b58;font-size:1.05rem;line-height:1.6;">{description}</p>
        <p class="small-muted"><b>Language:</b> {language}</p>
        <p class="small-muted"><b>Source bulletin:</b> {source_file}</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown("""
        <h3 style="color:#073b4c; margin-top:1.25rem; font-weight:900;">Parish Location</h3>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="detail-map">
            <iframe
                src="{maps_embed_url}"
                width="100%"
                height="360"
                style="border:0;"
                allowfullscreen=""
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade">
            </iframe>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown(f"""
        <div class="detail-card">
            <h3 style="color:#073b4c;margin-top:0;">{parish_name}</h3>
            <p style="color:#244b58;"><b>City:</b> {city or 'Not listed'}</p>
            <p style="color:#244b58;"><b>Deanery:</b> {deanery or 'Not listed'}</p>
            <p style="color:#244b58;"><b>Event type:</b> {category}</p>
            <p><a href="{maps_open_url}" target="_blank" style="color:#087e8b;font-weight:900;">Open in Google Maps</a></p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("← Back to events", key="back_to_events_bottom"):
        st.query_params.clear()
        st.rerun()



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



# ============================================================
# PDF PARISH IDENTIFICATION + BETTER EVENT EXTRACTION
# ============================================================

def _norm_for_score(text):
    text = normalize(text)
    replacements = {
        "st ": "saint ",
        "ste ": "saint ",
        "cathedral of st ": "cathedral of saint ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip()


def infer_parish_from_filename(filename):
    """Fallback parish detector using the PDF file name."""
    name = _norm_for_score(filename.replace("_", " ").replace("-", " "))

    best_match = "Unknown Parish"
    best_score = 0

    for parish in parish_df["parish"]:
        parish_norm = _norm_for_score(parish)
        words = [w for w in parish_norm.split() if len(w) > 2 and w not in {"the", "of", "and", "mission", "parish", "church", "catholic"}]
        score = sum(1 for word in words if word in name)

        if parish_norm in name:
            score += 10

        if score > best_score:
            best_score = score
            best_match = parish

    return best_match if best_score >= 2 else "Unknown Parish"


def identify_parish_for_pdf(filename, text):
    """
    Identify which parish a bulletin belongs to BEFORE extracting events.
    Uses filename first, then the first pages of PDF text.
    """
    filename_guess = infer_parish_from_filename(filename)
    if filename_guess != "Unknown Parish":
        return filename_guess

    sample = _norm_for_score((filename + " " + text[:5000]).replace("\n", " "))

    best_match = "Unknown Parish"
    best_score = 0

    for _, row in parish_df.iterrows():
        parish = row["parish"]
        city = row.get("city", "")
        parish_norm = _norm_for_score(parish)
        city_norm = _norm_for_score(city)

        score = 0
        if parish_norm and parish_norm in sample:
            score += 20

        words = [w for w in parish_norm.split() if len(w) > 2 and w not in {"the", "of", "and", "mission", "parish", "church", "catholic"}]
        score += sum(3 for word in words if word in sample)

        if city_norm and city_norm in sample:
            score += 2

        # Common bulletin abbreviations
        if parish == "Holy Name of Jesus" and ("holy name" in sample or "hnj" in sample or "myhnj" in sample):
            score += 25
        if parish == "Basilica of Saint Edward" and ("basilica of saint edward" in sample or "basilicaofsaintedward" in sample or "st edward" in sample):
            score += 25
        if parish == "Saint Thomas More" and ("st thomas more" in sample or "saint thomas more" in sample or "stmbb" in sample):
            score += 25

        if score > best_score:
            best_score = score
            best_match = parish

    return best_match if best_score >= 5 else "Unknown Parish"


def infer_category(title, description=""):
    text = normalize(title + " " + description)

    if any(w in text for w in ["mass", "eucharist", "first communion", "communion", "vigil", "liturgy"]):
        return "Liturgy / Mass"
    if any(w in text for w in ["confession", "reconciliation", "penance", "rosary", "novena", "prayer", "stations", "divine mercy"]):
        return "Confession / Prayer"
    if "adoration" in text or "blessed sacrament" in text or "exposition" in text:
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
                try:
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=3)
                    if page_text:
                        text += "\n" + page_text
                except Exception:
                    continue
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
        r"\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)\s*[-–]\s*\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)",
        r"\d{1,2}\s*(?:am|pm|AM|PM)\s*[-–]\s*\d{1,2}\s*(?:am|pm|AM|PM)",
        r"\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)",
        r"\d{1,2}\s*(?:am|pm|AM|PM)",
        r"12\s*(?:noon|Noon|NOON)",
    ]
    combined = line + " " + context
    for pattern in time_patterns:
        match = re.search(pattern, combined)
        if match:
            return clean_text(match.group(0))
    return ""



def make_event_id(parish, title, date_label, time_label):
    raw = f"{parish}-{title}-{date_label}-{time_label}"
    return hashlib.md5(raw.encode()).hexdigest()


# ============================================================
# SMART BULLETIN EXTRACTION
# ============================================================

def _normalize_pdf_schedule_text(text):
    """
    Clean PDF text without changing the website layout.
    This helps with bulletin text like 8:00AM, 12Noon, SaturdayEveningVigilMass, etc.
    """
    text = text or ""
    text = text.replace("\u2014", "-").replace("\u2013", "-").replace("\u00a0", " ")
    text = re.sub(r"(?i)(\d{1,2}:\d{2})(am|pm)", r"\1 \2", text)
    text = re.sub(r"(?i)(\d{1,2})(am|pm)", r"\1 \2", text)
    text = re.sub(r"(?i)(\d{1,2})(noon)", r"\1 Noon", text)
    text = re.sub(r"(?i)\b12\s*noon\b", "12:00 PM", text)

    # Add spaces around common glued words from PDF extraction.
    replacements = {
        "MASSINTENTIONS": "MASS INTENTIONS",
        "SUMMERMASSSCHEDULE": "SUMMER MASS SCHEDULE",
        "MASSSCHEDULE": "MASS SCHEDULE",
        "SundayMasses": "Sunday Masses",
        "SaturdayEveningVigilMass": "Saturday Evening Vigil Mass",
        "DailyMass": "Daily Mass",
        "CONFESSIONS": "CONFESSIONS",
        "SACRAMENTS": "SACRAMENTS",
        "ADORATION": "ADORATION",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def _clean_lines(text):
    text = _normalize_pdf_schedule_text(text)
    return [clean_text(line) for line in text.splitlines() if clean_text(line)]


def _extract_times(text):
    """
    Extract real times from a local schedule/event context.
    Does not decide whether something is an event; it only normalizes time strings.
    """
    text = _normalize_pdf_schedule_text(text)
    raw_times = re.findall(
        r"(?i)\b\d{1,2}:\d{2}\s*(?:am|pm)\b|\b\d{1,2}\s*(?:am|pm)\b",
        text
    )

    cleaned = []
    for t in raw_times:
        t = clean_text(t).upper().replace(" ", "")
        t = t.replace("AM", " AM").replace("PM", " PM")
        if ":" not in t:
            t = t.replace(" AM", ":00 AM").replace(" PM", ":00 PM")
        if t not in cleaned:
            cleaned.append(t)

    return cleaned


def _has_time(text):
    return bool(_extract_times(text))


def _add_event(events, parish, source_file, title, date_label, time_label, category, description, confidence="rule"):
    title = clean_text(title)
    date_label = clean_text(date_label) or "See bulletin"
    time_label = clean_text(time_label) or "See bulletin"
    description = clean_text(description)

    if not title:
        return

    events.append({
        "id": make_event_id(parish, title, date_label, time_label),
        "title": title,
        "date_label": date_label,
        "time": time_label,
        "parish": parish,
        "category": category,
        "description": description,
        "source_file": source_file,
        "confidence": confidence,
    })



def _has_pdf_artifact_text_basic(text):
    raw = clean_text(text)
    low = normalize(raw)
    if not raw:
        return True
    if re.search(r"\(cid:\d+\)", raw, flags=re.I) or raw.count("(cid:") >= 1:
        return True
    if "::" in raw or re.search(r"(?i)\b(?:aamm|ppmm)\b", raw):
        return True
    artifact_phrases = [
        "view this bulletin online",
        "discovermass com",
        "www discovermass com",
        "lekti pou semen lan",
        "readings for the week",
        "scripture readings",
    ]
    return any(p in low for p in artifact_phrases)



def _is_noise_or_ad(text):
    """
    Reject lines that mention Catholic words but are not parish events:
    Mass intentions, readings, ads, phone/address blocks, online bulletin footers, etc.
    """
    text = clean_text(text)
    low = normalize(text)

    if _has_pdf_artifact_text_basic(text):
        return True

    noise_phrases = [
        "mass intentions",
        "unscheduled masses",
        "scripture readings",
        "readings for this sunday",
        "view this bulletin online",
        "for ad info",
        "catholic cruises",
        "catholicmatch",
        "insurance",
        "abogado",
        "incorporated",
        "contractors",
        "funeral",
        "cemetery",
        "advertise",
        "parishioner certificate",
        "pope s intentions",
        "gospel meditation",
        "meditacion del evangelio",
        "offertory",
        "dsa goal",
        "second collection",
        "parish clergy",
        "rectory office hours",
        "staff",
        "phone",
        "email",
        "website",
        "fax",
    ]

    if any(p in low for p in noise_phrases):
        return True

    # Reject mostly contact / address / ad lines.
    if re.search(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b", text) and not any(k in low for k in ["call to register", "for information", "contact"]):
        if not any(k in low for k in ["workshop", "retreat", "study", "meeting", "adoration", "confession", "mass schedule"]):
            return True

    if len(text) > 260 and not any(k in low for k in ["where", "when", "time", "join us", "meets", "schedule"]):
        return True

    return False



def _has_pdf_artifact_text(text):
    """
    Detect PDF extraction artifacts and footer/page text that should never become event cards.
    """
    raw = clean_text(text)
    low = normalize(raw)

    if not raw:
        return True

    artifact_phrases = [
        "view this bulletin online",
        "discovermass com",
        "www discovermass com",
        "page ",
        "cid",
        "lekti pou semen lan",
        "readings for the week",
        "scripture readings",
    ]

    if any(p in low for p in artifact_phrases):
        return True

    # Literal PDF character artifacts: (cid:3), (cid:160), etc.
    if re.search(r"\(cid:\d+\)", raw, flags=re.I):
        return True

    # Lines with many replacement/control artifacts are not usable event text.
    if raw.count("(cid:") >= 1:
        return True

    # Broken OCR time artifacts like 77::3300, 1122::0055, aamm, ppmm.
    if "::" in raw:
        return True
    if re.search(r"(?i)\b(?:aamm|ppmm)\b", raw):
        return True

    # Repeated OCR characters across a line, like Apprriill or TThhuurrss.
    repeated_pairs = re.findall(r"([A-Za-z])\1", raw)
    if len(repeated_pairs) >= 5:
        return True

    return False


def _is_bad_extracted_event(event):
    """
    Final safety gate before adding/displaying events.
    This catches footer junk that passed through context-based scoring.
    """
    title = clean_text(event.get("title", ""))
    description = clean_text(event.get("description", ""))
    date_label = clean_text(event.get("date_label", ""))
    time_label = clean_text(event.get("time", ""))
    category = clean_text(event.get("category", ""))

    combined = " ".join([title, description, date_label, time_label, category])

    if _has_pdf_artifact_text(title) or _has_pdf_artifact_text(description) or _has_pdf_artifact_text(combined):
        return True

    if _is_noise_or_ad(title) or _is_noise_or_ad(description):
        return True

    # Reject fake Mass cards that have no actual schedule.
    if category == "Liturgy / Mass" and date_label == "See bulletin" and time_label == "See bulletin":
        return True

    # Reject cards whose title is only a footer/page label or too vague.
    title_low = normalize(title)
    bad_titles = [
        "view this bulletin online at www discovermass com",
        "view this bulletin online",
        "page",
        "source",
    ]
    if any(bt in title_low for bt in bad_titles):
        return True

    return False


def _is_mass_intention_context(context):
    low = normalize(context)
    return any(p in low for p in [
        "mass intentions",
        "unscheduled masses",
        "by ",
        "special int",
        "parishioners and benefactors",
        "for the souls",
        "deceased",
        "intention",
        "intensions",
    ])


def _get_schedule_windows(lines):
    """
    Pull only the parts of the bulletin that are likely to contain real recurring schedules.
    This prevents the extractor from treating every Mass intention as a separate event.
    """
    windows = []
    schedule_markers = [
        "mass schedule", "celebration of the eucharist", "sacraments",
        "confessions", "confession", "adoration", "summer mass schedule",
        "daily mass", "sunday masses", "saturday vigil"
    ]

    for i, line in enumerate(lines):
        low = normalize(line)
        if any(marker in low for marker in schedule_markers):
            block = " ".join(lines[i:min(len(lines), i + 8)])
            windows.append(block)

    # Also include the first two pages worth of text because most bulletins put schedules there.
    if lines:
        windows.append(" ".join(lines[:80]))

    return windows


def _day_label_from_context(text, default="See bulletin"):
    low = normalize(text)

    if ("monday" in low and "friday" in low) or "mon fri" in low or "mon - fri" in low:
        return "Monday-Friday"
    if "monday" in low and "saturday" in low:
        return "Monday-Saturday"
    if "saturday" in low or "sabado" in low:
        return "Saturday"
    if "sunday" in low or "domingo" in low:
        return "Sunday"
    if "wednesday" in low or "miercoles" in low:
        return "Wednesday"
    if "thursday" in low or "jueves" in low:
        return "Thursday"
    if "friday" in low or "viernes" in low:
        return "Friday"

    return default


def _extract_schedule_items_from_window(window, parish, source_file):
    """
    Extract recurring sacramental schedules only from schedule-looking windows.
    This is intentionally stricter than a keyword search.
    """
    events = []
    window = _normalize_pdf_schedule_text(window)
    low = normalize(window)

    # Reject the whole block if it is clearly Mass intentions / readings / ads.
    if _is_mass_intention_context(window) and not any(k in low for k in ["mass schedule", "celebration of the eucharist", "sacraments"]):
        return events

    # Mass schedule lines/blocks.
    if any(k in low for k in ["mass schedule", "celebration of the eucharist", "daily mass", "sunday masses", "saturday vigil", "vigil mass"]):
        # Daily / weekday Mass.
        daily_patterns = [
            r"(?is)(?:daily mass|monday\s*(?:through|-|to)\s*friday|mon\s*-?\s*fri).*?(?=(?:saturday|sunday|confession|adoration|$))",
            r"(?is)(?:monday\s*(?:through|-|to)\s*saturday).*?(?=(?:sunday|confession|adoration|$))",
        ]

        for pattern in daily_patterns:
            for match in re.finditer(pattern, window):
                block = match.group(0)
                if _is_mass_intention_context(block):
                    continue
                for time_str in _extract_times(block):
                    _add_event(
                        events, parish, source_file,
                        "Daily Mass", _day_label_from_context(block, "Monday-Friday"),
                        time_str, "Liturgy / Mass",
                        "Recurring Mass schedule extracted from the bulletin's sacrament/schedule section.",
                        "schedule"
                    )

        # Saturday Vigil Mass.
        vigil_patterns = [
            r"(?is)(?:saturday\s*(?:evening)?\s*vigil\s*mass|vigil\s*mass).*?(?=(?:sunday|daily|confession|adoration|$))",
            r"(?is)(?:saturday\s*vigil).*?(?=(?:sunday|daily|confession|adoration|$))",
        ]

        for pattern in vigil_patterns:
            for match in re.finditer(pattern, window):
                block = match.group(0)
                for time_str in _extract_times(block):
                    _add_event(
                        events, parish, source_file,
                        "Saturday Vigil Mass", "Saturday", time_str,
                        "Liturgy / Mass",
                        "Saturday Vigil Mass schedule extracted from the bulletin's schedule section.",
                        "schedule"
                    )

        # Sunday Masses.
        sunday_patterns = [
            r"(?is)(?:sunday\s*masses|sunday\s*mass|sunday).*?(?=(?:daily|monday|saturday|confession|adoration|$))",
        ]

        for pattern in sunday_patterns:
            for match in re.finditer(pattern, window):
                block = match.group(0)
                if "readings" in normalize(block):
                    continue
                for time_str in _extract_times(block):
                    _add_event(
                        events, parish, source_file,
                        "Sunday Mass", "Sunday", time_str,
                        "Liturgy / Mass",
                        "Sunday Mass schedule extracted from the bulletin's schedule section.",
                        "schedule"
                    )

        # If schedule block is compact, like "SATURDAY VIGIL 4:00pm / SUNDAY 8:00am..."
        compact_parts = re.split(r"(?i)\b(SATURDAY VIGIL|SUNDAY|DAILY MASS|CONFESSIONS|ADORATION)\b", window)
        for idx in range(1, len(compact_parts), 2):
            header = compact_parts[idx]
            body = compact_parts[idx + 1] if idx + 1 < len(compact_parts) else ""
            block = header + " " + body[:250]
            hlow = normalize(header)
            if "saturday vigil" in hlow:
                for time_str in _extract_times(block):
                    _add_event(events, parish, source_file, "Saturday Vigil Mass", "Saturday", time_str, "Liturgy / Mass", "Saturday Vigil Mass schedule.", "schedule")
            elif hlow == "sunday":
                for time_str in _extract_times(block):
                    _add_event(events, parish, source_file, "Sunday Mass", "Sunday", time_str, "Liturgy / Mass", "Sunday Mass schedule.", "schedule")
            elif "daily mass" in hlow:
                for time_str in _extract_times(block):
                    _add_event(events, parish, source_file, "Daily Mass", "Monday-Friday", time_str, "Liturgy / Mass", "Daily Mass schedule.", "schedule")

    # Confession schedule.
    if any(k in low for k in ["confession", "confessions", "reconciliation", "penance"]):
        confession_blocks = re.findall(
            r"(?is)(?:confession|confessions|reconciliation|penance).*?(?=(?:adoration|mass schedule|daily mass|sunday masses|baptism|marriage|$))",
            window
        )
        for block in confession_blocks:
            if _is_noise_or_ad(block):
                continue
            for time_str in _extract_times(block):
                _add_event(
                    events, parish, source_file,
                    "Confession", _day_label_from_context(block, "Weekly"),
                    time_str, "Confession / Prayer",
                    "Confession/Reconciliation schedule extracted from the bulletin's sacrament section.",
                    "schedule"
                )

    # Adoration schedule.
    if any(k in low for k in ["adoration", "exposition", "blessed sacrament"]):
        adoration_blocks = re.findall(
            r"(?is)(?:adoration|exposition|blessed sacrament).*?(?=(?:confession|mass schedule|daily mass|sunday masses|baptism|marriage|$))",
            window
        )
        for block in adoration_blocks:
            if _is_noise_or_ad(block):
                continue
            times = _extract_times(block)
            time_label = " - ".join(times[:2]) if len(times) >= 2 else (times[0] if times else "See bulletin")
            _add_event(
                events, parish, source_file,
                "Eucharistic Adoration", _day_label_from_context(block, "See bulletin"),
                time_label, "Adoration",
                "Eucharistic Adoration schedule extracted from the bulletin's sacrament/schedule section.",
                "schedule"
            )

    return events


def extract_recurring_sacrament_events(text, parish, source_file):
    """
    Extract recurring schedules from schedule sections only.
    This avoids false positives such as Mass intentions, ads, readings, or articles mentioning Mass.
    """
    events = []
    lines = _clean_lines(text)

    for window in _get_schedule_windows(lines):
        events.extend(_extract_schedule_items_from_window(window, parish, source_file))

    unique = {}
    for e in events:
        unique[e["id"]] = e

    return list(unique.values())


def _event_quality_score(line, context):
    """
    Scores whether a line is a real event listing rather than an article/ad/random sentence.
    A line must have enough structure: title + time/date/meeting words, and must avoid noise.
    """
    combined = clean_text(line + " " + context)
    low = normalize(combined)

    if _is_noise_or_ad(combined) or _is_mass_intention_context(combined):
        return 0

    score = 0

    # Strong event structure.
    if re.search(r"(?i)\b(where|when|time|date|join us|meets?|meeting|register|registration|call to register|contact)\b", combined):
        score += 3

    if find_date_near_line(line, context):
        score += 3

    if find_time_near_line(line, context):
        score += 3

    # Good event category words.
    category_words = [
        "workshop", "retreat", "bible study", "faith formation", "oica", "rcia",
        "youth", "young adult", "luncheon", "gathering", "festival", "speaker",
        "meeting", "ministry", "volunteer", "food pantry", "outreach",
        "knights of columbus", "columbiettes", "legion of mary",
        "carmelite", "may crowning", "revival", "adoration",
        "rosary", "novena", "prayer group", "marriage", "couples", "parejas"
    ]

    if any(word in low for word in category_words):
        score += 3

    # Recurrence clues.
    recurrence_words = [
        "every", "weekly", "monthly", "second monday", "second wednesday",
        "third friday", "last monday", "each month", "todos", "cada",
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ]

    if any(word in low for word in recurrence_words):
        score += 2

    # Avoid vague theology/article sentences.
    article_words = ["gospel", "reading", "meditation", "pope", "scripture", "reflection", "homily"]
    if any(word in low for word in article_words) and not any(word in low for word in ["join", "meets", "workshop", "study", "prayer group"]):
        score -= 4

    return score


def _make_title_from_event_context(line, context):
    """
    Prefer the short uppercase/event-like heading as title.
    """
    title = clean_text(line)

    # If line is "Where/When/Time", use previous heading from context.
    if normalize(title) in {"where", "when", "time", "date"} or re.match(r"(?i)^(where|when|time|date)\s*:", title):
        parts = [p.strip() for p in context.split("  ") if p.strip()]
        for p in parts:
            if len(p) <= 90 and not re.match(r"(?i)^(where|when|time|date)\s*:", p):
                return p

    # Trim very long descriptions.
    if len(title) > 110:
        title = title[:110] + "..."

    return title


def extract_general_bulletin_events(text, parish, source_file):
    """
    Extract non-schedule events using structure and context, not just keywords.
    This requires a useful date/time/recurrence clue and rejects ads, articles, Mass intentions, and readings.
    """
    lines = _clean_lines(text)
    events = []

    for i, line in enumerate(lines):
        if _is_noise_or_ad(line):
            continue

        previous_lines = lines[max(0, i - 3):i]
        next_lines = lines[i + 1:min(len(lines), i + 5)]
        context = " ".join(previous_lines + next_lines)

        score = _event_quality_score(line, context)
        if score < 5:
            continue

        # Avoid creating a general event for the sacrament schedule itself;
        # those are handled by extract_recurring_sacrament_events.
        low = normalize(line + " " + context)
        if any(k in low for k in ["mass schedule", "celebration of the eucharist", "sunday masses", "daily mass", "confessions"]):
            continue

        title = _make_title_from_event_context(line, context)
        date_label = find_date_near_line(line, context) or _day_label_from_context(line + " " + context, "See bulletin")
        time_label = find_time_near_line(line, context) or "See bulletin"
        description = clean_text(" ".join([line] + next_lines[:3]))
        category = infer_category(title, description)

        _add_event(
            events,
            parish,
            source_file,
            title,
            date_label,
            time_label,
            category,
            description,
            "scored"
        )

    unique = {}
    for e in events:
        unique[e["id"]] = e

    return list(unique.values())


def extract_events_from_text(text, parish, source_file):
    """
    Main extraction:
    1. Extract recurring sacrament schedules from schedule sections only.
    2. Extract other events only when the line has event-like structure.
    """
    events = []
    events.extend(extract_recurring_sacrament_events(text, parish, source_file))
    events.extend(extract_general_bulletin_events(text, parish, source_file))

    unique = {}
    for event in events:
        if not _is_bad_extracted_event(event):
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
        text = extract_text_from_pdf(pdf_path)
        parish = identify_parish_for_pdf(file, text)
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
# EVENT DETAIL ROUTING
# ============================================================

selected_event_id = st.query_params.get("event")
if isinstance(selected_event_id, list):
    selected_event_id = selected_event_id[0] if selected_event_id else None

if selected_event_id and not events_df.empty:
    selected_match = events_df[events_df["id"].astype(str) == str(selected_event_id)]
    if not selected_match.empty:
        render_event_detail_page(selected_match.iloc[0])
        st.stop()
    else:
        st.warning("That event could not be found. Returning to the event list.")
        st.query_params.clear()

    events_df = events_df[
        ~events_df.apply(lambda row: _is_bad_extracted_event(row.to_dict()), axis=1)
    ].reset_index(drop=True)


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
# ============================================================
# FIND AN EVENT GUI
# ============================================================

st.markdown("""
<h2 style="color:#073b4c; margin-top:30px; margin-bottom:0.35rem; font-weight:900;">
Find an Event
</h2>
<p style="color:#3f6473; margin-top:0;">
Search parish bulletins by parish, event type, Mass, confession, adoration, and other parish life events.
</p>
""", unsafe_allow_html=True)

filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1.4])

with filter_col1:
    selected_category = st.selectbox(
        "Event type",
        ["All"] + CATEGORY_OPTIONS
    )

with filter_col2:
    # IMPORTANT: always show ALL 54 parishes, not just parishes with matched events
    parish_options = ["All"] + parish_df["parish"].dropna().tolist()
    selected_parish = st.selectbox(
        "Parish",
        parish_options
    )

with filter_col3:
    search_query = st.text_input(
        "Search by keyword",
        placeholder="Try: mass, confession, adoration, rosary, youth..."
    )


filtered_df = events_df.copy()

if selected_category != "All" and not filtered_df.empty:
    filtered_df = filtered_df[
        filtered_df["category"].astype(str).str.contains(selected_category, case=False, na=False)
    ]

if selected_parish != "All" and not filtered_df.empty:
    filtered_df = filtered_df[
        filtered_df["parish"].astype(str).str.contains(selected_parish, case=False, na=False)
    ]

if search_query.strip() and not filtered_df.empty:
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
                str(row.get("source_file", "")),
            ]).lower(),
            axis=1
        )
    ]


st.markdown(f"""
<h4 style="color:#075763; margin-top:1rem;">
{len(filtered_df)} event(s) found
</h4>
""", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No events matched your filters. If you just uploaded PDFs, reboot/redeploy Streamlit so the cached bulletin scan refreshes.")
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

        if st.button("View event details", key=f"view_event_{row['id']}"):
            st.query_params["event"] = str(row["id"])
            st.rerun()

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
