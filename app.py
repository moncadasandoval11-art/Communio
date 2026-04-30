import streamlit as st
import pandas as pd
import time

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Communio",
    page_icon="⛪",
    layout="wide"
)

# ==========================================
# CUSTOM CSS (BEACHY PALM BEACH STYLE)
# ==========================================

st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #e6f2f8 0%, #ffffff 100%);
}

.title {
    font-size: 3rem;
    font-weight: 800;
    color: #0a3a5a;
}

.subtitle {
    color: #5c7d8a;
    margin-bottom: 20px;
}

.quick-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-top: 20px;
}

.quick-card {
    background: linear-gradient(135deg, #0a3a5a, #1b6b8f);
    padding: 18px;
    border-radius: 14px;
    color: white;
    transition: 0.3s;
}

.quick-card:hover {
    transform: translateY(-5px);
}

.quick-card a {
    color: white;
    font-weight: bold;
    text-decoration: none;
}

.bishop-card {
    display: flex;
    gap: 20px;
    margin-top: 30px;
    background: linear-gradient(135deg, #1b6b8f, #4bb6d6);
    padding: 20px;
    border-radius: 18px;
    color: white;
    align-items: center;
}

.bishop-card img {
    border-radius: 12px;
}

.bishop-kicker {
    font-weight: bold;
    font-size: 1.1rem;
    opacity: 0.9;
}

.bishop-quote {
    margin-top: 8px;
    font-size: 1rem;
}

.event-card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border-left: 5px solid #1b6b8f;
    margin-bottom: 10px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

.slide-box {
    background: linear-gradient(135deg, #0a3a5a, #1b6b8f);
    color: white;
    padding: 25px;
    border-radius: 16px;
    margin-top: 25px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================

st.markdown('<div class="title">COMMUNIO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A coastal Catholic guide to parish life across the Diocese of Palm Beach.</div>', unsafe_allow_html=True)

# ==========================================
# QUICK LINKS (FIXED RENDERING)
# ==========================================

st.markdown("""
<div class="quick-grid">

    <div class="quick-card">
        <a href="https://www.diocesepb.org/" target="_blank">Diocese Website</a>
        <p>Official diocesan homepage, ministries, and resources.</p>
    </div>

    <div class="quick-card">
        <a href="https://www.diocesepb.org/news/events.html" target="_blank">Diocesan Calendar</a>
        <p>Browse official diocesan events quickly.</p>
    </div>

    <div class="quick-card">
        <a href="https://www.diocesepb.org/about-us/office-of-the-bishop.html" target="_blank">Message from the Bishop</a>
        <p>Read updates from diocesan leadership.</p>
    </div>

</div>
""", unsafe_allow_html=True)

# ==========================================
# BISHOP SECTION
# ==========================================

st.markdown("""
<div class="bishop-card">
    <img src="Headshot2-Chosen-FrRodriguez.jpg.webp" width="140">
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

# ==========================================
# SAMPLE EVENTS (MANUAL - NO API NEEDED)
# ==========================================

events = pd.DataFrame([
    ["Final Guild Gathering & May Crowning", "May 6", "11:00 AM", "Adult Formation"],
    ["Extraordinary Ministers Workshop", "May 23", "9:00 AM", "Liturgy"],
    ["Unbound Revival Night", "May 24", "5:00 PM", "Prayer"],
    ["Bible Study Wednesday", "Weekly", "10:00 AM", "Adult Formation"],
])

events.columns = ["Title", "Date", "Time", "Category"]

# ==========================================
# EVENT FILTER
# ==========================================

st.subheader("Find an Event")

category = st.selectbox("Category", ["All"] + list(events["Category"].unique()))

if category != "All":
    filtered = events[events["Category"] == category]
else:
    filtered = events

for _, row in filtered.iterrows():
    st.markdown(f"""
    <div class="event-card">
        <b>{row['Title']}</b><br>
        {row['Date']} • {row['Time']}<br>
        <i>{row['Category']}</i>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# SLIDESHOW FEATURED EVENTS
# ==========================================

st.markdown("### Featured Events")

placeholder = st.empty()

featured = [
    "Final Guild Gathering & May Crowning",
    "Unbound Revival Night",
    "Eucharistic Ministers Workshop"
]

for i in range(3):
    with placeholder.container():
        st.markdown(f"""
        <div class="slide-box">
            <h2>{featured[i]}</h2>
            <p>Join your parish community in this upcoming event.</p>
        </div>
        """, unsafe_allow_html=True)
    time.sleep(2)
