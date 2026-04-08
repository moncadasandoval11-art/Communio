import re
from datetime import date
from urllib.parse import urljoin

import pandas as pd
import requests
import streamlit as st

try:
    from bs4 import BeautifulSoup
except ImportError:
    st.error("Missing dependency: beautifulsoup4. Add it to requirements.txt and redeploy.")
    st.stop()

st.set_page_config(page_title="Communio", page_icon="⛪", layout="wide")

PARISHES_URL = "https://www.diocesepb.org/parishes/parishes.html"
EVENTS_URL_TEMPLATE = "https://www.diocesepb.org/news/events.html/calendar/{year}/{month}"

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
]

st.markdown(
    """
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
.big-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 800;
    color: #d4a853;
    margin-bottom: 0;
}
.subtitle {
    text-align: center;
    font-size: 1.05rem;
    color: #bfbfbf;
    margin-top: 0.15rem;
    margin-bottom: 1rem;
}
.stat-card {
    background: linear-gradient(135deg, #d4a853 0%, #f0cf8d 100%);
    color: #111;
    padding: 1rem;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}
.event-card {
    background-color: #17171d;
    border-radius: 14px;
    padding: 1rem 1rem 0.8rem 1rem;
    margin-bottom: 0.9rem;
    border-left: 5px solid #d4a853;
}
.parish-card {
    background-color: #17171d;
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    border: 1px solid rgba(212,168,83,0.20);
}
.small-muted {
    color: #bfbfbf;
    font-size: 0.92rem;
}
.badge {
    display: inline-block;
    padding: 0.25rem 0.55rem;
    border-radius: 999px;
    background: rgba(212,168,83,0.18);
    border: 1px solid rgba(212,168,83,0.35);
    margin-right: 0.35rem;
    margin-bottom: 0.35rem;
    font-size: 0.82rem;
}
a {
    text-decoration: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_name(value: str) -> str:
    value = clean_text(value).replace("†", "")
    value = value.replace("Saint ", "St. ")
    value = value.replace("Saint", "St.")
    value = value.replace("Cathedral of Saint", "Cathedral of St.")
    return clean_text(value.lower())


def infer_category(title: str) -> str:
    t = (title or "").lower()

    if any(word in t for word in ["mass", "requiem", "holy week", "holy thursday", "good friday", "holy saturday", "resurrection", "easter vigil"]):
        return "Liturgy / Mass"
    if "adoration" in t:
        return "Adoration"
    if any(word in t for word in ["confession", "stations of the cross", "rosary", "prayer"]):
        return "Confession / Prayer"
    if "retreat" in t:
        return "Retreat"
    if any(word in t for word in ["youth", "young adult"]):
        return "Youth / Young Adult"
    if any(word in t for word in ["marriage", "family", "wedding"]):
        return "Marriage / Family"
    if any(word in t for word in ["school", "open house"]):
        return "School / Open House"
    if any(word in t for word in ["charities", "baby shower", "families in need", "drive"]):
        return "Service / Charity"
    if any(word in t for word in ["theology", "saint thomas", "formation", "study", "tour"]):
        return "Adult Formation"
    if any(word in t for word in ["vineyard", "viñedo", "social", "fellowship", "festival"]):
        return "Social / Fellowship"
    if any(word in t for word in ["easter", "christmas", "advent", "pentecost", "holy day"]):
        return "Holiday / Holy Day"

    return "Adult Formation"


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_parishes() -> pd.DataFrame:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(PARISHES_URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text("\n")
    lines = [clean_text(x) for x in text.splitlines() if clean_text(x)]

    deanery_names = {
        "Northern Deanery",
        "Cathedral Deanery",
        "Central Deanery",
        "Southern Deanery",
    }

    rows = []
    current_deanery = None

    i = 0
    while i < len(lines):
        line = lines[i].replace("†", "").strip()

        if line in deanery_names:
            current_deanery = line
            i += 1
            continue

        if re.match(r"^\d+\.", line):
            combined = line

            while i + 1 < len(lines):
                nxt = lines[i + 1].replace("†", "").strip()
                if re.match(r"^\d+\.", nxt) or nxt in deanery_names or nxt == "Next section:":
                    break
                combined += " " + nxt
                i += 1

            combined = re.sub(r"^\d+\.\s*", "", combined).strip()
            main_part = combined.split("Email:")[0].strip()

            phone_match = re.search(r"(\d{3}-\d{3}-\d{4})", main_part)
            phone = phone_match.group(1) if phone_match else ""
            if phone:
                main_part = main_part.replace(phone, "").strip(" ,")

            parts = [p.strip() for p in main_part.split(",") if p.strip()]
            parish = parts[0] if parts else ""
            city = ""

            if len(parts) >= 2:
                city = parts[-1]
                city = re.sub(r"\bFL\s+\d{5}\b", "", city).strip(" ,")

            rows.append(
                {
                    "parish": parish,
                    "city": city,
                    "deanery": current_deanery or "Unknown",
                    "phone": phone,
                }
            )

        i += 1

    df = pd.DataFrame(rows)

    for col in ["parish", "city", "deanery", "phone"]:
        if col not in df.columns:
            df[col] = ""

    website_map = {}
    for a in soup.find_all("a", href=True):
        name = clean_text(a.get_text(" ", strip=True)).replace("†", "").strip()
        href = a["href"].strip()
        if not name or not href or href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        full_url = urljoin(PARISHES_URL, href)
        website_map.setdefault(name, full_url)

    df["website"] = df["parish"].map(website_map).fillna("")
    df = df[df["parish"] != ""].drop_duplicates(subset=["parish"]).sort_values(["deanery", "parish"]).reset_index(drop=True)
    return df


def _extract_event_lines(text: str) -> list[str]:
    lines = [clean_text(x) for x in text.splitlines() if clean_text(x)]
    out = []
    date_header_pattern = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}$")

    started = False
    for line in lines:
        if date_header_pattern.match(line):
            started = True
            out.append(line)
            continue
        if started:
            out.append(line)
    return out


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def fetch_events(year: int, month: int, parish_names: list[str]) -> pd.DataFrame:
    url = EVENTS_URL_TEMPLATE.format(year=year, month=month)
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    lines = _extract_event_lines(soup.get_text("\n"))

    date_header_pattern = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}$")
    event_line_pattern = re.compile(
        r"^(.*?)\s+(All Day|\d{1,2}:\d{2}\s*(?:am|pm)\s*-\s*\d{1,2}:\d{2}\s*(?:am|pm)|\d{1,2}:\d{2}\s*(?:am|pm))$",
        re.I,
    )

    normalized_map = {normalize_name(p): p for p in parish_names}
    rows = []
    current_date = None

    def detect_parish(title: str) -> str:
        title_norm = normalize_name(title)
        for norm_name, original in normalized_map.items():
            if norm_name and norm_name in title_norm:
                return original

        # handles event titles like "(St. Jude - Tequesta)"
        abbreviated = {
            normalize_name(p.replace("Saint ", "St. ").replace("Saint", "St.")): p
            for p in parish_names
        }
        for norm_name, original in abbreviated.items():
            if norm_name and norm_name in title_norm:
                return original
        return ""

    for line in lines:
        if date_header_pattern.match(line):
            current_date = line
            continue

        if current_date is None:
            continue

        line = line.lstrip("* ").strip()
        match = event_line_pattern.match(line)
        if not match:
            continue

        title = clean_text(match.group(1))
        time_text = clean_text(match.group(2))

        rows.append(
            {
                "date_label": current_date,
                "title": title,
                "time": time_text,
                "category": infer_category(title),
                "parish": detect_parish(title),
                "source_url": url,
            }
        )

    if not rows:
        return pd.DataFrame(columns=["date_label", "title", "time", "category", "parish", "source_url"])

    return pd.DataFrame(rows)


def parish_matches_search(row: pd.Series, query: str) -> bool:
    if not query:
        return True
    haystack = " ".join(
        [str(row.get("parish", "")), str(row.get("city", "")), str(row.get("deanery", "")), str(row.get("phone", ""))]
    ).lower()
    return query.lower() in haystack


def event_matches_search(row: pd.Series, query: str) -> bool:
    if not query:
        return True
    haystack = " ".join(
        [str(row.get("title", "")), str(row.get("date_label", "")), str(row.get("time", "")), str(row.get("category", "")), str(row.get("parish", ""))]
    ).lower()
    return query.lower() in haystack


def render_parish_card(row: pd.Series):
    st.markdown('<div class="parish-card">', unsafe_allow_html=True)
    left, right = st.columns([5, 1.5])
    with left:
        st.markdown(f"### {row['parish']}")
        st.markdown(
            f"<span class='badge'>{row['deanery']}</span><span class='badge'>{row['city']}</span>",
            unsafe_allow_html=True,
        )
        if row["phone"]:
            st.markdown(f"<div class='small-muted'>📞 {row['phone']}</div>", unsafe_allow_html=True)
        if row["website"]:
            st.markdown(f"[Visit parish website]({row['website']})")
    with right:
        if st.button("Show events", key=f"show_{row['parish']}"):
            st.session_state["selected_parish"] = row["parish"]
    st.markdown("</div>", unsafe_allow_html=True)


def render_event_card(row: pd.Series):
    parish_badge = f"<span class='badge'>{row['parish']}</span>" if row.get("parish") else ""
    st.markdown(
        f"""
        <div class="event-card">
            <div class="small-muted">{row['date_label']} · {row['time']}</div>
            <div style="font-size:1.12rem;font-weight:700;margin:0.35rem 0 0.45rem 0;">{row['title']}</div>
            <span class="badge">{row['category']}</span>
            {parish_badge}
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown('<div class="big-title">⛪ COMMUNIO</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Diocese of Palm Beach · Interactive Parish Directory and Event Browser</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filters")
    view_mode = st.radio("View", ["Dashboard", "Parishes", "Events"], index=0)
    search = st.text_input("Search", placeholder="Parish, city, event, keyword...")
    category = st.selectbox("Event category", CATEGORY_OPTIONS, index=0)
    year = st.number_input("Year", min_value=2024, max_value=2030, value=date.today().year, step=1)
    month = st.selectbox(
        "Month",
        options=list(range(1, 13)),
        format_func=lambda m: date(2000, m, 1).strftime("%B"),
        index=date.today().month - 1,
    )
    if st.button("Clear selected parish"):
        st.session_state["selected_parish"] = ""

try:
    parishes_df = fetch_parishes()
except Exception as e:
    st.error(f"Could not load parish data from the diocesan website: {e}")
    st.stop()

if parishes_df.empty:
    st.error("No parish data was parsed from the diocesan website.")
    st.stop()

try:
    events_df = fetch_events(year, month, parishes_df["parish"].tolist())
except Exception as e:
    events_df = pd.DataFrame(columns=["date_label", "title", "time", "category", "parish", "source_url"])
    st.warning(f"Could not load the diocesan event calendar right now: {e}")

filtered_parishes = parishes_df[parishes_df.apply(lambda r: parish_matches_search(r, search), axis=1)].copy()
filtered_events = events_df[events_df.apply(lambda r: event_matches_search(r, search), axis=1)].copy()

if category != "All" and not filtered_events.empty:
    filtered_events = filtered_events[filtered_events["category"] == category].copy()

selected_parish = st.session_state.get("selected_parish", "")
if selected_parish:
    filtered_events_for_selected = filtered_events[filtered_events["parish"] == selected_parish].copy()
else:
    filtered_events_for_selected = pd.DataFrame(columns=filtered_events.columns)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><h3>{len(parishes_df)}</h3><p>Total Parishes</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><h3>{parishes_df["deanery"].nunique()}</h3><p>Deaneries</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><h3>{len(events_df)}</h3><p>Events This Month</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><h3>{len(filtered_parishes)}</h3><p>Visible Parishes</p></div>', unsafe_allow_html=True)

st.divider()

if view_mode == "Dashboard":
    left, right = st.columns([1.15, 1])

    with left:
        st.subheader("Parishes")
        for _, row in filtered_parishes.head(12).iterrows():
            render_parish_card(row)
        if len(filtered_parishes) > 12:
            st.info(f"Showing 12 of {len(filtered_parishes)} matching parishes.")

    with right:
        st.subheader("Upcoming events")
        if filtered_events.empty:
            st.info("No events matched the current filters.")
        else:
            for _, row in filtered_events.head(12).iterrows():
                render_event_card(row)

        if selected_parish:
            st.subheader(f"Events for {selected_parish}")
            if filtered_events_for_selected.empty:
                st.info("No currently visible events were matched to this parish.")
            else:
                for _, row in filtered_events_for_selected.iterrows():
                    render_event_card(row)

elif view_mode == "Parishes":
    st.subheader("All parishes")
    deanery_options = sorted(parishes_df["deanery"].dropna().unique().tolist())
    deanery_filter = st.multiselect("Filter by deanery", options=deanery_options, default=deanery_options)

    display_df = filtered_parishes[filtered_parishes["deanery"].isin(deanery_filter)].copy()

    if display_df.empty:
        st.info("No parishes matched your search.")
    else:
        for deanery, group in display_df.groupby("deanery"):
            st.markdown(f"### {deanery}")
            for _, row in group.iterrows():
                render_parish_card(row)

else:
    st.subheader("Monthly diocesan events")
    st.caption("Browse the official diocesan event calendar by month and category.")
    if filtered_events.empty:
        st.info("No events matched the current filters.")
    else:
        for date_label, group in filtered_events.groupby("date_label", sort=False):
            with st.expander(date_label):
                for _, row in group.iterrows():
                    render_event_card(row)

st.divider()
st.markdown(
    "<p style='text-align:center;color:#8a8a8a;'>Communio · Diocese of Palm Beach · Built with Streamlit</p>",
    unsafe_allow_html=True,
)
