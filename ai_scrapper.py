"""
AI Event Scraper for Diocese of Palm Beach
This script uses AI to extract events from parish bulletins
"""

import json
import os
import requests
from datetime import datetime, timedelta
import hashlib

# For PDF parsing
import pdfplumber
import PyPDF2

# For AI extraction (using free option)
import openai

# ============================================
# CONFIGURATION
# ============================================

# List of parish bulletin URLs (You'll need to add actual links)
# These are examples - you'll need to find the actual bulletin pages
PARISH_BULLETINS = {
    "Cathedral of St. Ignatius Loyola": "https://www.stignatiuspb.org/bulletins",
    "St. Ann Parish": "https://www.stannpb.org/bulletins",
    "Holy Name of Jesus": "https://www.hnjpb.org/bulletin",
    "St. Joseph Parish (Stuart)": "https://www.stjosephstuart.org/bulletins",
    "St. Lucie Parish": "https://www.stlucieparish.org/bulletin",
    "St. Anastasia": "https://www.stanastasia.org/bulletins",
    "Holy Cross (Indiantown)": "https://www.holycrosscc.org/bulletins"
}

# OpenAI API Key (you'll need to add yours)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "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"  # <-- YOU NEED TO ADD THIS

# ============================================
# AI PROMPT FOR EVENT EXTRACTION
# ============================================

EVENT_EXTRACTION_PROMPT = """
You are an AI that extracts Catholic parish events from bulletin text.

From the bulletin text below, extract all events happening in the coming week.

For each event, provide:
- event_name: The name of the event
- date: When it happens (day of week or specific date)
- time: What time it starts
- location: Where in the parish it happens
- category: Choose from: Mass, Confession, Adoration, Bible Study, Youth, Family, Retreat, Service, Fundraiser, Social, Other
- description: A short 1-sentence description

Return ONLY a JSON array. Example format:
[
    {
        "event_name": "Eucharistic Adoration",
        "date": "Friday",
        "time": "6:30 PM",
        "location": "Main Church",
        "category": "Adoration",
        "description": "Hour of silent prayer before the Blessed Sacrament"
    }
]

If no events found, return an empty array [].

Bulletin text:
"""

# ============================================
# FUNCTIONS
# ============================================

def download_bulletin(url, parish_name):
    """Download a bulletin PDF from a URL"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Create bulletins folder if it doesn't exist
            os.makedirs("bulletins", exist_ok=True)
            
            # Create a safe filename
            safe_name = parish_name.replace(" ", "_").replace("(", "").replace(")", "")
            filename = f"bulletins/{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print(f"Failed to download {parish_name}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading {parish_name}: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text

def extract_events_with_ai(bulletin_text, parish_name):
    """Use AI to extract events from bulletin text"""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_API_KEY_HERE":
        print(f"⚠️ No API key set. Skipping AI extraction for {parish_name}")
        return []
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Truncate text if too long (keep last ~4000 characters where events usually are)
        if len(bulletin_text) > 4000:
            bulletin_text = bulletin_text[-4000:]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You extract events from Catholic church bulletins. Return only JSON."},
                {"role": "user", "content": EVENT_EXTRACTION_PROMPT + bulletin_text}
            ],
            temperature=0.3
        )
        
        # Parse the response
        events_text = response.choices[0].message.content
        # Clean up the response (remove markdown code blocks if present)
        events_text = events_text.replace("```json", "").replace("```", "")
        events = json.loads(events_text)
        return events
    except Exception as e:
        print(f"Error with AI extraction for {parish_name}: {e}")
        return []

def save_events(parish_name, events):
    """Save extracted events to the master JSON file"""
    # Load existing events
    if os.path.exists("events_data.json"):
        with open("events_data.json", "r") as f:
            all_events = json.load(f)
    else:
        all_events = {}
    
    # Add timestamp
    for event in events:
        event["parish"] = parish_name
        event["date_added"] = datetime.now().isoformat()
        # Create a unique ID for each event
        event_id = hashlib.md5(f"{parish_name}{event['event_name']}{event['date']}".encode()).hexdigest()
        event["id"] = event_id
    
    all_events[parish_name] = {
        "last_updated": datetime.now().isoformat(),
        "events": events
    }
    
    # Save back
    with open("events_data.json", "w") as f:
        json.dump(all_events, f, indent=2)
    
    print(f"✅ Saved {len(events)} events for {parish_name}")

def run_scraper():
    """Main function to run the AI scraper"""
    print("=" * 50)
    print("🤖 AI Event Scraper - Diocese of Palm Beach")
    print(f"📅 Running on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    total_events = 0
    
    for parish_name, url in PARISH_BULLETINS.items():
        print(f"\n📋 Processing: {parish_name}")
        
        # Step 1: Download bulletin
        print(f"   📥 Downloading from {url}...")
        pdf_path = download_bulletin(url, parish_name)
        
        if not pdf_path:
            print(f"   ❌ Could not download bulletin")
            continue
        
        # Step 2: Extract text
        print(f"   📄 Extracting text from PDF...")
        bulletin_text = extract_text_from_pdf(pdf_path)
        
        if len(bulletin_text) < 100:
            print(f"   ⚠️ Very little text extracted (might be scanned PDF)")
            continue
        
        # Step 3: Use AI to extract events
        print(f"   🧠 Using AI to extract events...")
        events = extract_events_with_ai(bulletin_text, parish_name)
        
        if events:
            # Step 4: Save events
            save_events(parish_name, events)
            total_events += len(events)
            print(f"   ✅ Extracted {len(events)} events")
            
            # Print preview
            for event in events[:2]:  # Show first 2 events
                print(f"      - {event.get('event_name', 'Unknown')} ({event.get('category', 'Other')})")
        else:
            print(f"   ⚠️ No events found")
    
    print("\n" + "=" * 50)
    print(f"🎉 SCRAPING COMPLETE!")
    print(f"📊 Total events extracted: {total_events}")
    print("=" * 50)

# ============================================
# RUN THE SCRAPER
# ============================================
if __name__ == "__main__":
    run_scraper()
