"""UAE Labour Law AI v2.3 — slim orchestrator. Modules: languages, ui, engine, chat, tools."""
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

import chat
import engine
import learn
import tools
import ui
from languages import LANGS, LANG_ORDER, detect_lang

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))

st.set_page_config(page_title="UAE Labour Law AI ⚖️", page_icon="⚖️", layout="wide")
ui.render()

with st.sidebar:
    st.markdown("### 🌐 Language / භාෂාව")
    mode = st.radio("Answer-language mode:", ["🤖 Auto-detect (recommended)", "🎯 Manual pick"], index=0)
    forced_lang = (st.selectbox("Language:", LANG_ORDER,
                                 format_func=lambda k: f"{LANGS[k]['flag']} {LANGS[k]['name']}")
                   if "Manual" in mode else None)
    st.markdown("---")
    stats = learn.feedback_stats()
    st.markdown("### 📊 Learning Stats")
    st.metric("👍 Verified answers", stats["up"])
    st.metric("👎 Rejected", stats["down"])
    st.markdown("---")
    st.caption("AI legal information, not legal advice • FD-L 33/2021 as amended")

if "messages" not in st.session_state:
    st.session_state.messages = []

db = engine.load_db("chroma_db")
verified_db = engine.load_db("chroma_verified")
if db is None:
    st.info("ℹ️ Knowledge base not built yet — answers use Gemini's general knowledge. "
            "Run `python scraper.py` → `python ingest.py` locally and upload chroma_db for grounded answers.")

try:
    from streamlit_mic_recorder import speech_to_text
    MIC_OK = True
except Exception:
    speech_to_text = None
    MIC_OK = False

tab_chat, tab_tools = st.tabs(["💬 Chat", "🧰 Tools"])
with tab_chat:
    chat.render(client, db, verified_db, learn, engine, LANGS, detect_lang, speech_to_text, MIC_OK, forced_lang)
with tab_tools:
    tools.render()

st.markdown("<p style='text-align:center;color:#9aa7ba;font-size:11px;margin-top:18px'>AI legal information, not legal advice • FD-L 33/2021 as amended (20/2023, 9/2024) • © 2026</p>", unsafe_allow_html=True)
