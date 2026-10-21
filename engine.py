"""RAG engine: vector search + dynamic Gemini model discovery + TTS voices (v2.3)."""
import base64
import pathlib
import re
import tempfile

import streamlit as st

EDGE_VOICES = {
    "si": "si-LK-ThiliniNeural", "ta": "ta-IN-PallaviNeural", "hi": "hi-IN-MadhurNeural",
    "kn": "kn-IN-SapnaNeural", "ml": "ml-IN-SomapookNeural", "ur": "ur-PK-UzmaNeural",
    "ar": "ar-AE-FatimaNeural", "bn": "bn-IN-TanishaaNeural", "ne": "ne-NP-HemkalaNeural",
    "tl": "fil-PH-AngeloNeural", "en": "en-AE-FatimaNeural",
}

STATIC_MODELS = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]


@st.cache_resource
def load_db(path):
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    if not pathlib.Path(path).exists():
        return None
    emb = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    return Chroma(persist_directory=path, embedding_function=emb)


@st.cache_resource
def discover_models(client):
    """Ask the API which models actually exist for this key (fixes 404s)."""
    found = []
    try:
        for m in client.models.list():
            name = getattr(m, "name", "") or ""
            actions = getattr(m, "supported_actions", None) or []
            if "generateContent" in actions and "flash" in name and "embedding" not in name:
                found.append(name)
    except Exception:
        pass
    return found


def gemini_generate(client, prompt: str) -> str:
    """Try static aliases, then every available model from the API list."""
    last_err = None
    tried = set()
    for model in STATIC_MODELS + [m for m in discover_models(client) if m not in STATIC_MODELS]:
        if model in tried:
            continue
        tried.add(model)
        try:
            return client.models.generate_content(model=model, contents=prompt).text
        except Exception as e:
            last_err = e
    raise last_err


def build_context(db, verified_db, learn, query):
    """Collect context parts from verified memory + official law DB."""
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
    return parts


def ask(client, db, verified_db, learn, query, lang):
    """RAG: context -> Gemini. Returns (answer, context_string)."""
    parts = build_context(db, verified_db, learn, query)
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
CRITICAL LANGUAGE RULE: Reply fully in: {lang['out']}. Even if the question is in Singlish or another language, the final answer must be in the user's language's natural script.
Keep it concise (under 180 words). Cite articles inside the answer when available.
{('CONTEXT:\n' + context) if grounded else ''}
QUESTION: {query}"""

    try:
        answer = gemini_generate(client, prompt)
    except Exception as e:
        msg = str(e)
        if "API key" in msg or "401" in msg or "permission" in msg.lower():
            st.error("🔑 Gemini API key problem: the key is missing, revoked, or invalid. "
                     "Check the app's Secrets (GEMINI_API_KEY) in Streamlit Cloud → Settings → Secrets.")
        elif "429" in msg or "quota" in msg.lower():
            st.error("⏳ Gemini free quota exceeded — wait a minute and try again.")
        elif "404" in msg:
            st.error("🔎 No Gemini model found for this API key. The key may be the wrong type — "
                     "create a **Gemini API key** (starts with `AIza...`) at aistudio.google.com/apikey "
                     "and update Secrets.")
        else:
            st.error(f"⚠️ Gemini API error: {msg[:300]}")
        return None, ""
    return answer, context


def tts_audio(text, lang_key):
    """Neural TTS (edge-tts) with gTTS fallback. Returns mp3 bytes or None."""
    try:
        import asyncio
        import edge_tts
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            asyncio.run(edge_tts.Communicate(text, EDGE_VOICES.get(lang_key, "en-AE-FatimaNeural")).save(f.name))
            return pathlib.Path(f.name).read_bytes()
    except Exception:
        try:
            from gtts import gTTS
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                gTTS(text=text, lang=lang_key).save(f.name)
                return pathlib.Path(f.name).read_bytes()
        except Exception:
            return None


def play_audio(b):
    if b:
        b64 = base64.b64encode(b).decode()
        st.markdown(f"<audio controls autoplay src='data:audio/mp3;base64,{b64}' type='audio/mpeg' style='width:100%;margin-top:8px;'></audio>", unsafe_allow_html=True)