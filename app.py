import re
from datetime import date
from urllib.parse import urljoin

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

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

st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
.big-title {
    text-align: center;
    font-size: 3.4rem;
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
.section-header {
    color: #d4a853;
    margin-top: 0.2rem;
}
a {
    text-decoration: none !important;
}
</style>
""", unsafe_allow_html=True)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def infer_category(title: str) -> str:
    t = (title or "").lower()

    if any(word in t for word in ["mass", "requiem", "holy week", "holy thursday", "good friday", "holy saturday", "resurrection", "sunday of easter", "mind mass"]):
        return "Liturgy / Mass"
    if any(word in t for word in ["adoration"]):
        return "Adoration"
    if any(word in t for word in ["confession", "stations of the cross", "rosary", "prayer"]):
        return "Confession / Prayer"
    if any(word in t for word in ["retreat"]):
        return "Retreat"
    if any(word in t for word in ["youth", "young adult"]):
        return "Youth / Young Adult"
    if any(word in t for word in ["marriage", "family", "wedding"]):
        return "Marriage / Family"
    if any(word in t for word in ["school", "open house"]):
        return "School / Open House"
    if any(word in t for word in ["shower", "charities", "drive", "need"]):
        return "Service / Charity"
    if any(word in t for word in ["theology", "saint thomas", "formation", "catechesis", "study"]):
        return "Adult Formation"
    if any(word in t for word in ["festival", "fellowship", "social", "vineyard", "viñedo"]):
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
    main_text = soup.get_text("\n")
    lines = [clean_text(x) for x in main_text.splitlines() if clean_text(x)]

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line == "Parishes in the Diocese of Palm Beach":
            start_idx = i + 1
        if line == "Next section:":
            end_idx = i
            break

    if start_idx is None:
        raise ValueError("Could not find parish section on the Diocese page.")

    working = lines[start_idx:end_idx]
    deanery = None
    rows = []

    deanery_names = {
        "Northern Deanery",
        "Cathedral Deanery",
        "Central Deanery",
        "Southern Deanery",
    }

    for line in working:
        if line in deanery_names:
            deanery = line
            continue

        match = re.match(
            r"^\d+\.\s*(.+?),\s*([A-Za-z .'\-]+?)(?:,\s*FL\s*\d{5})?,\s*(\d{3}-\d{3}-\d{4})",
            line,
        )
        if not match:
            continue

        parish_name = clean_text(match.group(1))
        city = clean_text(match.group(2))
        phone = clean_text(match.group(3))

        rows.append(
            {
                "parish": parish_name,
                "city": city,
                "deanery": deanery or "Unknown",
                "phone": phone,
            }
        )

    # add websites from anchor tags where possible
    website_map = {}
    current_deanery = None
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "p", "li", "a"]):
        text = clean_text(tag.get_text(" ", strip=True))
        if text in deanery_names:
            current_deanery = text

        href = tag.get("href")
        if not href or href.startswith("mailto:"):
            continue

        absolute_href = urljoin(PARISHES_URL, href)
        link_text = clean_text(tag.get_text(" ", strip=True))
        if link_text and not link_text.lower().startswith("image:"):
            website_map[link_text] = absolute_href

    for row in rows:
        row["website"] = website_map.get(row["parish"], "")

    df = pd.DataFrame(rows).drop_duplicates(subset=["parish"]).sort_values(["deanery", "parish"]).reset_index(drop=True)
    return df


def _extract_event_lines(text: str) -> list[str]:
    lines = [clean_text(x) for x in text.splitlines() if clean_text(x)]
    output = []

    date_header_pattern = re.compile(
        r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}$"
    )

    in_daily_listing = False
    for line in lines:
        if date_header_pattern.match(line):
            in_daily_listing = True
            output.append(line)
            continue

        if not in_daily_listing:
            continue

        if line in {"March 2026", "May 2026", "Privacy Policy"}:
            break

        output.append(line)

    return output


@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def fetch_events(year: int, month: int) -> pd.DataFrame:
    url = EVENTS_URL_TEMPLATE.format(year=year, month=month)
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text("\n")
    lines = _extract_event_lines(text)

    date_header_pattern = re.compile(
        r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}$"
    )
    event_line_pattern = re.compile(r"^(.*?)\s+(All Day|\d{1,2}:\d{2}\s*(?:am|pm)\s*-\s*\d{1,2}:\d{2}\s*(?:am|pm))$", re.I)

    rows = []
    current_date = None

    for line in lines:
        if date_header_pattern.match(line):
            current_date = line
            continue

        if current_date is None:
            continue

        line = line.lstrip("* ").strip()

        match = event_line_pattern.match(line)
        if match:
            title = clean_text(match.group(1))
            time_text = clean_text(match.group(2))
            rows.append(
                {
                    "date_label": current_date,
                    "title": title,
                    "time": time_text,
                    "category": infer_category(title),
                    "source_url": url,
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["date_label", "title", "time", "category", "source_url"])

    # crude parish detection from title text
    parishes = fetch_parishes()
    parish_names = parishes["parish"].tolist()

    def detect_parish(title: str) -> str:
        tl = title.lower()
        for parish in parish_names:
            if parish.lower() in tl:
                return parish
        # handle short names in parentheses like (St. Jude - Tequesta)
        for parish in parish_names:
            short = parish.replace("Saint", "St.").replace("Saint ", "St. ").lower()
            if short in tl or parish.lower().replace("saint", "st.") in tl:
                return parish
        return ""

    df["parish"] = df["title"].apply(detect_parish)
    return df


def parish_matches_search(row: pd.Series, query: str) -> bool:
    if not query:
        return True
    haystack = " ".join(
        [
            str(row.get("parish", "")),
            str(row.get("city", "")),
            str(row.get("deanery", "")),
            str(row.get("phone", "")),
        ]
    ).lower()
    return query.lower() in haystack


def event_matches_search(row: pd.Series, query: str) -> bool:
    if not query:
        return True
    haystack = " ".join(
        [
            str(row.get("title", "")),
            str(row.get("date_label", "")),
            str(row.get("time", "")),
            str(row.get("category", "")),
            str(row.get("parish", "")),
        ]
    ).lower()
    return query.lower() in haystack


def render_parish_card(row: pd.Series):
    st.markdown('<div class="parish-card">', unsafe_allow_html=True)
    left, right = st.columns([5, 1.6])
    with left:
        st.markdown(f"### {row['parish']}")
        st.markdown(
            f"<span class='badge'>{row['deanery']}</span>"
            f"<span class='badge'>{row['city']}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='small-muted'>📞 {row['phone']}</div>",
            unsafe_allow_html=True,
        )
        if row.get("website"):
            st.markdown(f"[Visit parish website]({row['website']})")
    with right:
        if st.button("Show events", key=f"show_{row['parish']}"):
            st.session_state["selected_parish"] = row["parish"]
    st.markdown("</div>", unsafe_allow_html=True)


def render_event_card(row: pd.Series):
    st.markdown(
        f"""
        <div class="event-card">
            <div class="small-muted">{row['date_label']} · {row['time']}</div>
            <div style="font-size:1.15rem;font-weight:700;margin:0.35rem 0 0.45rem 0;">{row['title']}</div>
            <span class="badge">{row['category']}</span>
            {"<span class='badge'>" + row['parish'] + "</span>" if row.get("parish") else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Header
st.markdown('<div class="big-title">⛪ COMMUNIO</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Diocese of Palm Beach · Parish Directory + Live Monthly Event Feed</div>',
    unsafe_allow_html=True,
)

# Sidebar controls
with st.sidebar:
    st.header("Filters")
    view_mode = st.radio("View", ["Dashboard", "Parishes", "Events"], index=0)
    search = st.text_input("Search", placeholder="Parish, event, city, keyword...")
    category = st.selectbox("Event category", CATEGORY_OPTIONS, index=0)
    year = st.number_input("Year", min_value=2024, max_value=2030, value=date.today().year, step=1)
    month = st.selectbox(
        "Month",
        options=list(range(1, 13)),
        format_func=lambda m: date(2000, m, 1).strftime("%B"),
        index=date.today().month - 1,
    )

try:
    parishes_df = fetch_parishes()
except Exception as e:
    st.error(f"Could not load parish data from the diocesan website: {e}")
    st.stop()

try:
    events_df = fetch_events(year, month)
except Exception as e:
    events_df = pd.DataFrame(columns=["date_label", "title", "time", "category", "source_url", "parish"])
    st.warning(f"Event feed could not be loaded right now: {e}")

filtered_parishes = parishes_df[parishes_df.apply(lambda r: parish_matches_search(r, search), axis=1)].copy()
filtered_events = events_df[events_df.apply(lambda r: event_matches_search(r, search), axis=1)].copy()

if category != "All" and not filtered_events.empty:
    filtered_events = filtered_events[filtered_events["category"] == category].copy()

selected_parish = st.session_state.get("selected_parish", "")
if selected_parish:
    filtered_events_for_selected = filtered_events[filtered_events["parish"] == selected_parish].copy()
else:
    filtered_events_for_selected = pd.DataFrame(columns=filtered_events.columns)

# Stats
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><h3>{len(parishes_df)}</h3><p>Total Parishes</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><h3>{parishes_df["deanery"].nunique()}</h3><p>Deaneries</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><h3>{len(events_df)}</h3><p>Events This Month</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><h3>{filtered_events["category"].nunique() if not filtered_events.empty else 0}</h3><p>Visible Categories</p></div>', unsafe_allow_html=True)

st.divider()

if view_mode == "Dashboard":
    left, right = st.columns([1.15, 1])

    with left:
        st.markdown("## Featured parishes")
        for _, row in filtered_parishes.head(10).iterrows():
            render_parish_card(row)

        if len(filtered_parishes) > 10:
            st.info(f"Showing 10 of {len(filtered_parishes)} matching parishes. Open the Parishes view to browse all of them.")

    with right:
        st.markdown("## Upcoming events")
        if filtered_events.empty:
            st.info("No events matched the current filters.")
        else:
            for _, row in filtered_events.head(10).iterrows():
                render_event_card(row)

        if selected_parish:
            st.markdown(f"## Events for {selected_parish}")
            if filtered_events_for_selected.empty:
                st.info("No currently visible events are tagged to this parish from the monthly feed.")
            else:
                for _, row in filtered_events_for_selected.iterrows():
                    render_event_card(row)

elif view_mode == "Parishes":
    st.markdown("## All parishes")
    deanery_filter = st.multiselect(
        "Filter by deanery",
        options=sorted(parishes_df["deanery"].dropna().unique().tolist()),
        default=sorted(parishes_df["deanery"].dropna().unique().tolist()),
    )

    display_df = filtered_parishes[filtered_parishes["deanery"].isin(deanery_filter)].copy()

    if display_df.empty:
        st.info("No parishes matched your search.")
    else:
        for deanery, group in display_df.groupby("deanery"):
            st.markdown(f"### {deanery}")
            for _, row in group.iterrows():
                render_parish_card(row)

else:
    st.markdown("## Monthly event feed")
    st.caption("This view shows events for the selected month from the diocesan calendar page.")

    if filtered_events.empty:
        st.info("No events matched the current filters.")
    else:
        for date_label, group in filtered_events.groupby("date_label", sort=False):
            with st.expander(date_label, expanded=False):
                for _, row in group.iterrows():
                    render_event_card(row)

st.divider()
st.markdown(
    "<p style='text-align:center;color:#8a8a8a;'>Communio · Diocese of Palm Beach · Interactive parish directory and event browser</p>",
    unsafe_allow_html=True,
)
