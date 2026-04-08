import streamlit as st

st.set_page_config(page_title="Communio", page_icon="⛪", layout="wide")

# Simple clean CSS
st.markdown("""
<style>
.big-title {
    text-align: center;
    font-size: 4rem;
    color: #d4a853;
    margin-bottom: 0;
}
.subtitle {
    text-align: center;
    font-size: 1.2rem;
    color: #aaa;
    margin-top: 0;
}
.event-card {
    background-color: #1e1e24;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #d4a853;
}
.parish-name {
    font-size: 1.2rem;
    font-weight: bold;
    color: #d4a853;
}
.stats {
    background-color: #d4a853;
    color: black;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="big-title">⛪ COMMUNIO</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Diocese of Palm Beach · Event Directory</p>', unsafe_allow_html=True)

# Sample data (real parishes)
parishes = {
    "Cathedral of St. Ignatius Loyola": {"city": "Palm Beach Gardens", "county": "Palm Beach"},
    "St. Ann Catholic Church": {"city": "West Palm Beach", "county": "Palm Beach"},
    "St. Patrick Catholic Church": {"city": "Delray Beach", "county": "Palm Beach"},
    "Blessed Trinity Parish": {"city": "Boca Raton", "county": "Palm Beach"},
}

# Stats row
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="stats"><h3>{len(parishes)}</h3><p>Parishes</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stats"><h3>🤖</h3><p>AI Powered</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stats"><h3>📅</h3><p>Weekly Updates</p></div>', unsafe_allow_html=True)

st.divider()

# Search and filters
st.subheader("🔍 Find Events")

col_search, col_cat = st.columns([3, 1])
with col_search:
    search = st.text_input("", placeholder="Search by event name, parish, or keyword...")
with col_cat:
    category = st.selectbox("Category", ["All", "Mass", "Confession", "Adoration", "Youth", "Retreat", "Social"])

# Display parishes
for parish_name, info in parishes.items():
    with st.expander(f"📌 {parish_name} — {info['city']}"):
        st.markdown(f"**📍 {info['city']} County**")
        st.markdown("No events yet. AI parser coming soon!")
        if st.button(f"View {parish_name} Events", key=parish_name):
            st.info("Event details will appear here once AI parsing is active.")

# Footer
st.divider()
st.markdown("<p style='text-align:center;color:#666;'>Communio · Diocese of Palm Beach · AI-Powered Event Hub</p>", unsafe_allow_html=True)
