def render_event_card(row: pd.Series):
    title = str(row.get("title", "")).strip()
    date_label = str(row.get("date_label", "")).strip()
    time_text = str(row.get("time", "")).strip()
    category = str(row.get("category", "Other")).strip()
    parish = str(row.get("parish", "")).strip()
    source = str(row.get("source", "")).strip()
    location = str(row.get("location", "")).strip()
    description = str(row.get("description", "")).strip()

    with st.container(border=True):
        if date_label or time_text:
            st.caption(f"{date_label} · {time_text}")

        st.markdown(f"### {title}")

        if location:
            st.caption(f"📍 {location}")

        if description:
            st.write(description)

        badges = []

        if category:
            badges.append(f"**Category:** {category}")

        if parish:
            badges.append(f"**Parish:** {parish}")

        if source:
            badges.append(f"**Source:** {source}")

        st.caption("  |  ".join(badges))
