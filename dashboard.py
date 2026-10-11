import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from html import escape

import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Hao Recording", page_icon="🎙️", layout="wide")

DISPLAY_TZ = ZoneInfo("America/New_York")  # User local time; change if you move time zones.

BASE_URL = st.secrets["SUPABASE_URL"].rstrip("/")
API_KEY = st.secrets["SUPABASE_KEY"]
API_ROOT = f"{BASE_URL}/rest/v1/recordings"
HEADERS = {"apikey": API_KEY}

st.markdown("""
<style>
/* Hao Recording — midnight-blue navigation with a calm reading surface */
.block-container {max-width: 1120px; padding-top: 2rem;}
[data-testid="stSidebar"] {
  background: linear-gradient(160deg, #15233b 0%, #101b2e 65%, #0b1424 100%) !important;
  border-right: 1px solid #253751;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {color: #e9effa;}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] [data-testid="stMetricValue"],
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {color: #e9effa !important;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
  color: #a9b9d1 !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] {
  background: #1b2d47; border: 1px solid #2c4362;
  border-radius: 12px; padding: 11px 12px;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
  font-size: 1.5rem;
}
[data-testid="stSidebar"] .stButton > button {
  color: #e9effa !important; background: #20334d !important;
  border: 1px solid #344b69 !important; border-radius: 9px;
  text-align: left; justify-content: flex-start;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #2b4565 !important; border-color: #7fa9db !important;
}
[data-testid="stSidebar"] .stTextInput input {
  color: #f4f7ff !important; background: #1b2d47 !important;
  border: 1px solid #354d6c !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder {color: #aebed5 !important;}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {color: #c6d3e6 !important;}
[data-testid="stSidebar"] hr {border-color: #34465d;}
.small-label {color: #8eb5ed; font-size: .74rem; font-weight: 700;
  letter-spacing: .1em; margin: 1rem 0 .25rem;}
.meta-line {color: #798292; font-size: .84rem; margin-top: -.5rem;}
.section-heading {font-size: 1rem; font-weight: 650; margin-top: 1.4rem;}
/* Transcript: crisp white text, even when the widget is read-only/disabled. */
[data-testid="stTextArea"] textarea,
[data-testid="stTextArea"] textarea:disabled {
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
  background-color: #162338 !important;
  opacity: 1 !important;
  border: 1px solid #425574 !important;
  font-weight: 450 !important;
  line-height: 1.7 !important;
}
[data-testid="stTextArea"] textarea:disabled::selection {
  background: #426b9c !important;
  color: #FFFFFF !important;
}
/* Sidebar recording cards: title on first row, time and actions on second. */
[data-testid="stSidebar"] [class*="st-key-record_row_"] {
  padding: .65rem .55rem .75rem !important;
  margin-bottom: .38rem !important;
  border: 1px solid #2b405d;
  background: rgba(255,255,255,.035);
  border-radius: 12px;
}
[data-testid="stSidebar"] [class*="st-key-record_row_"]:hover {
  background: rgba(255,255,255,.065);
}
[data-testid="stSidebar"] [class*="st-key-record_row_"] .stButton > button {
  min-width: 0 !important;
  box-sizing: border-box !important;
}
/* Main title separated from its controls so it cannot squeeze on phones. */
.st-key-selected_record_header h1 {
  font-size: clamp(1.35rem, 4vw, 2rem) !important;
  overflow-wrap: anywhere;
  line-height: 1.25;
  margin-bottom: .25rem;
}
/* Precise square action controls for the sidebar and the main page. */
[class*="st-key-record_row_"] [data-testid="stHorizontalBlock"],
.st-key-record_actions [data-testid="stHorizontalBlock"] {
  flex-wrap: nowrap !important;
  align-items: center !important;
  gap: .42rem !important;
}
[class*="st-key-record_row_"] [data-testid="stColumn"],
.st-key-record_actions [data-testid="stColumn"] {
  min-width: 0 !important;
}
[class*="st-key-record_row_"] [data-testid="stColumn"]:not(:first-child),
.st-key-record_actions [data-testid="stColumn"]:not(:first-child) {
  flex: 0 0 2.25rem !important;
  width: 2.25rem !important;
}
[class*="st-key-record_row_"] [data-testid="stColumn"]:not(:first-child) .stButton > button,
.st-key-record_actions [data-testid="stColumn"]:not(:first-child) .stButton > button {
  width: 2.25rem !important;
  min-width: 2.25rem !important;
  max-width: 2.25rem !important;
  height: 2.25rem !important;
  min-height: 2.25rem !important;
  max-height: 2.25rem !important;
  padding: 0 !important;
  display: inline-flex !important;
  justify-content: center !important;
  align-items: center !important;
  line-height: 1 !important;
  font-size: 1.15rem !important;
}
[class*="st-key-record_row_"] [data-testid="stColumn"]:not(:first-child) .stButton > button p,
.st-key-record_actions [data-testid="stColumn"]:not(:first-child) .stButton > button p {
  margin: 0 !important;
  white-space: nowrap !important;
  line-height: 1 !important;
}
[class*="st-key-record_row_"] .stButton > button[kind="secondary"] {
  border-color: #344b69;
}
[class*="st-key-record_row_"] [data-testid="stColumn"]:first-child .stButton > button {
  width: 100% !important;
  padding: .3rem .35rem !important;
  background: transparent !important;
  border-color: transparent !important;
  justify-content: flex-start !important;
  text-align: left !important;
  height: auto !important;
  min-height: 2rem !important;
  font-size: .95rem !important;
  font-weight: 600;
}
[class*="st-key-record_row_"] [data-testid="stColumn"]:first-child .stButton > button p {
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  display: block !important;
}
.sidebar-record-time {
  display: flex; align-items: center;
  min-height: 2.25rem;
  font-size: .75rem; color: #a9b9d1;
  white-space: nowrap;
}
@media (max-width: 640px) {
  /* Space for the fixed Streamlit menu / Deploy / Share toolbar. */
  .block-container {
    padding-top: 4.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
  }
  [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-left: .75rem !important;
    padding-right: .75rem !important;
    padding-top: 2.4rem !important;
  }
  .st-key-selected_record_header h1 {font-size: 1.55rem !important;}
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30, show_spinner=False)
def fetch_recordings():
    response = requests.get(
        API_ROOT,
        headers=HEADERS,
        params={
            "select": "id,title,category,recorded_at,created_at,summary,transcript,key_points,action_items,starred",
            "order": "created_at.desc",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def update_recording(recording_id, changes):
    # ID is supplied as a query parameter rather than interpolated into the URL.
    response = requests.patch(
        API_ROOT,
        headers={**HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
        params={"id": f"eq.{recording_id}"},
        json=changes,
        timeout=20,
    )
    response.raise_for_status()
    fetch_recordings.clear()


def parse_datetime(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        # Supabase timestamps include offsets. Treat legacy naive timestamps as UTC.
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(DISPLAY_TZ)
    except (ValueError, TypeError):
        return None


def timestamp_for(record):
    # Never claim that cloud upload time is the true recording time.
    return record.get("recorded_at") or record.get("created_at")


def timestamp_label(record):
    return "Recorded" if record.get("recorded_at") else "Uploaded"


def display_clock(value):
    dt = parse_datetime(value)
    return dt.strftime("%-I:%M %p") if dt else "Time unavailable"


def date_group(value):
    dt = parse_datetime(value)
    if not dt:
        return "Undated"
    today = datetime.now(DISPLAY_TZ).date()
    if dt.date() == today:
        return "Today"
    if dt.date() == today - timedelta(days=1):
        return "Yesterday"
    return dt.strftime("%A, %b %-d, %Y")


def sort_timestamp(record):
    dt = parse_datetime(timestamp_for(record))
    return dt.timestamp() if dt else 0

def sections_from_markdown(md):
    """Split Markdown summary on #/##/### or standalone bold headings."""
    sections = defaultdict(list)
    current = "Executive Summary"
    canonical = {
        "recording type": "Recording Type",
        "type": "Recording Type",
        "executive summary": "Executive Summary",
        "summary": "Executive Summary",
        "key takeaways": "Key Takeaways",
        "takeaways": "Key Takeaways",
        "decisions": "Decisions",
        "decisions made": "Decisions",
        "action items": "Action Items",
        "actions": "Action Items",
        "problems and solutions": "Problems and Solutions",
        "problems & solutions": "Problems and Solutions",
        "important questions": "Important Questions",
        "questions": "Important Questions",
        "tags": "Tags",
        "key points": "Key Points",
        "title": "Title",
    }
    for line in (md or "").splitlines():
        match = re.match(r"^\s{0,3}#{1,4}\s+(.+?)\s*$", line)
        bold = re.match(r"^\s*\*\*(.+?)\*\*\s*:?[ \t]*(.*?)\s*$", line)
        heading = match.group(1) if match else (bold.group(1) if bold else None)
        inline_value = bold.group(2) if bold else ""
        if heading:
            normalized = re.sub(r"[*_:#]+", "", heading).strip().lower()
            if normalized in canonical:
                current = canonical[normalized]
                if inline_value:
                    sections[current].append(inline_value)
                continue
        sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def suggested_title(record):
    # A manually renamed title in the database always takes priority.
    title = (record.get("title") or "").strip()
    if title and title != record["id"] and title != "Untitled Recording":
        return title
    section = sections_from_markdown(record.get("summary") or "").get("Title", "")
    return section.splitlines()[0].strip(" *_#:-") if section.strip() else (title or record["id"])


def as_items(value):
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            out.append(str(item.get("text") or item.get("task") or item))
    return out


# Poll for new recordings every 30 seconds without a manual browser refresh.
# Pause while the rename form is open to avoid interrupting user input.
if not st.session_state.get("renaming", False):
    st_autorefresh(interval=30_000, limit=None, key="hao_recordings_auto_refresh")

try:
    recordings = fetch_recordings()
except Exception:
    st.error("Could not load recordings. Check Streamlit Secrets and Supabase access.")
    st.stop()

if "selected_id" not in st.session_state and recordings:
    st.session_state.selected_id = recordings[0]["id"]

with st.sidebar:
    st.title("🎙️ Hao Recording")
    st.caption("Your private recording library")
    today = datetime.now(DISPLAY_TZ).date()
    uploaded_today = sum(
        parse_datetime(r.get("created_at")) is not None
        and parse_datetime(r.get("created_at")).date() == today
        for r in recordings
    )
    c1, c2 = st.columns(2)
    c1.metric("Recordings", len(recordings))
    c2.metric("Uploaded today", uploaded_today)
    st.caption(f"★ {sum(bool(r.get('starred')) for r in recordings)} starred · {today.strftime('%b %-d, %Y')} (New York time)")
    search = st.text_input("Search", placeholder="Search titles and notes…")
    show_starred = st.toggle("Starred only", value=False)
    st.divider()

    visible = []
    for r in recordings:
        if show_starred and not r.get("starred"):
            continue
        if search.lower() not in (suggested_title(r) + " " + (r.get("summary") or "")).lower():
            continue
        visible.append(r)

    grouped = defaultdict(list)
    for r in sorted(visible, key=sort_timestamp, reverse=True):
        grouped[date_group(timestamp_for(r))].append(r)

    for group_name, items in grouped.items():
        st.markdown(f'<div class="small-label">{group_name.upper()}</div>', unsafe_allow_html=True)
        for r in items:
            title = suggested_title(r)
            # A keyed container enables phone-specific no-wrap CSS.
            with st.container(key="record_row_" + re.sub(r"[^A-Za-z0-9_]", "_", str(r["id"]))):
                # First row: recording name, with comfortable tap target.
                if st.button(title, key="select_" + r["id"], use_container_width=True):
                    st.session_state.selected_id = r["id"]
                    st.session_state["renaming"] = False
                    st.rerun()
                # Second row: time left, square favorite/rename buttons right.
                time_col, fav_col, rename_col = st.columns(
                    [0.70, 0.15, 0.15], gap="small", vertical_alignment="center"
                )
                with time_col:
                    st.markdown(
                        '<div class="sidebar-record-time">'
                        + escape(timestamp_label(r)) + ' · '
                        + escape(display_clock(timestamp_for(r)))
                        + '</div>', unsafe_allow_html=True
                    )
                with fav_col:
                    if st.button("★" if r.get("starred") else "☆", key="fav_" + r["id"], help="Toggle favorite", use_container_width=True):
                        try:
                            update_recording(r["id"], {"starred": not bool(r.get("starred"))})
                            st.rerun()
                        except Exception:
                            st.error("Could not update favorite.")
                with rename_col:
                    if st.button("✎", key="rename_" + r["id"], help="Rename", use_container_width=True):
                        st.session_state.selected_id = r["id"]
                        st.session_state["renaming"] = True
                        st.rerun()

    if not visible:
        st.info("No recordings match your search.")

chosen = next((r for r in recordings if r["id"] == st.session_state.get("selected_id")), None)
if chosen is None:
    st.info("Select a recording from the sidebar.")
    st.stop()

name = suggested_title(chosen)
with st.container(key="selected_record_header"):
    st.title(name)

# Keep actions in their own row, so the title never overlaps or wraps around icons.
with st.container(key="record_actions"):
    spacer_col, star_col, edit_col = st.columns(
        [0.70, 0.15, 0.15], gap="small", vertical_alignment="center"
    )
    with star_col:
        if st.button("★" if chosen.get("starred") else "☆", help="Toggle favorite", key="star_selected", use_container_width=True):
            try:
                update_recording(chosen["id"], {"starred": not bool(chosen.get("starred"))})
                st.rerun()
            except Exception:
                st.error("Could not update favorite.")
    with edit_col:
        if st.button("✎", help="Rename recording", key="edit_selected", use_container_width=True):
            st.session_state["renaming"] = not st.session_state.get("renaming", False)

if st.session_state.get("renaming"):
    with st.form("rename_form"):
        new_name = st.text_input("Recording name", value=name)
        if st.form_submit_button("Save name"):
            if new_name.strip():
                try:
                    update_recording(chosen["id"], {"title": new_name.strip()})
                    st.session_state["renaming"] = False
                    st.rerun()
                except Exception:
                    st.error("Could not save name.")
            else:
                st.warning("Enter a recording name.")

st.markdown(
    '<div class="meta-line">'
    + escape(timestamp_label(chosen)) + ' · '
    + escape(date_group(timestamp_for(chosen))) + ' · '
    + escape(display_clock(timestamp_for(chosen))) + ' · '
    + escape(chosen.get("category") or "Other") + '</div>',
    unsafe_allow_html=True,
)

st.divider()

parsed = sections_from_markdown(chosen.get("summary") or "")
preferred = [
    "Recording Type", "Executive Summary", "Key Takeaways", "Decisions",
    "Action Items", "Problems and Solutions", "Important Questions", "Tags", "Key Points"
]

for section in preferred:
    content = parsed.get(section, "").strip()
    if section == "Key Points" and not content:
        pts = as_items(chosen.get("key_points"))
        if pts:
            content = "\n".join("- " + p for p in pts)
    if section == "Action Items" and not content:
        tasks = as_items(chosen.get("action_items"))
        if tasks:
            content = "\n".join("- " + p for p in tasks)
    if not content:
        continue
    st.subheader(section)
    st.markdown(content)

other = [k for k in parsed if k not in preferred and k != "Title"]
for section in other:
    if parsed[section].strip():
        st.subheader(section)
        st.markdown(parsed[section])

st.divider()
st.subheader("🎧 Audio & timestamped transcript")
st.info("Audio replay and click-to-jump timestamps need audio storage plus timestamped transcription. Your current cloud records only include plain text, so no timeline is available yet.")
st.subheader("📝 Full Transcript")
st.text_area("Transcript", chosen.get("transcript") or "", height=300, disabled=True, label_visibility="collapsed")
st.download_button("Download transcript", data=chosen.get("transcript") or "", file_name="transcript.txt", mime="text/plain")
st.download_button("Download summary", data=chosen.get("summary") or "", file_name="summary.md", mime="text/markdown")
st.caption("Hao Recording · Private library")
