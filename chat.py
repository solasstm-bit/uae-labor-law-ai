"""Chat tab: answer rendering, feedback, live voice chat, history (v2.3)."""
import re

import streamlit as st


def answer_and_show(client, db, verified_db, learn, query, lang_key, LANGS, engine, speak=True, fkey=""):
    with st.spinner("🧠 Searching official law database + verified memory…"):
        ans, ctx = engine.ask(client, db, verified_db, learn, query, LANGS[lang_key])
    if ans is None:
        return None, ""
    st.markdown(ans)
    if ctx:
        st.markdown("<div class='src-note'>📚 Sources: official UAE law database + verified memory</div>", unsafe_allow_html=True)
    if speak:
        clean = re.sub(r"[#*`|>]", " ", ans)[:600]
        engine.play_audio(engine.tts_audio(clean, lang_key))
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


def render(client, db, verified_db, learn, engine, LANGS, detect_lang, speech_to_text, MIC_OK, forced_lang):
    """Render the full chat tab."""
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
                        ans, ctx = answer_and_show(client, db, verified_db, learn, spoken, lk, LANGS, engine, speak=True, fkey=f"live{rounds}")
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
            ans, ctx = answer_and_show(client, db, verified_db, learn, user_prompt, lk, LANGS, engine, speak=True, fkey=f"t{len(st.session_state.messages)}")
        if ans:
            st.session_state.messages.append({"role": "assistant", "content": ans, "source": True})