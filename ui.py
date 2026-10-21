"""Animated 3D-glass dark UI styles + hero banner (v2.3)."""
import streamlit as st

STYLES = """
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
"""

HERO = """
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
"""


def render():
    st.markdown(STYLES, unsafe_allow_html=True)
    st.markdown(HERO, unsafe_allow_html=True)