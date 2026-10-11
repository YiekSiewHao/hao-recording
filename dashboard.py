import streamlit as st

st.set_page_config(
    page_title="Hao Recording",
    page_icon="🎙️",
    layout="wide"
)

with st.sidebar:
    st.title("🎙️ Hao Recording")
    st.caption("Private AI recording library")
    st.text_input("Search recordings", placeholder="Search notes...")
    st.divider()
    st.caption("MY RECORDINGS")
    st.info("Your synced recordings will appear here.")

st.title("Hao Recording")
st.caption("Your personal AI-powered recording assistant")

st.success("Your private website is ready for deployment!")

st.header("✨ AI Summary")
st.write("Select a recording to view its AI summary.")

st.header("💡 Key Points")
st.write("Important ideas from your recordings will appear here.")

st.header("✅ Action Items")
st.write("Tasks extracted from recordings will appear here.")

st.header("🎧 Audio & Transcription")
st.write("Audio playback and transcripts will appear here.")

st.divider()
st.caption("Hao Recording · Private Dashboard")
