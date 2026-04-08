{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
\
# Page setup\
st.set_page_config(page_title="Communio", page_icon="\uc0\u9962 ")\
st.title("Communio")\
st.subheader("Your Diocese Event Hub")\
\
# Simple events for testing\
events = [\
    \{"Parish": "St. Mary's", "Event": "Eucharistic Adoration", "Date": "Friday", "Time": "6:30 PM", "Location": "Main Church"\},\
    \{"Parish": "St. Joseph", "Event": "Bible Study", "Date": "Wednesday", "Time": "7:00 PM", "Location": "Parish Hall"\},\
    \{"Parish": "Sacred Heart", "Event": "Confession", "Date": "Saturday", "Time": "3:00-4:30 PM", "Location": "Church"\},\
]\
\
# Display as a nice table\
st.write("### Upcoming Events in the Diocese")\
st.table(events)\
\
# Simple filter box\
st.write("### Filter by Parish")\
parish_options = list(set([e["Parish"] for e in events]))\
selected_parish = st.selectbox("Choose a parish", ["All"] + parish_options)\
\
if selected_parish != "All":\
    filtered = [e for e in events if e["Parish"] == selected_parish]\
    st.table(filtered)}
