"""
Communio Bulletin Scraper for the Diocese of Palm Beach

What this does:
1. Reads the diocesan parish directory page.
2. Finds each parish website.
3. Searches each parish website for a bulletin page or recent bulletin PDF.
4. Downloads readable bulletin PDFs.
5. Extracts event-like items from the bulletin text.
6. Saves normalized events to events_data.json for the Streamlit website.

Security note:
- Do NOT hardcode your OpenAI API key in this file.
- Optional AI extraction uses OPENAI_API_KEY from your environment or Streamlit secrets.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import pandas as pd
import pdfplumber
import requests
from bs4 import BeautifulSoup

try:
    from openai import OpenAI
except Exception:  # lets the app run without OpenAI installed/configured
    OpenAI = None

PARISHES_URL = "https://www.diocesepb.org/parishes/parishes.html"
OUTPUT_JSON = Path("events_data.json")
BULLETIN_DIR = Path("bulletins")
CACHE_DIR = Path("scraper_cache")

HEADERS = {
    "User-Agent": "Communio parish bulletin event browser (+contact parish office if needed) Mozilla/5.0"
}

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
]

BULLETIN_KEYWORDS = [
    "bulletin",
    "bulletins",
    "weekly bulletin",
    "parish bulletin",
    "publications",
    "news",
]

EVENT_KEYWORDS = [
    "mass", "confession", "adoration", "holy hour", "rosary", "bible study", "study",
    "youth", "young adult", "family", "marriage", "retreat", "mission", "fundraiser",
    "breakfast", "dinner", "festival", "fellowship", "service", "charity", "drive",
    "open house", "formation", "class", "meeting", "ministry", "prayer", "novena",
]

DATE_WORDS = r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon\.?|Tue\.?|Tues\.?|Wed\.?|Thu\.?|Thur\.?|Fri\.?|Sat\.?|Sun\.?)"
MONTH_WORDS = r"(?:Jan\.?|January|Feb\.?|February|Mar\.?|March|Apr\.?|April|May|Jun\.?|June|Jul\.?|July|Aug\.?|August|Sep\.?|Sept\.?|September|Oct\.?|October|Nov\.?|November|Dec\.?|December)"
TIME_RE = r"(?:\d{1,2}(?::\d{2})?\s*(?:a\.m\.|p\.m\.|am|pm|AM|PM)|Noon|Midnight)"


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_name(value: str) -> str:
    value = clean_text(value).replace("†", "")
    value = value.replace("Saint ", "St. ").replace("Saint", "St.")
    value = value.replace("Cathedral of Saint", "Cathedral of St.")
    return clean_text(value.lower())


def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")[:120] or "bulletin"


def infer_category(text: str) -> str:
    t = (text or "").lower()
    if any(w in t for w in ["mass", "holy thursday", "good friday", "easter vigil", "requiem"]):
        return "Liturgy / Mass"
    if any(w in t for w in ["adoration", "holy hour", "blessed sacrament"]):
        return "Adoration"
    if any(w in t for w in ["confession", "reconciliation", "rosary", "stations of the cross", "prayer", "novena"]):
        return "Confession / Prayer"
    if "retreat" in t or "mission" in t:
        return "Retreat"
    if any(w in t for w in ["youth", "young adult", "teen"]):
        return "Youth / Young Adult"
    if any(w in t for w in ["marriage", "family", "wedding", "parent"]):
        return "Marriage / Family"
    if any(w in t for w in ["school", "open house", "academy"]):
        return "School / Open House"
    if any(w in t for w in ["charity", "charities", "drive", "families in need", "food pantry", "service", "donation"]):
        return "Service / Charity"
    if any(w in t for w in ["bible study", "formation", "class", "theology", "catechism", "rcia", "ocia", "study"]):
        return "Adult Formation"
    if any(w in t for w in ["social", "fellowship", "festival", "breakfast", "dinner", "coffee", "bingo"]):
        return "Social / Fellowship"
    if any(w in t for w in ["christmas", "advent", "lent", "easter", "holy day", "pentecost", "assumption"]):
        return "Holiday / Holy Day"
    return "Adult Formation"


def request_url(url: str, timeout: int = 25) -> requests.Response:
    response = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    return response


def fetch_parishes() -> pd.DataFrame:
    response = request_url(PARISHES_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text("\n")
    lines = [clean_text(x) for x in text.splitlines() if clean_text(x)]

    deanery_names = {"Northern Deanery", "Cathedral Deanery", "Central Deanery", "Southern Deanery"}
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
            city = re.sub(r"\bFL\s+\d{5}\b", "", parts[-1]).strip(" ,") if len(parts) >= 2 else ""
            rows.append({"parish": parish, "city": city, "deanery": current_deanery or "Unknown", "phone": phone})
        i += 1

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["parish", "city", "deanery", "phone", "website"])

    website_map = {}
    for a in soup.find_all("a", href=True):
        name = clean_text(a.get_text(" ", strip=True)).replace("†", "")
        href = a["href"].strip()
        if not name or href.startswith(("mailto:", "javascript:")):
            continue
        website_map.setdefault(name, urljoin(PARISHES_URL, href))

    df["website"] = df["parish"].map(website_map).fillna("")
    return df[df["parish"] != ""].drop_duplicates(subset=["parish"]).reset_index(drop=True)


def same_domain(url_a: str, url_b: str) -> bool:
    a = urlparse(url_a).netloc.lower().replace("www.", "")
    b = urlparse(url_b).netloc.lower().replace("www.", "")
    return a == b


def looks_like_pdf(url: str) -> bool:
    path = urlparse(url).path.lower()
    return path.endswith(".pdf") or ".pdf" in path


def score_bulletin_link(text: str, href: str) -> int:
    joined = f"{text} {href}".lower()
    score = 0
    for kw in BULLETIN_KEYWORDS:
        if kw in joined:
            score += 10
    if looks_like_pdf(href):
        score += 8
    if any(w in joined for w in ["latest", "current", "week", "2026", "2025"]):
        score += 2
    return score


def find_bulletin_candidates(parish_website: str, max_pages: int = 8) -> list[str]:
    if not parish_website:
        return []

    queue = [parish_website]
    seen = set()
    candidates = []

    # Try common bulletin paths first.
    base = parish_website.rstrip("/") + "/"
    queue.extend(urljoin(base, path) for path in ["bulletin", "bulletins", "parish-bulletin", "weekly-bulletin", "publications"])

    while queue and len(seen) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            response = request_url(url, timeout=20)
        except Exception:
            continue

        content_type = response.headers.get("content-type", "").lower()
        final_url = response.url
        if "pdf" in content_type or looks_like_pdf(final_url):
            candidates.append(final_url)
            continue
        if "html" not in content_type and "text" not in content_type:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = urljoin(final_url, a["href"].strip())
            text = clean_text(a.get_text(" ", strip=True))
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            if not same_domain(href, final_url) and not looks_like_pdf(href):
                # many parishes host PDFs on same domain or on eCatholic/CDN; keep PDFs only off-domain
                continue
            score = score_bulletin_link(text, href)
            if score > 0:
                links.append((score, href))
        links.sort(reverse=True, key=lambda x: x[0])
        for _, href in links[:10]:
            if looks_like_pdf(href):
                candidates.append(href)
            elif href not in seen and href not in queue:
                queue.append(href)

    # de-dupe while keeping order
    deduped = []
    for c in candidates:
        if c not in deduped:
            deduped.append(c)
    return deduped[:5]


def download_pdf(url: str, parish_name: str) -> Path | None:
    try:
        response = request_url(url, timeout=30)
        content_type = response.headers.get("content-type", "").lower()
        if "pdf" not in content_type and not looks_like_pdf(response.url):
            return None
        BULLETIN_DIR.mkdir(exist_ok=True)
        digest = hashlib.md5(response.url.encode()).hexdigest()[:10]
        filename = BULLETIN_DIR / f"{safe_filename(parish_name)}_{datetime.now().strftime('%Y%m%d')}_{digest}.pdf"
        filename.write_bytes(response.content)
        return filename
    except Exception as exc:
        print(f"   ❌ PDF download failed: {exc}")
        return None


def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                text += page_text + "\n"
    except Exception as exc:
        print(f"   ⚠️ Could not extract text from {pdf_path.name}: {exc}")
    return text


def candidate_event_lines(text: str) -> list[str]:
    raw_lines = [clean_text(x) for x in text.splitlines() if clean_text(x)]
    lines = []
    for line in raw_lines:
        if len(line) < 8 or len(line) > 220:
            continue
        lower = line.lower()
        has_keyword = any(k in lower for k in EVENT_KEYWORDS)
        has_time = re.search(TIME_RE, line, re.I) is not None
        has_date = re.search(DATE_WORDS, line, re.I) is not None or re.search(MONTH_WORDS + r"\s+\d{1,2}", line, re.I) is not None
        if has_keyword and (has_time or has_date):
            lines.append(line)
    return lines[:80]


def fallback_extract_events(text: str, parish_name: str, bulletin_url: str) -> list[dict]:
    events = []
    for line in candidate_event_lines(text):
        time_match = re.search(TIME_RE, line, re.I)
        dow_match = re.search(DATE_WORDS, line, re.I)
        date_match = re.search(MONTH_WORDS + r"\s+\d{1,2}(?:,\s*\d{4})?", line, re.I)
        date_label = clean_text(date_match.group(0) if date_match else dow_match.group(0) if dow_match else "See bulletin")
        time_label = clean_text(time_match.group(0) if time_match else "See bulletin")
        title = line
        # remove leading dates/times to make a cleaner title
        title = re.sub(DATE_WORDS + r"[:,]?\s*", "", title, flags=re.I)
        title = re.sub(MONTH_WORDS + r"\s+\d{1,2}(?:,\s*\d{4})?[:,]?\s*", "", title, flags=re.I)
        title = re.sub(TIME_RE, "", title, flags=re.I)
        title = clean_text(title.strip(" -–—|:;")) or line
        event_id = hashlib.md5(f"{parish_name}|{title}|{date_label}|{time_label}".encode()).hexdigest()
        events.append({
            "id": event_id,
            "title": title[:140],
            "date_label": date_label,
            "time": time_label,
            "location": parish_name,
            "category": infer_category(line),
            "parish": parish_name,
            "description": line,
            "source_url": bulletin_url,
            "source_type": "bulletin",
            "date_added": datetime.now(timezone.utc).isoformat(),
        })
    return events


def extract_events_with_ai(text: str, parish_name: str, bulletin_url: str) -> list[dict]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or OpenAI is None:
        return []

    prompt = f"""
Extract Catholic parish events from this bulletin text for {parish_name}.
Return only valid JSON array. Use these exact category labels: {CATEGORY_OPTIONS}.
Each item must have: title, date_label, time, location, category, description.
Skip Mass intention names unless they are a public event. Keep events useful for a public parish event website.

Bulletin text:
{text[:12000]}
"""
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You extract structured event listings from Catholic parish bulletins. Return JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        raw = response.choices[0].message.content or "[]"
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        out = []
        for item in parsed if isinstance(parsed, list) else []:
            title = clean_text(str(item.get("title") or item.get("event_name") or ""))
            if not title:
                continue
            event_id = hashlib.md5(f"{parish_name}|{title}|{item.get('date_label','')}|{item.get('time','')}".encode()).hexdigest()
            out.append({
                "id": event_id,
                "title": title[:140],
                "date_label": clean_text(str(item.get("date_label") or item.get("date") or "See bulletin")),
                "time": clean_text(str(item.get("time") or "See bulletin")),
                "location": clean_text(str(item.get("location") or parish_name)),
                "category": item.get("category") if item.get("category") in CATEGORY_OPTIONS else infer_category(title),
                "parish": parish_name,
                "description": clean_text(str(item.get("description") or "")),
                "source_url": bulletin_url,
                "source_type": "bulletin",
                "date_added": datetime.now(timezone.utc).isoformat(),
            })
        return out
    except Exception as exc:
        print(f"   ⚠️ AI extraction failed for {parish_name}: {exc}")
        return []


def load_existing_events(path: Path = OUTPUT_JSON) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}


def save_events_for_parish(parish_name: str, events: list[dict], bulletin_url: str, path: Path = OUTPUT_JSON) -> None:
    data = load_existing_events(path)
    data[parish_name] = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "bulletin_url": bulletin_url,
        "events": events,
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def run_scraper(limit: int | None = None, use_ai: bool = True, sleep_seconds: float = 0.7) -> dict:
    print("=" * 58)
    print("Communio Bulletin Scraper - Diocese of Palm Beach")
    print(datetime.now().strftime("Started: %Y-%m-%d %H:%M:%S"))
    print("=" * 58)

    parishes = fetch_parishes()
    if limit:
        parishes = parishes.head(limit)

    total_events = 0
    processed = 0
    failed = []

    for _, row in parishes.iterrows():
        parish_name = row.get("parish", "")
        website = row.get("website", "")
        print(f"\n⛪ {parish_name}")
        print(f"   Website: {website or 'not listed'}")
        if not website:
            failed.append({"parish": parish_name, "reason": "No website listed"})
            continue

        candidates = find_bulletin_candidates(website)
        if not candidates:
            print("   ⚠️ No bulletin candidates found")
            failed.append({"parish": parish_name, "reason": "No bulletin link found"})
            continue

        parish_events = []
        used_url = candidates[0]
        for bulletin_url in candidates:
            print(f"   Trying bulletin: {bulletin_url}")
            pdf_path = download_pdf(bulletin_url, parish_name)
            if not pdf_path:
                continue
            text = extract_text_from_pdf(pdf_path)
            if len(text) < 100:
                print("   ⚠️ PDF had too little extractable text; it may be scanned images")
                continue
            used_url = bulletin_url
            parish_events = extract_events_with_ai(text, parish_name, bulletin_url) if use_ai else []
            if not parish_events:
                parish_events = fallback_extract_events(text, parish_name, bulletin_url)
            break

        save_events_for_parish(parish_name, parish_events, used_url)
        processed += 1
        total_events += len(parish_events)
        print(f"   ✅ Saved {len(parish_events)} bulletin events")
        time.sleep(sleep_seconds)

    summary = {"processed_parishes": processed, "total_events": total_events, "failed": failed}
    print("\nDone:", summary)
    return summary


if __name__ == "__main__":
    # Use LIMIT_PARISHES=5 for testing.
    limit_value = os.getenv("LIMIT_PARISHES", "").strip()
    limit = int(limit_value) if limit_value.isdigit() else None
    run_scraper(limit=limit, use_ai=os.getenv("USE_AI", "1") != "0")
