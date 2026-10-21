"""UAE Labour Law AI v2.2 — GUI • auto language detection • live voice chat.

Fixes in v2.2:
  - Gemini model fallback chain (flash-latest -> 2.0-flash -> 1.5-flash).
  - Forced dark theme (see .streamlit/config.toml) + explicit widget text colors
    so typed text and the language selector are visible everywhere.
  - Clearer API error messages (key missing / invalid / quota).
"""
import base64
import os
import pathlib
import re
import tempfile
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai

import learn

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))

# ---------------- Languages ----------------
LANGS = {
    "si": {"name": "Sinhala / සිංහල", "stt": "si-LK", "tts": "si",
           "out": "Sinhala (සිංහල script). If the user writes Singlish (romanized Sinhala), still reply in proper Sinhala script", "flag": "🇱🇰"},
    "ta": {"name": "Tamil / தமிழ்", "stt": "ta-IN", "tts": "ta", "out": "Tamil (தமிழ் script)", "flag": "🇱🇰"},
    "hi": {"name": "Hindi / हिन्दी", "stt": "hi-IN", "tts": "hi", "out": "Hindi (हिन्दी script)", "flag": "🇮🇳"},
    "kn": {"name": "Kannada / ಕನ್ನಡ", "stt": "kn-IN", "tts": "kn", "out": "Kannada (ಕನ್ನಡ script)", "flag": "🇮🇳"},
    "ml": {"name": "Malayalam / മലയാളം", "stt": "ml-IN", "tts": "ml", "out": "Malayalam (മലയാളം script)", "flag": "🇮🇳"},
    "ur": {"name": "Urdu / اردو", "stt": "ur-PK", "tts": "ur", "out": "Urdu (اردو script, RTL)", "flag": "🇵🇰"},
    "ar": {"name": "Arabic / العربية", "stt": "ar-AE", "tts": "ar", "out": "Arabic (العربية script, RTL)", "flag": "🇦🇪"},
    "bn": {"name": "Bengali / বাংলা", "stt": "bn-IN", "tts": "bn", "out": "Bengali (বাংলা script)", "flag": "🇧🇩"},
    "ne": {"name": "Nepali / नेपाली", "stt": "ne-NP", "tts": "ne", "out": "Nepali (नेपाली script)", "flag": "🇳🇵"},
    "tl": {"name": "Tagalog / Filipino", "stt": "fil-PH", "tts": "tl", "out": "Tagalog", "flag": "🇵🇭"},
    "en": {"name": "English", "stt": "en-AU", "tts": "en", "out": "English", "flag": "🇬🇧"},
}
LANG_ORDER = ["si", "ta", "hi", "kn", "ml", "ur", "ar", "bn", "ne", "tl", "en"]

SINGLISH_WORDS = (
    "mama", "oyaa", "oyage", "mata", "machan", "mchan", "kawda", "kawada", "karan",
    "kala", "one", "epa", "puluvan", "puluvanne", "denna", "kiyanna", "thama",
    "thamai", "nathi", "nisa", "witharai", "hari", "honda", "numba", "api", "eheme",
    "meke", "meeka", "eka", "deka", "wenna", "wenawa", "tiyenna", "anna",
    "kohomada", "koheda", "mokakda", "meka", "eyaa", "eyage", "apa", "salara",
)


def detect_lang(text: str, fallback: str = "en") -> str:
    """Detect the question's language. Singlish -> Sinhala."""
    t = re.sub(r"[^\w\s]", " ", text.lower())
    words = set(t.split())
    if len(words & set(SINGLISH_WORDS)) >= 2:
        return "si"
    try:
        from langdetect import detect, DetectorFactory
        DetectorFactory.seed = 0
        code = detect(text)
        return code if code in LANGS else fallback
    except Exception:
        return fallback


# ---------------- UI ----------------
st.set_page_config(page_title="UAE Labour Law AI ⚖️", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+Sinhala:wght@400;700&family=Noto+Sans+Arabic:wght@400;700&family=Noto+Sans+Tamil:wght@400;700&display=swap');
@keyframes aurora{0%{transform:translate(-8%,-4%) rotate(0)}50%{transform:translate(10%,6%) rotate(180deg)}100%{transform:translate(-8%,-4%) rotate(360deg)}}
@keyframes aurora2{0%{transform:translate(10%,4%) rotate(0)}50%{transform:translate(-6%,-8%) rotate(180deg)}100%{transform:translate(10%,4%) rotate(360deg)}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 20px rgba(16,163,127,.35)}50%{box-shadow:0 0 45px rgba(16,163,127,.75)}}
@keyframes shimmer{0%{left:-500px}100%{left:120%}}
.stApp{background:#070b12; color:#e7ecf3 !important; font-family:'Inter','Noto Sans Sinhala','Noto Sans Arabic','Noto Sans Tamil',sans-serif; overflow-x:hidden;}
.stApp::before{content:''; position:fixed; inset:-20%; z-index:-1;
  background:radial-gradient(45% 45% at 30% 30%, rgba(16,163,127,.22) 0%, transparent 60%),
             radial-gradient(40% 40% at 75% 25%, rgba(212,175,55,.16) 0%, transparent 60%),
             radial-gradient(50% 50% at 50% 80%, rgba(29,111,209,.18) 0%, transparent 65%);
  animation:aurora 26s linear infinite;}
.stApp::after{content:''; position:fixed; inset:-20%; z-index:-1;
  background:radial-gradient(35% 35% at 80% 70%, rgba(122,92,255,.14) 0%, transparent 60%),
             radial-gradient(30% 30% at 20% 85%, rgba(16,163,127,.12) 0%, transparent 60%);
  animation:aurora2 34s linear infinite;}
#MainMenu,footer{visibility:hidden}
header{background:transparent}
.hero{background:linear-gradient(145deg, rgba(255,255,255,.10), rgba(255,255,255,.03));
  backdrop-filter:blur(16px); border:1px solid rgba(255,255,255,.15); border-radius:26px;
  padding:30px 28px; box-shadow:0 20px 50px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.2);
  transform:perspective(1100px) rotateX(2deg); margin-bottom:18px; position:relative; overflow:hidden;}
.hero::after{content:''; position:absolute; top:0; left:-500px; width:60%; height:100%;
  background:linear-gradient(120deg, transparent, rgba(255,255,255,.08), transparent);
  animation:shimmer 5s infinite;}
.big-title{display:flex; align-items:center; justify-content:center; gap:14px; font-weight:800; font-size:44px;
  background:linear-gradient(135deg,#10a37f 0%,#7ef0c5 40%,#d4af37 100%); -webkit-background-clip:text; background-clip:text; color:transparent;}
.big-title .scales{font-size:52px; animation:floaty 4s ease-in-out infinite;}
.subtitle{text-align:center;color:#9aa7ba;margin-top:2px;font-size:15px;}
.lang-strip{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:16px;}
.lang-pill{background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.14); padding:6px 13px;
  border-radius:999px; font-size:12px; color:#cdd6e3; animation:floaty 6s ease-in-out infinite;}
.lang-pill:nth-child(odd){animation-delay:.8s}
.lang-pill:nth-child(3n){animation-delay:1.6s}
.feature-row{display:flex;justify-content:center;gap:10px;margin-top:14px;flex-wrap:wrap;}
.feature-chip{background:rgba(16,163,127,.15); border:1px solid rgba(16,163,127,.5); color:#7ef0c5;
  padding:5px 14px; border-radius:999px; font-size:12px;}
.voice-panel{background:linear-gradient(145deg, rgba(209,52,56,.16), rgba(255,255,255,.03));
  border:1px solid rgba(209,52,56,.5); border-radius:22px; padding:18px 20px; margin:14px 0;
  box-shadow:0 12px 30px rgba(0,0,0,.4);}
.mic-big{width:86px; height:86px; border-radius:50%; margin:0 auto 10px; display:grid; place-items:center;
  font-size:36px; background:linear-gradient(135deg,#d13438,#a4262c); cursor:pointer;
  animation:pulseGlow 1.6s ease-in-out infinite; border:3px solid rgba(255,255,255,.25);}
div[data-testid="stChatMessage"]{background:linear-gradient(145deg, rgba(255,255,255,.075), rgba(255,255,255,.02));
  border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:14px 18px;
  box-shadow:0 10px 26px rgba(0,0,0,.35); animation:rise .35s ease;}
@keyframes rise{from{opacity:0; transform:translateY(10px)} to{opacity:1}}
div[data-testid="stChatMessage"] p{color:#e7ecf3 !important;}
.stButton>button{background:linear-gradient(135deg,#10a37f,#0d8a6d); color:#fff !important; border:none; border-radius:14px;
  font-weight:700; box-shadow:0 6px 18px rgba(16,163,127,.45); transition:all .25s;}
.stButton>button:hover{transform:translateY(-2px) scale(1.02); color:#fff !important;}
.stChatInput{border-radius:16px !important; border:1px solid rgba(255,255,255,.2) !important;}
/* ---- v2.2 FIX: make all typed text + widget text clearly visible on dark UI ---- */
.stChatInput textarea, div[data-testid="stChatInput"] textarea{color:#ffffff !important; background-color:#101726 !important;}
.stTextInput input, .stTextArea textarea{color:#ffffff !important; background-color:#101726 !important;}
.stNumberInput input{color:#ffffff !important; background-color:#101726 !important;}
.stSelectbox>div>div{background:#101726 !important; border:1px solid rgba(255,255,255,.25) !important; border-radius:12px !important;}
.stSelectbox span, .stRadio label, .stRadio label p{color:#e7ecf3 !important;}
.stRadio div[role="radiogroup"] label{color:#e7ecf3 !important;}
.stRadio label:hover{color:#7ef0c5 !important;}
.stMetric{background:rgba(255,255,255,.05); border-radius:14px; padding:8px 12px;}
.stExpander{background:rgba(255,255,255,.04); border-radius:16px;}
.src-note{color:#9aa7ba; font-size:12px; border-inline-start:3px solid #d4af37; padding-inline-start:10px; margin-top:6px;}
.detected-pill{background:rgba(16,163,127,.15); border:1px solid rgba(16,163,127,.5); color:#7ef0c5;
  padding:3px 12px; border-radius:999px; font-size:11px; display:inline-block; margin-bottom:8px;}
.stDownloadButton>button{color:#ffffff !important;}
h1, h2, h3, h4, h5, h6, p, span, label, li{color:#e7ecf3;}
.stAlert, .stWarning, .stError, .stSuccess, .stInfo{color:#0b0f17;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="big-title"><span class="scales">⚖️</span> UAE Labour Law AI <span class="scales" style="animation-delay:2s">🏛️</span></div>
  <p class="subtitle">Your smart legal advisor — ask in <b>any language</b>, get the answer <b>in your language</b> 🗣️</p>
  <div class="feature-row">
    <span class="feature-chip">🌍 Auto Language Detect</span>
    <span class="feature-chip">🎙️ Voice Typing</span>
    <span class="feature-chip">🔴 Live Voice Chat</span>
    <span class="feature-chip">🧠 Self-Learning</span>
    <span class="feature-chip">📚 FD-L 33/2021</span>
  </div>
  <div class="lang-strip">
    <span class="lang-pill">සිංහල</span><span class="lang-pill">தமிழ்</span><span class="lang-pill">हिन्दी</span><span class="lang-pill">ಕನ್ನಡ</span><span class="lang-pill">മലയാളം</span><span class="lang-pill">اردو</span><span class="lang-pill">العربية</span><span class="lang-pill">বাংলা</span><span class="lang-pill">नेपाली</span><span class="lang-pill">Tagalog</span><span class="lang-pill">English</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
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

# ---------------- DB ----------------
@st.cache_resource
def load_db(path):
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    if not pathlib.Path(path).exists():
        return None
    emb = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    return Chroma(persist_directory=path, embedding_function=emb)


db = load_db("chroma_db")
verified_db = load_db("chroma_verified")
if db is None:
    st.info("ℹ️ Knowledge base not built yet — answers use Gemini's general knowledge. Run `python scraper.py` → `python ingest.py` locally and upload chroma_db for 100% grounded answers.")

# ---------------- Voice helpers ----------------
try:
    from streamlit_mic_recorder import speech_to_text
    MIC_OK = True
except Exception:
    MIC_OK = False

EDGE_VOICES = {
    "si": "si-LK-ThiliniNeural", "ta": "ta-IN-PallaviNeural", "hi": "hi-IN-MadhurNeural",
    "kn": "kn-IN-SapnaNeural", "ml": "ml-IN-SomapookNeural", "ur": "ur-PK-UzmaNeural",
    "ar": "ar-AE-FatimaNeural", "bn": "bn-IN-TanishaaNeural", "ne": "ne-NP-HemkalaNeural",
    "tl": "fil-PH-AngeloNeural", "en": "en-AE-FatimaNeural",
}


def tts_audio(text, lang):
    try:
        import asyncio
        import edge_tts
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            asyncio.run(edge_tts.Communicate(text, EDGE_VOICES.get(lang, "en-AE-FatimaNeural")).save(f.name))
            return pathlib.Path(f.name).read_bytes()
    except Exception:
        try:
            from gtts import gTTS
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                gTTS(text=text, lang=lang).save(f.name)
                return pathlib.Path(f.name).read_bytes()
        except Exception:
            return None


def play_audio(b):
    if b:
        b64 = base64.b64encode(b).decode()
        st.markdown(f"<audio controls autoplay src='data:audio/mp3;base64,{b64}' type='audio/mpeg' style='width:100%;margin-top:8px;'></audio>", unsafe_allow_html=True)


# ---------------- RAG engine ----------------
GENAI_MODELS = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-1.5-flash"]


def gemini_generate(prompt: str) -> str:
    """Try each model alias until one works — fixes 'model not found' errors."""
    last_err = None
    for model in GENAI_MODELS:
        try:
            return client.models.generate_content(model=model, contents=prompt).text
        except Exception as e:
            last_err = e
    raise last_err


def ask(query: str, lang_key: str):
    """RAG: verified memory + law DB -> Gemini -> (answer, context)."""
    L = LANGS[lang_key]
    parts = []
    if verified_db is not None:
        try:
            for d in verified_db.similarity_search(query, k=2):
                parts.append(f"[VERIFIED MEMORY — user-approved]\n{d.page_content}")
        except Exception:
            pass
    if db is not None:
        try:
            for d in db.similarity_search(query, k=4):
                parts.append(f"[OFFICIAL LAW — {d.metadata.get('title', 'source')}]\n{d.page_content}")
        except Exception:
            pass
    for r in (learn.best_verified(query) or []):
        parts.append(f"[VERIFIED MEMORY]\nQ: {r['question']}\nA: {r['answer']}")
    context = "\n\n---\n\n".join(parts)
    grounded = bool(parts)

    if grounded:
        context_rule = ('Answer ONLY using the context below. If the answer is not in the context, '
                        'say "I am sorry, I cannot provide an answer based on the official laws." '
                        'Do not hallucinate. Do not invent article numbers.')
    else:
        context_rule = ('Answer from your general knowledge of UAE Federal Decree-Law No. 33/2021 '
                        'as amended. If unsure, say so. Never invent article numbers.')

    prompt = f"""You are an expert UAE Labour Lawyer. {context_rule}
CRITICAL LANGUAGE RULE: Reply fully in: {L['out']}. Even if the question is in Singlish or another language, the final answer must be in the user's language's natural script.
Keep it concise (under 180 words). Cite articles inside the answer when available.
{('CONTEXT:\n' + context) if grounded else ''}
QUESTION: {query}"""

    try:
        answer = gemini_generate(prompt)
    except Exception as e:
        msg = str(e)
        if "API key" in msg or "401" in msg or "permission" in msg.lower():
            st.error("🔑 Gemini API key problem: the key is missing, revoked, or invalid. "
                     "Check the app's Secrets (GEMINI_API_KEY) in Streamlit Cloud → Settings → Secrets.")
        elif "429" in msg or "quota" in msg.lower():
            st.error("⏳ Gemini free quota exceeded — wait a minute and try again.")
        else:
            st.error(f"⚠️ Gemini API error: {msg[:300]}")
        return None, ""
    return answer, context


def answer_and_show(query, lang_key, speak=True, fkey=""):
    with st.spinner("🧠 Searching official law database + verified memory…"):
        ans, ctx = ask(query, lang_key)
    if ans is None:
        return None, ""
    st.markdown(ans)
    if ctx:
        st.markdown("<div class='src-note'>📚 Sources: official UAE law database + verified memory</div>", unsafe_allow_html=True)
    if speak:
        play_audio(tts_audio(re.sub(r"[#*`|>]", " ", ans)[:600], LANGS[lang_key]["tts"]))
    c1, c2 = st.columns([1, 11])
    with c1:
        if st.button("👍", key=f"up_{fkey}"):
            learn.log_feedback(query, ans, ctx, +1, lang_key)
            st.success("✅ Learned! Saved as trusted memory.")
    with c2:
        if st.button("👎", key=f"down_{fkey}"):
            learn.log_feedback(query, ans, ctx, -1, lang_key)
            st.info("📉 Logged — we'll steer away from this pattern.")
    return ans, ctx

# ---------------- Tabs ----------------
tab_chat, tab_tools = st.tabs(["💬 Chat", "🧰 Tools"])

with tab_chat:
    with st.expander("🔴 LIVE Voice Chat — hands-free conversation", expanded=False):
        st.markdown("""
        <div class="voice-panel">
          <div class="mic-big">🎙️</div>
          <p style='text-align:center;color:#ffb3b5;margin:0;font-size:13px;'>Speak in <b>any language</b> — bot replies <b>in your language</b>, out loud. Say <b>stop</b> to end.</p>
        </div>
        """, unsafe_allow_html=True)
        if not MIC_OK:
            st.caption("🎙️ Voice features unavailable (streamlit-mic-recorder missing). Text chat still works.")
        live_on = st.toggle("🎤 Start live conversation", key="live_toggle")
        if live_on and MIC_OK:
            rounds, stop = 0, False
            while rounds < 8 and not stop:
                listen_locale = LANGS[forced_lang or "en"]["stt"]
                spoken = speech_to_text(language=listen_locale, start_prompt=f"🗣️ Round {rounds+1}", stop_prompt="⏹", just_once=True, key=f"live_{rounds}")
                if not spoken:
                    stop = True
                    st.caption("🤫 No speech — session ended.")
                elif spoken.strip().lower() in ("stop", "නවත්වන්න", "நிறுத்து", "stop na"):
                    stop = True
                    st.success("🔴 Live session ended by voice.")
                else:
                    lk = detect_lang(spoken, fallback=(forced_lang or "en"))
                    with st.chat_message("user"):
                        st.markdown(spoken)
                    with st.chat_message("assistant"):
                        st.markdown(f"<span class='detected-pill'>🌍 {LANGS[lk]['flag']} {LANGS[lk]['name']}</span>", unsafe_allow_html=True)
                        ans, ctx = answer_and_show(spoken, lk, speak=True, fkey=f"live{rounds}")
                    if ans:
                        st.session_state.messages.append({"role": "user", "content": spoken, "lang": lk})
                        st.session_state.messages.append({"role": "assistant", "content": ans, "source": True})
                    rounds += 1
            if not stop and rounds >= 8:
                st.caption("Max rounds — restart to continue.")

    voice_text = None
    if MIC_OK:
        listen_locale = LANGS[forced_lang or "en"]["stt"]
        voice_text = speech_to_text(language=listen_locale, start_prompt="🎙️ Speak (any language)", stop_prompt="⏹", just_once=True, key="stt_main")
        if voice_text:
            lk = detect_lang(voice_text, fallback=(forced_lang or "en"))
            st.markdown(f"<span class='detected-pill'>🌍 Detected: {LANGS[lk]['flag']} {LANGS[lk]['name']}</span>", unsafe_allow_html=True)

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"] == "assistant" and m.get("source"):
                st.markdown("<div class='src-note'>📚 Official UAE law sources + verified memory</div>", unsafe_allow_html=True)

    user_prompt = st.chat_input("✍️ Ask anything about UAE labour law — any language, any script…")
    if voice_text:
        user_prompt = voice_text

    if user_prompt:
        lk = detect_lang(user_prompt, fallback=(forced_lang or "en"))
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        with st.chat_message("assistant"):
            st.markdown(f"<span class='detected-pill'>🌍 Answering in: {LANGS[lk]['flag']} {LANGS[lk]['name']}</span>", unsafe_allow_html=True)
            ans, ctx = answer_and_show(user_prompt, lk, speak=True, fkey=f"t{len(st.session_state.messages)}")
        if ans:
            st.session_state.messages.append({"role": "assistant", "content": ans, "source": True})

with tab_tools:
    st.markdown("### 🧮 End-of-Service Gratuity Calculator")
    st.caption("Art. 51(2), FD-L 33/2021 — basic wage only; resignation before 5 years reduces the amount.")
    g1, g2, g3 = st.columns(3)
    basic = g1.number_input("Monthly basic salary (AED)", min_value=0.0, value=5000.0, step=100.0)
    years = g2.number_input("Years of service", min_value=0.0, value=3.0, step=0.25)
    rmode = g3.selectbox("Resignation status", ["No resignation / 5+ yrs", "Resigned 1–3 yrs", "Resigned 3–5 yrs"])

    def gratuity_math(b, y, rm):
        daily = b / 30
        total = min(y, 5) * daily * 21 + max(0, y - 5) * daily * 30
        note = "✅ Full gratuity applies."
        if y < 1:
            total = 0
            note = "❌ Under 1 year of service → no gratuity."
        elif rm.startswith("Resigned 1–3"):
            total /= 3
            note = "⚠️ Resigned after 1–3 years → ⅓ of gratuity (Art. 51(2))."
        elif rm.startswith("Resigned 3–5"):
            total = total * 2 / 3
            note = "⚠️ Resigned after 3–5 years → ⅔ of gratuity (Art. 51(2))."
        if b and total > b * 24:
            total = b * 24
            note += " Capped at 2 years' basic wage."
        return total, note

    total, note = gratuity_math(basic, years, rmode)
    st.success(f"**Estimated gratuity: AED {total:,.0f}**  \n{note}")

    st.markdown("---")
    st.markdown("### 📝 Resignation Letter Generator")
    with st.form("resign_form"):
        r1, r2 = st.columns(2)
        name = r1.text_input("Your full name")
        comp = r2.text_input("Company / HR name")
        job = st.text_input("Your position")
        notice = st.number_input("Notice period (days)", min_value=30, max_value=90, value=30)
        go = st.form_submit_button("Generate Letter")
    if go and name and comp:
        letter = f"""**RESIGNATION LETTER**

Date: {datetime.today().strftime('%d %B %Y')}

To: {comp}
Subject: Resignation — {job}

Dear {comp},

I am writing to formally resign from my position as {job}, in accordance with Article 42 of Federal Decree-Law No. 33 of 2021. My last working day will be {notice} days from the date of this letter, following my {notice}-day contractual notice period.

Kindly settle my end-of-service entitlements (gratuity, leave balance and accrued dues) within 14 days of my final working day, per Articles 51–53.

Yours sincerely,
**{name}**"""
        st.markdown(letter)
        st.download_button("⬇️ Download (TXT)", letter, "resignation_letter.txt")

    st.markdown("---")
    st.markdown("### 🛡️ Labour Dispute Guide + MOHRE Contacts")
    st.markdown("""
- ☎️ **MOHRE call centre:** 600 59 0000
- 📱 **MOHRE UAE app** — file complaints, view your contract
- 🌐 **mohre.gov.ae** — e-services, complaint tracking
- 🤝 MOHRE attempts settlement within 2 weeks, then referral to labour court
- ⚖️ Claims under AED 50,000: **exempt from court fees** (Art. 16)
- ⏰ Limitation period: **1 year** from when the right became due (Art. 54)
""")

st.markdown("<p style='text-align:center;color:#9aa7ba;font-size:11px;margin-top:18px'>AI legal information, not legal advice • FD-L 33/2021 as amended (20/2023, 9/2024) • © 2026</p>", unsafe_allow_html=True)
