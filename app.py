import streamlit as st

st.set_page_config(page_title="Communio", page_icon="⛪")
st.title("Communio")
st.subheader("Your Diocese Event Hub")

events = [
    {"Parish": "St. Mary's", "Event": "Adoration", "Date": "Friday", "Time": "6:30 PM"},
    {"Parish": "St. Joseph", "Event": "Bible Study", "Date": "Wednesday", "Time": "7:00 PM"},
]

st.table(events)
