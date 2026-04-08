import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import os

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Communio - Diocese of Palm Beach",
    page_icon="⛪",
    layout="wide"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 3rem;
        color: #2B4F2B;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .event-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2B4F2B;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .event-card:hover {
        transform: translateY(-2px);
    }
    .parish-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2B4F2B;
    }
    .event-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #333;
    }
    .category-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 8px;
    }
    .category-Mass { background-color: #e8f5e9; color: #2e7d32; }
    .category-Confession { background-color: #fff3e0; color: #e65100; }
    .category-Adoration { background-color: #e3f2fd; color: #1565c0; }
    .category-Bible_Study { background-color: #f3e5f5; color: #6a1b9a; }
    .category-Youth { background-color: #fce4ec; color: #c2185b; }
    .category-Family { background-color: #e0f2f1; color: #00695c; }
    .category-Retreat { background-color: #e8eaf6; color: #283593; }
    .category-Service { background-color: #fbe9e7; color: #bf360c; }
    .category-Fundraiser { background-color: #fff8e1; color: #f57f17; }
    .category-Social { background-color: #f1f8e9; color: #33691e; }
    .category-Other { background-color: #eceff1; color: #455a64; }
    .stats-card {
        background: linear-gradient(135deg, #2B4F2B 0%, #1e3a1e 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .search-box {
        margin-bottom: 1rem;
    }
    .featured-section {
        background-color: #f0f4f0;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOAD EVENTS DATA
# ============================================
def load_events():
    """Load events from the JSON file or use fallback data"""
    if os.path.exists("events_data.json"):
        with open("events_data.json", "r") as f:
            return json.load(f)
    else:
        # Fallback sample data
        return {
            "Cathedral of St. Ignatius Loyola": {
                "events": [
                    {"event_name": "Sunday Mass", "date": "Sunday", "time": "8:00 AM, 10:00 AM, 12:00 PM", 
                     "category": "Mass", "description": "Weekly Sunday Eucharist"},
                    {"event_name": "Confession", "date": "Saturday", "time": "4:00 PM", 
                     "category": "Confession", "description": "Sacrament of Reconciliation"},
                ]
            }
        }

# ============================================
# HEADER
# ============================================
st.markdown('<p class="main-title">⛪ Communio</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Event Hub for the Diocese of Palm Beach</p>', unsafe_allow_html=True)

# ============================================
# STATS BAR (Top of page)
# ============================================
events_data = load_events()
total_parishes = len(events_data)
total_events = sum(len(data.get("events", [])) for data in events_data.values())

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stats-card"><h3>{total_parishes}</h3><p>Parishes</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stats-card"><h3>{total_events}</h3><p>Active Events</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stats-card"><h3>🤖</h3><p>AI-Powered</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stats-card"><h3>📅</h3><p>Weekly Updates</p></div>', unsafe_allow_html=True)

# ============================================
# SEARCH ENGINE (MAIN AI COMPONENT)
# ============================================
st.markdown("## 🔍 Search Events")
st.markdown("Ask AI to find events that match what you're looking for")

col_search1, col_search2 = st.columns([3, 1])
with col_search1:
    search_query = st.text_input("", placeholder="e.g., 'confession this weekend' or 'youth group near me'", key="search")
with col_search2:
    search_button = st.button("🔍 Search", type="primary")

# ============================================
# CATEGORY ADVERTISEMENT SECTION
# ============================================
st.markdown("## 📖 Browse by Category")

# Define categories with icons
categories = {
    "Mass": "🙏",
    "Confession": "🕊️",
    "Adoration": "✨",
    "Bible Study": "📖",
    "Youth": "🧑‍🎤",
    "Family": "👨‍👩‍👧‍👦",
    "Retreat": "🏔️",
    "Service": "🤝",
    "Fundraiser": "💰",
    "Social": "🎉"
}

# Create category buttons in rows
cat_cols = st.columns(5)
for i, (cat, icon) in enumerate(categories.items()):
    with cat_cols[i % 5]:
        if st.button(f"{icon} {cat}", key=f"cat_{cat}", use_container_width=True):
            search_query = cat
            search_button = True

# ============================================
# FEATURED EVENTS OF THE WEEK
# ============================================
st.markdown("## ⭐ Featured Events This Week")
st.markdown('<div class="featured-section">', unsafe_allow_html=True)

# Display 3 featured events (most recent or random)
featured_events = []
for parish_name, parish_data in events_data.items():
    for event in parish_data.get("events", [])[:1]:  # Take first event from each parish
        featured_events.append({"parish": parish_name, **event})

for event in featured_events[:3]:
    cat_class = f"category-{event.get('category', 'Other').replace(' ', '_')}"
    st.markdown(f"""
    <div class="event-card">
        <div class="parish-name">{event.get('parish', 'Unknown')}</div>
        <div class="event-name">📌 {event.get('event_name', 'Unknown')}</div>
        <div><span class="category-badge {cat_class}">{event.get('category', 'Other')}</span></div>
        <div>📅 {event.get('date', 'TBD')} at {event.get('time', 'TBD')}</div>
        <div>📝 {event.get('description', 'No description available')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ALL EVENTS WITH FILTERS
# ============================================
st.markdown("## 📋 All Events")

# Filter sidebar
with st.sidebar:
    st.markdown("### 🎯 Filter Events")
    
    # Parish filter
    parish_list = ["All Parishes"] + list(events_data.keys())
    selected_parish = st.selectbox("🏛️ Parish", parish_list)
    
    # Category filter
    cat_list = ["All Categories"] + list(categories.keys()) + ["Other"]
    selected_category = st.selectbox("📖 Category", cat_list)
    
    # Day filter
    days = ["Any Day", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_day = st.selectbox("📅 Day", days)
    
    st.markdown("---")
    st.markdown("### 🤖 About the AI")
    st.info("""
    This website uses AI to:
    - Extract events from parish bulletins
    - Categorize events automatically
    - Power the search engine
    
    Events are updated weekly.
    """)

# Search/filter logic
filtered_events = []
for parish_name, parish_data in events_data.items():
    if selected_parish != "All Parishes" and selected_parish != parish_name:
        continue
    
    for event in parish_data.get("events", []):
        # Category filter
        if selected_category != "All Categories" and event.get("category", "Other") != selected_category:
            continue
        
        # Day filter
        if selected_day != "Any Day" and selected_day.lower() not in event.get("date", "").lower():
            continue
        
        # Search query
        if search_query and search_button:
            search_lower = search_query.lower()
            event_text = f"{event.get('event_name', '')} {event.get('description', '')} {event.get('category', '')}"
            if search_lower not in event_text.lower():
                continue
        
        filtered_events.append({"parish": parish_name, **event})

# Display filtered events
if filtered_events:
    for event in filtered_events:
        cat_class = f"category-{event.get('category', 'Other').replace(' ', '_')}"
        st.markdown(f"""
        <div class="event-card">
            <div class="parish-name">{event.get('parish', 'Unknown')}</div>
            <div class="event-name">📌 {event.get('event_name', 'Unknown')}</div>
            <div><span class="category-badge {cat_class}">{event.get('category', 'Other')}</span></div>
            <div>📅 {event.get('date', 'TBD')} at {event.get('time', 'TBD')}</div>
            <div>📝 {event.get('description', 'No description available')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("🔍 No events match your filters. Try a different search or category!")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(f"""
*Communio • Diocese of Palm Beach • AI-Powered Event Hub • Last updated: {datetime.now().strftime('%Y-%m-%d')}*
""")
