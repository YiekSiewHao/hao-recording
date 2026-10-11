
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="Hao Recording",
    page_icon="🎙️",
    layout="wide"
)

@st.cache_data(ttl=60, show_spinner=False)
def load_recordings():
    url = st.secrets["SUPABASE_URL"].rstrip("/")
    key = st.secrets["SUPABASE_KEY"]

    response = requests.get(
        f"{url}/rest/v1/recordings",
        headers={"apikey": key},
        params={
            "select": "id,title,recorded_at,category,summary,transcript,key_points,action_items,starred",
            "order": "created_at.desc"
        },
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def format_date(value):
    if not value:
        return "Undated"

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return "Undated"


def as_list(value):
    if isinstance(value, list):
        return value
    return []


st.title("🎙️ Hao Recording")
st.caption("Your personal AI-powered recording assistant")

try:
    recordings = load_recordings()
except Exception:
    st.error(
        "Unable to load recordings. Check your Streamlit "
        "Secrets and Supabase connection."
    )
    st.stop()

with st.sidebar:
    st.title("Hao Recording")
    search = st.text_input(
        "Search recordings",
        placeholder="Search titles..."
    )
    st.divider()
    st.caption("MY RECORDINGS")

    filtered = [
        r for r in recordings
        if search.lower() in (r.get("title") or "").lower()
    ]

    if not filtered:
        st.info("No recordings found.")
        st.stop()

    choices = list(range(len(filtered)))
    selected_index = st.radio(
        "Select a recording",
        choices,
        format_func=lambda i: (
            ("⭐ " if filtered[i].get("starred") else "")
            + (filtered[i].get("title") or "Untitled")
        ),
        label_visibility="collapsed"
    )

recording = filtered[selected_index]

st.header(recording.get("title") or "Untitled Recording")

st.caption(
    f"{format_date(recording.get('recorded_at'))}"
    f" · {recording.get('category') or 'Other'}"
)

st.divider()

st.subheader("✨ AI Summary")
st.markdown(
    recording.get("summary") or
    "_No summary available._"
)

st.subheader("💡 Key Points")
points = as_list(recording.get("key_points"))

if points:
    for point in points:
        st.markdown(f"- {point}")
else:
    st.caption("No key points available.")

st.subheader("✅ Action Items")
actions = as_list(recording.get("action_items"))

if actions:
    for i, action in enumerate(actions):
        st.checkbox(
            str(action),
            key=f"{recording['id']}_action_{i}"
        )
else:
    st.caption("No action items available.")

st.subheader("📝 Transcript")
st.text_area(
    "Full transcription",
    value=recording.get("transcript") or "",
    height=300,
    disabled=True,
    label_visibility="collapsed"
)

st.divider()
st.caption("Hao Recording · Private AI Recording Library")
