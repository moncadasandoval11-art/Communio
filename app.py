
import json
import hashlib
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


# ============================================================
# APP CONFIG
# ============================================================

st.set_page_config(
    page_title="Communio | Diocese of Palm Beach",
    page_icon="✦",
    layout="wide",
)

DATA_FILE = Path("events_data.json")

DIOCESE_HOME = "https://www.diocesepb.org/"
DIOCESE_EVENTS = "https://www.diocesepb.org/news/events.html"
BISHOP_MESSAGE = "https://www.diocesepb.org/about-us/office-of-the-bishop.html"
ST_THOMAS_MORE_BULLETIN = "https://www.flipsnack.com/stmbb/st-thomas-more-catholic-church-april-2026-bulletin"


CATEGORY_OPTIONS = [
    "All",
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
    "Diocesan",
]


# ============================================================
# SEEDED PARISH DIRECTORY
# ============================================================

PARISHES = [
    # Northern Deanery
    {"deanery":"Northern Deanery","parish":"Saint Sebastian","city":"Sebastian","address":"13075 US Highway 1, Sebastian, FL 32958","phone":"772-589-5790","email":"office@stsebastian.com"},
    {"deanery":"Northern Deanery","parish":"Our Lady of Guadalupe Mission","city":"Fellsmere","address":"Fellsmere, FL","phone":"772-571-9875","email":"office@olgmission.com"},
    {"deanery":"Northern Deanery","parish":"Holy Cross","city":"Vero Beach","address":"Vero Beach, FL","phone":"772-231-0671","email":"cflynn@holycrossverobeach.org"},
    {"deanery":"Northern Deanery","parish":"Saint Helen","city":"Vero Beach","address":"Vero Beach, FL","phone":"772-567-5129","email":"church@sthelenvero.org"},
    {"deanery":"Northern Deanery","parish":"Saint John of the Cross","city":"Vero Beach","address":"Vero Beach, FL","phone":"772-563-0057","email":"info@stjohnsvero.org"},
    {"deanery":"Northern Deanery","parish":"Notre Dame Catholic Mission","city":"Fort Pierce","address":"Fort Pierce, FL","phone":"772-466-9617","email":"info@notredamecatholicmission.org"},
    {"deanery":"Northern Deanery","parish":"Saint Anastasia","city":"Fort Pierce","address":"Fort Pierce, FL","phone":"772-461-2233","email":"frontdesk@stanastasiachurch.org"},
    {"deanery":"Northern Deanery","parish":"San Juan Diego Hispanic Pastoral Center","city":"Fort Pierce","address":"Fort Pierce, FL","phone":"772-468-0806","email":"sanjuandiegohm129@outlook.com"},
    {"deanery":"Northern Deanery","parish":"Saint Mark the Evangelist","city":"Fort Pierce","address":"Fort Pierce, FL","phone":"772-461-8150","email":"stmarks1924@gmail.com"},
    {"deanery":"Northern Deanery","parish":"Holy Family","city":"Port St. Lucie","address":"Port St. Lucie, FL","phone":"772-335-2385","email":"office@holyfamilyccpsl.com"},
    {"deanery":"Northern Deanery","parish":"Saint Lucie","city":"Port St. Lucie","address":"Port St. Lucie, FL","phone":"772-878-1215","email":"parishoffice@stlucie.cc"},
    {"deanery":"Northern Deanery","parish":"Saint Elizabeth Ann Seton","city":"Port St. Lucie","address":"Port St. Lucie, FL","phone":"772-336-0282","email":"seton@steasparish.org"},
    {"deanery":"Northern Deanery","parish":"Saint Bernadette","city":"Port St. Lucie","address":"Port St. Lucie, FL","phone":"772-336-9956","email":"parish@stbernadetteslw.org"},
    {"deanery":"Northern Deanery","parish":"Sacred Heart","city":"Okeechobee","address":"Okeechobee, FL","phone":"863-763-3727","email":"sacredheart901@outlook.com"},

    # Cathedral Deanery
    {"deanery":"Cathedral Deanery","parish":"Saint Martin de Porres","city":"Jensen Beach","address":"Jensen Beach, FL","phone":"772-334-4214","email":"info@stmartindp.com"},
    {"deanery":"Cathedral Deanery","parish":"Saint Joseph","city":"Stuart","address":"Stuart, FL","phone":"772-287-2727","email":"melanied@sjcflorida.org"},
    {"deanery":"Cathedral Deanery","parish":"Holy Redeemer","city":"Palm City","address":"Palm City, FL","phone":"772-286-4590","email":"ewesley@holyredeemercc.org"},
    {"deanery":"Cathedral Deanery","parish":"Saint Andrew","city":"Stuart","address":"Stuart, FL","phone":"772-781-4415","email":"admin@saintandrewcatholic.org"},
    {"deanery":"Cathedral Deanery","parish":"Saint Christopher","city":"Hobe Sound","address":"Hobe Sound, FL","phone":"772-546-5150","email":"office@stchrishs.com"},
    {"deanery":"Cathedral Deanery","parish":"Holy Cross","city":"Indiantown","address":"Indiantown, FL","phone":"772-597-2798","email":"holycross351@gmail.com"},
    {"deanery":"Cathedral Deanery","parish":"Saint Jude","city":"Tequesta","address":"Tequesta, FL","phone":"561-746-7974","email":"info@stjudechurch.net"},
    {"deanery":"Cathedral Deanery","parish":"Saint Peter","city":"Jupiter","address":"Jupiter, FL","phone":"561-575-0837","email":"office@stpeterjupiter.com"},
    {"deanery":"Cathedral Deanery","parish":"Saint Patrick","city":"Palm Beach Gardens","address":"Palm Beach Gardens, FL","phone":"561-626-8626","email":"donna@stpatrickchurch.org"},
    {"deanery":"Cathedral Deanery","parish":"Saint Paul of the Cross","city":"North Palm Beach","address":"North Palm Beach, FL","phone":"561-626-1873","email":"office@paulcross.org"},
    {"deanery":"Cathedral Deanery","parish":"Cathedral of Saint Ignatius Loyola","city":"Palm Beach Gardens","address":"Palm Beach Gardens, FL","phone":"561-622-2565","email":"office@cathedralpb.com"},
    {"deanery":"Cathedral Deanery","parish":"Saint Clare","city":"North Palm Beach","address":"North Palm Beach, FL","phone":"561-622-7477","email":"info@stclarechurch.net"},
    {"deanery":"Cathedral Deanery","parish":"Saint Francis of Assisi","city":"Riviera Beach","address":"Riviera Beach, FL","phone":"561-842-2482","email":"stfrancisrbf@gmail.com"},
    {"deanery":"Cathedral Deanery","parish":"Saint John Fisher","city":"West Palm Beach","address":"West Palm Beach, FL","phone":"561-842-1224","email":"sjf@stjohnfisherwpb.com"},

    # Central Deanery
    {"deanery":"Central Deanery","parish":"Mary Immaculate","city":"West Palm Beach","address":"West Palm Beach, FL","phone":"561-686-8128","email":"RVanoordt@miwpb.com"},
    {"deanery":"Central Deanery","parish":"Basilica of Saint Edward","city":"Palm Beach","address":"144 North County Road, Palm Beach, FL 33480","phone":"561-832-0400","email":"stedwardch@aol.com"},
    {"deanery":"Central Deanery","parish":"Saint Ann","city":"West Palm Beach","address":"West Palm Beach, FL","phone":"561-832-3757","email":""},
    {"deanery":"Central Deanery","parish":"Our Lady Queen of Apostles","city":"Royal Palm Beach","address":"Royal Palm Beach, FL","phone":"561-798-5661","email":"info@olqa.cc"},
    {"deanery":"Central Deanery","parish":"Saint Rita","city":"Wellington","address":"Wellington, FL","phone":"561-793-8544","email":"office@saintrita.com"},
    {"deanery":"Central Deanery","parish":"Saint Therese de Lisieux","city":"Wellington","address":"Wellington, FL","phone":"561-784-0689","email":"frontoffice@sttherese-church.org"},
    {"deanery":"Central Deanery","parish":"Saint Mary","city":"Pahokee","address":"Pahokee, FL","phone":"561-924-7305","email":"office@stmaryofpahokee.com"},
    {"deanery":"Central Deanery","parish":"Saint Philip Benizi","city":"Belle Glade","address":"Belle Glade, FL","phone":"561-996-3870","email":"stphilipbenizicc21@gmail.com"},
    {"deanery":"Central Deanery","parish":"Holy Name of Jesus","city":"West Palm Beach","address":"345 South Military Trail, West Palm Beach, FL 33415","phone":"561-683-3555","email":"bulletin@myhnj.org"},
    {"deanery":"Central Deanery","parish":"Saint Juliana","city":"West Palm Beach","address":"West Palm Beach, FL","phone":"561-833-9745","email":"officeadmin@stjulianawpb.com"},
    {"deanery":"Central Deanery","parish":"Saint Luke","city":"Palm Springs","address":"Palm Springs, FL","phone":"561-965-8980","email":"frandrew@stlukeparish.com"},
    {"deanery":"Central Deanery","parish":"Sacred Heart","city":"Lake Worth","address":"Lake Worth, FL","phone":"561-582-4736","email":"rectory@sacredheartfamily.com"},
    {"deanery":"Central Deanery","parish":"Holy Spirit","city":"Lantana","address":"Lantana, FL","phone":"561-585-5970","email":"office@holyspiritlantana.com"},
    {"deanery":"Central Deanery","parish":"Saint Matthew","city":"Lantana","address":"Lantana, FL","phone":"561-966-8878","email":"frclemh@bellsouth.net"},

    # Southern Deanery
    {"deanery":"Southern Deanery","parish":"Saint Mark","city":"Boynton Beach","address":"Boynton Beach, FL","phone":"561-734-9330","email":"maskar@stmarkboynton.com"},
    {"deanery":"Southern Deanery","parish":"Saint Thomas More","city":"Boynton Beach","address":"Boynton Beach, FL","phone":"561-737-3095","email":"operations@stmbb.org"},
    {"deanery":"Southern Deanery","parish":"Emmanuel","city":"Delray Beach","address":"Delray Beach, FL","phone":"561-496-2480","email":"secretary@emmanuelcatholic.church"},
    {"deanery":"Southern Deanery","parish":"Saint Vincent Ferrer","city":"Delray Beach","address":"Delray Beach, FL","phone":"561-276-6892","email":"office@stvincentferrer.com"},
    {"deanery":"Southern Deanery","parish":"Our Lady of Perpetual Help Mission","city":"Delray Beach","address":"Delray Beach, FL","phone":"561-276-4880","email":"perpetualchurch@att.net"},
    {"deanery":"Southern Deanery","parish":"Our Lady Queen of Peace","city":"Delray Beach","address":"Delray Beach, FL","phone":"561-499-6234","email":"queenofpeacedelray@gmail.com"},
    {"deanery":"Southern Deanery","parish":"Saint Lucy","city":"Highland Beach","address":"Highland Beach, FL","phone":"561-278-1280","email":"stlucys@bellsouth.net"},
    {"deanery":"Southern Deanery","parish":"Ascension","city":"Boca Raton","address":"Boca Raton, FL","phone":"561-997-5486","email":"ascension@accboca.net"},
    {"deanery":"Southern Deanery","parish":"Saint Joan of Arc","city":"Boca Raton","address":"Boca Raton, FL","phone":"561-392-0007","email":"info_church@stjoan.org"},
    {"deanery":"Southern Deanery","parish":"Saint Jude","city":"Boca Raton","address":"Boca Raton, FL","phone":"561-392-8172","email":"info@stjudeboca.org"},
    {"deanery":"Southern Deanery","parish":"Our Lady of Lourdes","city":"Boca Raton","address":"Boca Raton, FL","phone":"561-483-2440","email":"secretary@lourdesboca.org"},
    {"deanery":"Southern Deanery","parish":"Saint John the Evangelist","city":"Boca Raton","address":"Boca Raton, FL","phone":"561-488-1373","email":"office@stjohnevangelistbr.org"},
]


# ============================================================
# SEEDED MANUAL EVENTS
# These behave like events that were manually uploaded through the website.
# ============================================================

SEEDED_EVENTS = [
    {
        "title": "Final Guild Gathering and May Crowning",
        "date_label": "Wednesday, May 6, 2026",
        "time": "11:00 AM",
        "location": "Basilica of Saint Edward",
        "category": "Social / Fellowship",
        "description": "Old-fashioned May procession, Crowning of the Blessed Mother, music, flowers, and spring luncheon in the parish hall.",
        "parish": "Basilica of Saint Edward",
        "source": "Manual bulletin upload — Basilica of Saint Edward, April 26, 2026",
        "source_url": "",
    },
    {
        "title": "Summer Mass Schedule Begins",
        "date_label": "Monday, April 27, 2026",
        "time": "8:00 AM daily Mass",
        "location": "Basilica of Saint Edward",
        "category": "Liturgy / Mass",
        "description": "Daily Mass changes to 8:00 AM Monday through Saturday. Sunday schedule changes May 3 to 9:00 AM, 10:30 AM, and 12:00 Noon.",
        "parish": "Basilica of Saint Edward",
        "source": "Manual bulletin upload — Basilica of Saint Edward, April 26, 2026",
        "source_url": "",
    },
    {
        "title": "Rosary Group",
        "date_label": "Monday through Saturday",
        "time": "After 8:30 AM Mass",
        "location": "Basilica of Saint Edward",
        "category": "Confession / Prayer",
        "description": "Parishioners are invited to pray the Rosary together after morning Mass.",
        "parish": "Basilica of Saint Edward",
        "source": "Manual bulletin upload — Basilica of Saint Edward, April 26, 2026",
        "source_url": "",
    },
    {
        "title": "World Youth Day Seoul 2027 Pilgrimage Registration",
        "date_label": "Registration deadline: May 31, 2026",
        "time": "",
        "location": "Diocese of Palm Beach / Seoul, South Korea",
        "category": "Youth / Young Adult",
        "description": "Bishop Manuel de Jesús Rodríguez invites high school youth and young adults ages 16–39 to join the diocesan pilgrimage to World Youth Day, August 1–10, 2027.",
        "parish": "Diocese of Palm Beach",
        "source": "Manual bulletin upload",
        "source_url": "",
    },
    {
        "title": "Mid-Morning Bible Study",
        "date_label": "Every Wednesday",
        "time": "10:00 AM – 12:00 PM",
        "location": "Holy Name of Jesus, School Room 3",
        "category": "Adult Formation",
        "description": "Weekly Catholic Bible study using videos, Scripture, and the Catechism of the Church.",
        "parish": "Holy Name of Jesus",
        "source": "Manual bulletin upload — Holy Name of Jesus, May 3, 2026",
        "source_url": "",
    },
    {
        "title": "Extraordinary Ministers of Holy Communion Workshop",
        "date_label": "Saturday, May 23, 2026",
        "time": "9:00 AM – 11:45 AM",
        "location": "Holy Name of Jesus / Fatima Hall",
        "category": "Adult Formation",
        "description": "Workshop for existing Extraordinary Ministers of Holy Communion and anyone wishing to become a new Eucharistic Minister.",
        "parish": "Holy Name of Jesus",
        "source": "Manual bulletin upload — Holy Name of Jesus, May 3, 2026",
        "source_url": "",
    },
    {
        "title": "Unbound Revival Fire",
        "date_label": "Sunday, May 24, 2026",
        "time": "5:00 PM – 8:00 PM",
        "location": "Holy Name of Jesus Catholic Church",
        "category": "Adoration",
        "description": "Holy Mass, praise and worship, Eucharistic adoration, and laying on of hands. Preaching by Fr. Antony Lopez.",
        "parish": "Holy Name of Jesus",
        "source": "Manual bulletin upload — Holy Name of Jesus, May 3, 2026",
        "source_url": "",
    },
    {
        "title": "Amor de Pareja: Diseño Divino",
        "date_label": "Saturday, May 16, 2026",
        "time": "6:00 PM – 9:00 PM",
        "location": "Holy Name of Jesus / Trinity Center",
        "category": "Marriage / Family",
        "description": "Spanish-language couples conference. Registration listed at $20 per couple with refreshments.",
        "parish": "Holy Name of Jesus",
        "source": "Manual bulletin upload — Holy Name of Jesus, May 3, 2026",
        "source_url": "",
    },
    {
        "title": "Saint Thomas More April 2026 Bulletin",
        "date_label": "April 2026",
        "time": "",
        "location": "Saint Thomas More, Boynton Beach",
        "category": "Adult Formation",
        "description": "Bulletin link stored for manual review/import. Events can be added below with the manual event form.",
        "parish": "Saint Thomas More",
        "source": "Manual bulletin link",
        "source_url": ST_THOMAS_MORE_BULLETIN,
    },
]


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(212, 175, 55, 0.18), transparent 34%),
        radial-gradient(circle at 90% 5%, rgba(90, 47, 156, 0.18), transparent 30%),
        linear-gradient(135deg, #09090d 0%, #11131c 45%, #17111d 100%);
    color: #f8f4ea;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 3rem;
}

.hero {
    border: 1px solid rgba(245, 211, 122, 0.22);
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.025));
    box-shadow: 0 24px 80px rgba(0,0,0,0.35);
    border-radius: 32px;
    padding: 2.2rem;
    margin-bottom: 1.1rem;
}

.logo-wrap {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.logo-mark {
    width: 76px;
    height: 76px;
    border-radius: 24px;
    background:
        linear-gradient(135deg, #f7d77f, #af7e2e),
        radial-gradient(circle at 60% 20%, white, transparent);
    display: grid;
    place-items: center;
    box-shadow: 0 0 30px rgba(247,215,127,0.25);
    color: #131018;
    font-size: 2.5rem;
    font-weight: 800;
}

.logo-title {
    font-family: 'Cinzel', serif;
    font-size: 3.2rem;
    line-height: 1;
    letter-spacing: 0.05em;
    color: #f7d77f;
    margin: 0;
}

.logo-subtitle {
    margin-top: .25rem;
    color: #d7c9ad;
    font-size: 1.05rem;
}

.quick-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .8rem;
    margin-top: 1.4rem;
}

.quick-card {
    border: 1px solid rgba(247,215,127,.20);
    background: rgba(255,255,255,.045);
    padding: 1rem;
    border-radius: 20px;
}

.quick-card a {
    color: #f7d77f !important;
    font-weight: 800;
    text-decoration: none;
}

.quick-card p {
    color: #cfc5b3;
    margin-bottom: 0;
    font-size: .92rem;
}

.event-card {
    border: 1px solid rgba(247,215,127,.20);
    background: rgba(255,255,255,.055);
    border-radius: 24px;
    padding: 1.1rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 16px 45px rgba(0,0,0,.20);
}

.event-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #fff9e8;
    margin-bottom: .35rem;
}

.meta {
    color: #d7c9ad;
    font-size: .92rem;
    margin-bottom: .25rem;
}

.pill {
    display: inline-block;
    padding: .25rem .55rem;
    border-radius: 999px;
    background: rgba(247,215,127,.14);
    border: 1px solid rgba(247,215,127,.28);
    color: #f7d77f;
    margin-right: .35rem;
    margin-top: .55rem;
    font-size: .78rem;
    font-weight: 700;
}

.parish-card {
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.045);
    border-radius: 22px;
    padding: 1rem;
    margin-bottom: .8rem;
}

.parish-title {
    font-weight: 800;
    font-size: 1.1rem;
    color: #fff9e8;
}

.small-muted {
    color: #cfc5b3;
    font-size: .9rem;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(247,215,127,.18);
    padding: 1rem;
    border-radius: 20px;
}

@media (max-width: 900px) {
    .quick-grid { grid-template-columns: 1fr; }
    .logo-title { font-size: 2.4rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def event_id(event: dict) -> str:
    base = f"{event.get('parish','')}-{event.get('title','')}-{event.get('date_label','')}-{event.get('time','')}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()


def add_ids(events: list[dict]) -> list[dict]:
    out = []
    for e in events:
        copy = dict(e)
        copy.setdefault("id", event_id(copy))
        copy.setdefault("date_added", "seeded")
        out.append(copy)
    return out


def load_manual_events() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text())
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            events = []
            for parish_data in data.values():
                if isinstance(parish_data, dict):
                    events.extend(parish_data.get("events", []))
                elif isinstance(parish_data, list):
                    events.extend(parish_data)
            return events
    except Exception:
        return []
    return []


def save_manual_event(event: dict) -> None:
    events = load_manual_events()
    event["id"] = event_id(event)
    event["date_added"] = datetime.now().isoformat()

    existing_ids = {e.get("id") for e in events}
    if event["id"] not in existing_ids:
        events.append(event)

    DATA_FILE.write_text(json.dumps(events, indent=2))


def save_many_events(events_to_save: list[dict]) -> int:
    events = load_manual_events()
    existing_ids = {e.get("id") for e in events}
    count = 0

    for event in events_to_save:
        event["id"] = event_id(event)
        event["date_added"] = datetime.now().isoformat()
        if event["id"] not in existing_ids:
            events.append(event)
            existing_ids.add(event["id"])
            count += 1

    DATA_FILE.write_text(json.dumps(events, indent=2))
    return count


def extract_text_from_pdf(uploaded_file) -> str:
    if pdfplumber is None:
        st.error("pdfplumber is missing. Add pdfplumber to requirements.txt.")
        return ""

    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        st.error(f"Could not read PDF: {e}")

    return text


def infer_category(title: str, description: str = "") -> str:
    t = f"{title} {description}".lower()
    if any(x in t for x in ["mass", "eucharist", "holy communion", "liturgy"]):
        return "Liturgy / Mass"
    if "adoration" in t:
        return "Adoration"
    if any(x in t for x in ["rosary", "novena", "prayer", "confession"]):
        return "Confession / Prayer"
    if "retreat" in t:
        return "Retreat"
    if any(x in t for x in ["youth", "young adult", "world youth day"]):
        return "Youth / Young Adult"
    if any(x in t for x in ["marriage", "couple", "pareja", "family"]):
        return "Marriage / Family"
    if any(x in t for x in ["school", "open house"]):
        return "School / Open House"
    if any(x in t for x in ["pantry", "donation", "charity", "outreach", "service"]):
        return "Service / Charity"
    if any(x in t for x in ["bible", "formation", "study", "workshop", "catechism"]):
        return "Adult Formation"
    if any(x in t for x in ["luncheon", "guild", "social", "fellowship"]):
        return "Social / Fellowship"
    return "Adult Formation"


def keyword_extract_events(text: str, parish: str, source_name: str) -> list[dict]:
    """
    No-API fallback extractor.
    It does not understand bulletins like ChatGPT would, but it catches common event lines.
    Users can edit/add events with the manual form.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    events = []

    keywords = [
        "workshop", "bible study", "adoration", "retreat", "conference", "conferencia",
        "rosary", "novena", "mass", "youth day", "guild", "meeting", "reun", "misa"
    ]

    for i, line in enumerate(lines):
        lower = line.lower()
        if not any(k in lower for k in keywords):
            continue

        context = " ".join(lines[i:i+5])
        title = line[:90]

        events.append({
            "title": title,
            "date_label": "",
            "time": "",
            "location": parish,
            "category": infer_category(title, context),
            "description": context[:350],
            "parish": parish,
            "source": f"Manual PDF keyword import — {source_name}",
            "source_url": "",
        })

    # keep it sane
    return add_ids(events[:20])


def matches(row: pd.Series, query: str) -> bool:
    if not query:
        return True
    haystack = " ".join(str(v) for v in row.fillna("").values).lower()
    return query.lower() in haystack


def render_event(event: pd.Series) -> None:
    title = event.get("title", "")
    date_label = event.get("date_label", "")
    time = event.get("time", "")
    location = event.get("location", "")
    description = event.get("description", "")
    parish = event.get("parish", "")
    category = event.get("category", "")
    source = event.get("source", "")
    source_url = event.get("source_url", "")

    source_html = f'<a href="{source_url}" target="_blank">{source}</a>' if source_url else source

    st.markdown(
        f"""
<div class="event-card">
    <div class="event-title">{title}</div>
    <div class="meta">🗓️ {date_label or "Date not listed"} {(" · " + time) if time else ""}</div>
    <div class="meta">📍 {location or parish or "Location not listed"}</div>
    <div class="small-muted">{description}</div>
    <span class="pill">{category}</span>
    <span class="pill">{parish}</span>
    <span class="pill">{source_html}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def render_parish(row: pd.Series) -> None:
    email = row.get("email", "")
    email_html = f'<a href="mailto:{email}">{email}</a>' if email else "No email listed"

    st.markdown(
        f"""
<div class="parish-card">
    <div class="parish-title">{row.get("parish","")}</div>
    <div class="small-muted">{row.get("deanery","")} · {row.get("city","")}</div>
    <div class="small-muted">📍 {row.get("address","")}</div>
    <div class="small-muted">☎️ {row.get("phone","")} · ✉️ {email_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# LOAD DATA
# ============================================================

parishes_df = pd.DataFrame(PARISHES)

seeded_events = add_ids(SEEDED_EVENTS)
saved_events = load_manual_events()
events_df = pd.DataFrame(seeded_events + saved_events)

if not events_df.empty:
    events_df = events_df.drop_duplicates(subset=["id"], keep="first")


# ============================================================
# HERO
# ============================================================

st.markdown(
    f"""
<div class="hero">
    <div class="logo-wrap">
        <div class="logo-mark">✦</div>
        <div>
            <h1 class="logo-title">COMMUNIO</h1>
            <div class="logo-subtitle">One living map of parish life across the Diocese of Palm Beach.</div>
        </div>
    </div>

    <div class="quick-grid">
        <div class="quick-card">
            <a href="{DIOCESE_HOME}" target="_blank">Diocese Website</a>
            <p>Official diocesan homepage, offices, ministries, news, and resources.</p>
        </div>
        <div class="quick-card">
            <a href="{DIOCESE_EVENTS}" target="_blank">Diocesan Calendar</a>
            <p>Quick jump to official diocesan events.</p>
        </div>
        <div class="quick-card">
            <a href="{BISHOP_MESSAGE}" target="_blank">Message from the Bishop</a>
            <p>A dedicated space for the bishop’s pastoral voice and diocesan updates.</p>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Explore")

    view = st.radio(
        "View",
        ["Events", "Parishes", "Manual Upload", "Add Event"],
        index=0,
    )

    search = st.text_input("Search", placeholder="Bible study, Boynton, adoration...")
    category = st.selectbox("Category", CATEGORY_OPTIONS)
    deanery = st.selectbox("Deanery", ["All"] + sorted(parishes_df["deanery"].unique()))
    parish_choice = st.selectbox("Parish", ["All"] + sorted(parishes_df["parish"].unique()))

    st.divider()
    st.caption("No API key required. Events shown here include seeded/manual bulletin entries plus anything you add through the form.")


# ============================================================
# FILTERS
# ============================================================

filtered_parishes = parishes_df.copy()
filtered_events = events_df.copy()

if deanery != "All":
    filtered_parishes = filtered_parishes[filtered_parishes["deanery"] == deanery]
    filtered_events = filtered_events[filtered_events["parish"].isin(filtered_parishes["parish"]) | (filtered_events["parish"] == "Diocese of Palm Beach")]

if parish_choice != "All":
    filtered_parishes = filtered_parishes[filtered_parishes["parish"] == parish_choice]
    filtered_events = filtered_events[filtered_events["parish"] == parish_choice]

if category != "All":
    filtered_events = filtered_events[filtered_events["category"] == category]

if search:
    filtered_parishes = filtered_parishes[filtered_parishes.apply(lambda r: matches(r, search), axis=1)]
    filtered_events = filtered_events[filtered_events.apply(lambda r: matches(r, search), axis=1)]


# ============================================================
# MAIN VIEWS
# ============================================================

if view == "Events":
    c1, c2, c3 = st.columns(3)
    c1.metric("Events", len(filtered_events))
    c2.metric("Parishes", len(parishes_df))
    c3.metric("Manual system", "Enabled")

    st.subheader("Parish and Diocesan Events")

    if filtered_events.empty:
        st.info("No events match your filters.")
    else:
        for _, event in filtered_events.iterrows():
            render_event(event)


elif view == "Parishes":
    st.subheader("Parish Directory")

    if filtered_parishes.empty:
        st.info("No parishes match your filters.")
    else:
        for _, row in filtered_parishes.sort_values(["deanery", "city", "parish"]).iterrows():
            render_parish(row)


elif view == "Manual Upload":
    st.subheader("Manual Bulletin Upload")

    st.write(
        "Upload a bulletin PDF without an OpenAI API key. The app will run a simple keyword scan, "
        "show possible events, and save them as manual uploads. You can clean them up later with the Add Event form."
    )

    parish_for_upload = st.selectbox(
        "Parish for this bulletin",
        sorted(parishes_df["parish"].unique()),
        key="upload_parish",
    )

    uploaded_files = st.file_uploader(
        "Upload bulletin PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button("Scan and save possible events"):
        if not uploaded_files:
            st.error("Upload at least one PDF first.")
        else:
            all_found = []
            for pdf in uploaded_files:
                text = extract_text_from_pdf(pdf)
                found = keyword_extract_events(text, parish_for_upload, pdf.name)
                all_found.extend(found)

            added = save_many_events(all_found)
            st.success(f"Saved {added} possible manual events to {DATA_FILE}.")

            if all_found:
                st.write("Preview:")
                for event in all_found[:8]:
                    render_event(pd.Series(event))


elif view == "Add Event":
    st.subheader("Add a Manual Event")

    with st.form("manual_event_form"):
        parish = st.selectbox("Parish", sorted(parishes_df["parish"].unique()))
        title = st.text_input("Event title")
        date_label = st.text_input("Date", placeholder="Example: Saturday, May 23, 2026")
        time = st.text_input("Time", placeholder="Example: 9:00 AM – 11:45 AM")
        location = st.text_input("Location")
        category_value = st.selectbox("Category", CATEGORY_OPTIONS[1:])
        description = st.text_area("Description")
        source_url = st.text_input("Bulletin/source URL", placeholder="Optional")
        submitted = st.form_submit_button("Save event")

    if submitted:
        if not title:
            st.error("Please add an event title.")
        else:
            save_manual_event({
                "title": title,
                "date_label": date_label,
                "time": time,
                "location": location,
                "category": category_value,
                "description": description,
                "parish": parish,
                "source": "Manual website entry",
                "source_url": source_url,
            })
            st.success("Event saved. Go to Events to see it.")
