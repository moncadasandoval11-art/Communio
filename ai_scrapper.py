"""
Communio AI Bulletin Scraper (FULL VERSION)
- Finds ALL parishes from Diocese of Palm Beach
- Gets parish websites
- Finds bulletin PDFs (website OR DiscoverMass fallback)
- Extracts text
- Uses AI to extract categorized events
"""

import os
import re
import json
import requests
from datetime import datetime
from urllib.parse import urljoin
import hashlib

import pdfplumber
from bs4 import BeautifulSoup
import openai

# ============================================
# CONFIG
# ============================================

PARISHES_URL = "https://www.diocesepb.org/parishes/parishes.html"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ============================================
# AI PROMPT
# ============================================

EVENT_PROMPT = """
Extract Catholic parish events.

Return JSON list:
[
  {
    "event_name": "",
    "date": "",
    "time": "",
    "location": "",
    "category": "Mass | Confession | Adoration | Bible Study | Youth | Family | Retreat | Service | Fundraiser | Social | Other",
    "description": ""
  }
]

Text:
"""

# ============================================
# STEP 1: GET PARISHES
# ============================================

def get_parishes():
    res = requests.get(PARISHES_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    parishes = []

    for a in soup.find_all("a", href=True):
        name = a.get_text(strip=True)
        link = urljoin(PARISHES_URL, a["href"])

        if name and "http" in link:
            parishes.append({
                "name": name,
                "website": link
            })

    return parishes

# ============================================
# STEP 2: FIND BULLETIN ON WEBSITE
# ============================================

def find_bulletin_from_site(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(" ", strip=True).lower()

            if "bulletin" in text or "bulletin" in href:
                return urljoin(url, a["href"])

    except:
        return None

    return None

# ============================================
# STEP 3: DISCOVERMASS SEARCH
# ============================================

def find_discovermass_page(parish_name):
    query = f"{parish_name} Palm Beach FL DiscoverMass"

    res = requests.get(
        "https://www.google.com/search",
        params={"q": query},
        headers=HEADERS
    )

    matches = re.findall(r"https://discovermass\.com/church/[^&\"'> ]+", res.text)
    return matches[0] if matches else None

def find_discovermass_pdf(url):
    try:
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if ".pdf" in href.lower():
                return urljoin(url, href)

    except:
        return None

    return None

# ============================================
# STEP 4: DOWNLOAD PDF
# ============================================

def download_pdf(url, name):
    os.makedirs("bulletins", exist_ok=True)

    safe = re.sub(r"[^a-zA-Z0-9]", "_", name)
    file_path = f"bulletins/{safe}.pdf"

    try:
        res = requests.get(url, headers=HEADERS, timeout=20)
        with open(file_path, "wb") as f:
            f.write(res.content)
        return file_path
    except:
        return None

# ============================================
# STEP 5: EXTRACT TEXT
# ============================================

def extract_text(pdf):
    text = ""
    try:
        with pdfplumber.open(pdf) as p:
            for page in p.pages:
                text += page.extract_text() or ""
    except:
        pass
    return text

# ============================================
# STEP 6: AI EVENT EXTRACTION
# ============================================

def extract_events(text):
    if not OPENAI_API_KEY:
        return []

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    text = text[-4000:]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": EVENT_PROMPT + text}
        ],
        temperature=0.2
    )

    try:
        return json.loads(response.choices[0].message.content)
    except:
        return []

# ============================================
# STEP 7: SAVE
# ============================================

def save(parish, events):
    data = {}

    if os.path.exists("events_data.json"):
        data = json.load(open("events_data.json"))

    for e in events:
        e["parish"] = parish
        e["id"] = hashlib.md5((parish + e["event_name"]).encode()).hexdigest()

    data[parish] = events

    with open("events_data.json", "w") as f:
        json.dump(data, f, indent=2)

# ============================================
# MAIN PIPELINE
# ============================================

def run():
    parishes = get_parishes()

    for p in parishes:
        name = p["name"]
        print(f"\n⛪ {name}")

        bulletin = find_bulletin_from_site(p["website"])

        # 🔁 FALLBACK TO DISCOVERMASS
        if not bulletin:
            print("   → Trying DiscoverMass...")
            dm_page = find_discovermass_page(name)

            if dm_page:
                bulletin = find_discovermass_pdf(dm_page)

        if not bulletin:
            print("   ❌ No bulletin found")
            continue

        print(f"   📥 {bulletin}")

        pdf = download_pdf(bulletin, name)
        if not pdf:
            print("   ❌ Download failed")
            continue

        text = extract_text(pdf)
        if len(text) < 100:
            print("   ⚠️ Empty text")
            continue

        events = extract_events(text)

        print(f"   ✅ {len(events)} events found")

        save(name, events)

    print("\n🎉 DONE")

# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    run()
