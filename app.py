import streamlit as st

# PAGE CONFIGURATION - MUST BE FIRST COMMAND
st.set_page_config(
    page_title="Communio - Diocese of Palm Beach",
    page_icon="⛪",
    layout="wide"
)

# CUSTOM CSS FOR BETTER LOOKING
st.markdown("""
<style>
    /* Main title styling */
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
    /* Event card styling */
    .event-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2B4F2B;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .parish-name {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2B4F2B;
        margin-bottom: 0.5rem;
    }
    .event-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #333;
    }
    /* Sidebar styling */
    .sidebar-section {
        background-color: #f0f4f0;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    /* Button styling */
    .stButton > button {
        background-color: #2B4F2B;
        color: white;
        border-radius: 20px;
    }
    .stButton > button:hover {
        background-color: #1e3a1e;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<p class="main-title">⛪ Communio</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your Event Hub for the Diocese of Palm Beach</p>', unsafe_allow_html=True)

# SIDEBAR - Diocese Info
with st.sidebar:
    st.image("https://www.diocesepb.org/images/logo.png", use_container_width=True)
    st.markdown("### 📌 Diocese of Palm Beach")
    st.markdown("**Bishop:** Gerald Barbarito")
    st.markdown("**Cathedral:** St. Ignatius Loyola")
    st.markdown("**Parishes:** 53 across 5 counties")
    st.markdown("---")
    st.markdown("### 🗺️ Counties Served")
    st.markdown("- Palm Beach")
    st.markdown("- Martin")
    st.markdown("- St. Lucie")
    st.markdown("- Indian River")
    st.markdown("- Okeechobee")

# REAL PARISHES DATA (Based on actual Diocese of Palm Beach)
# In a real implementation, you'd have ALL 53 parishes. Here are sample real ones:

parishes_data = {
    "Cathedral of St. Ignatius Loyola": {
        "city": "Palm Beach",
        "county": "Palm Beach",
        "events": [
            {"name": "Sunday Mass", "day": "Sunday", "time": "8:00 AM, 10:00 AM, 12:00 PM"},
            {"name": "Daily Mass", "day": "Monday-Friday", "time": "7:30 AM"},
            {"name": "Confession", "day": "Saturday", "time": "4:00-5:00 PM"}
        ]
    },
    "St. Ann Parish": {
        "city": "West Palm Beach",
        "county": "Palm Beach",
        "events": [
            {"name": "Sunday Mass", "day": "Sunday", "time": "7:30 AM, 9:00 AM, 11:00 AM"},
            {"name": "Eucharistic Adoration", "day": "Thursday", "time": "9:00 AM - 7:00 PM"}
        ]
    },
    "Holy Name of Jesus": {
        "city": "West Palm Beach",
        "county": "Palm Beach",
        "events": [
            {"name": "Sunday Mass", "day": "Sunday", "time": "8:00 AM, 10:00 AM, 12:00 PM"},
            {"name": "Bible Study", "day": "Wednesday", "time": "7:00 PM"}
        ]
    },
    "St. Joseph Parish": {
        "city": "Stuart",
        "county": "Martin",
        "events": [
            {"name": "Sunday Mass", "day": "Sunday", "time": "8:00 AM, 10:00 AM"},
            {"name": "Youth Group", "day": "Friday", "time": "6:30 PM"}
        ]
    },
    "St. Lucie Parish": {
        "city": "Port St. Lucie",
        "county": "St. Lucie",
        "events": [
            {"name": "Sunday Mass", "day": "Sunday", "time": "9:00 AM, 11:00 AM"},
            {"name": "Confession", "day": "Saturday", "time": "3:30-4:30 PM"}
        ]
    },
    "St. Anastasia": {
        "city": "Fort Pierce",
        "county": "St. Lucie",
        "events": [
            {"name": "Sunday Mass", "day": "Sunday", "time": "8:30 AM, 10:30 AM"},
            {"name": "Adoration", "day": "Friday", "time": "9:00 AM - 6:00 PM"}
        ]
    },
    "Holy Cross": {
        "city": "Indiantown",
        "county": "Martin",
        "events": [
            {"name": "Sunday Mass (Spanish)", "day": "Sunday", "time": "9:00 AM"},
            {"name": "Sunday Mass (English)", "day": "Sunday", "time": "11:00 AM"}
        ]
    }
}

# MAIN CONTENT - Filters
st.markdown("## 📅 Upcoming Events")

col1, col2, col3 = st.columns(3)

with col1:
    # Get unique parishes for filter
    parish_list = ["All Parishes"] + list(parishes_data.keys())
    selected_parish = st.selectbox("🏛️ Filter by Parish", parish_list)

with col2:
    # County filter
    counties = ["All Counties", "Palm Beach", "Martin", "St. Lucie", "Indian River", "Okeechobee"]
    selected_county = st.selectbox("📍 Filter by County", counties)

with col3:
    # Event type filter
    event_types = ["All Events", "Mass", "Confession", "Adoration", "Bible Study", "Youth Group"]
    selected_type = st.selectbox("📖 Filter by Event Type", event_types)

# DISPLAY EVENTS
st.markdown("---")

# Filter logic
displayed_count = 0
for parish_name, parish_info in parishes_data.items():
    # Apply parish filter
    if selected_parish != "All Parishes" and selected_parish != parish_name:
        continue
    
    # Apply county filter
    if selected_county != "All Counties" and parish_info["county"] != selected_county:
        continue
    
    for event in parish_info["events"]:
        # Apply event type filter
        if selected_type != "All Events" and selected_type not in event["name"]:
            continue
        
        # Display event card
        st.markdown(f"""
        <div class="event-card">
            <div class="parish-name">{parish_name}</div>
            <div class="event-name">📌 {event["name"]}</div>
            <div>📅 {event["day"]} at {event["time"]}</div>
            <div>📍 {parish_info["city"]}, {parish_info["county"]} County</div>
        </div>
        """, unsafe_allow_html=True)
        displayed_count += 1

if displayed_count == 0:
    st.info("No events found. Try changing your filters!")

# FOOTER
st.markdown("---")
st.markdown(f"*Communio • Diocese of Palm Beach • {len(parishes_data)} parishes shown*")
