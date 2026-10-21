# ⚖️ UAE Labour Law AI

A multilingual AI legal advisor for UAE private-sector employment law (Federal Decree-Law No. 33/2021, as amended by FD-Laws 20/2023 and 9/2024). Ask in **any of 11 languages** — get the answer **in your language**, spoken out loud.

## ✨ Features

- 🌍 **Auto language detection** — ask in Sinhala, Singlish, Tamil, Hindi, Kannada, Malayalam, Urdu, Arabic, Bengali, Nepali, Tagalog or English; the bot replies in that language's script
- 🇱🇰 **Singlish → Sinhala** — romanized Sinhala questions get proper Sinhala script answers
- 🎙️ **Voice typing** per language (browser STT)
- 🔴 **Live voice chat** — hands-free: speak → answer → neural TTS speaks it back (edge-tts voices)
- 🧠 **Self-learning** — 👍/👎 feedback creates "verified memory" injected into future answers (reward-based RL-lite loop)
- 📚 **RAG grounded** in official UAE sources only (u.ae + uaelegislation.gov.ae) — no hallucinated articles
- 🧰 **Tools** — gratuity calculator (Art. 51), resignation letter generator, MOHRE dispute guide

## 🚀 Run locally

```bash
pip install -r requirements.txt
cp .env.example .env        # add your GEMINI_API_KEY
python scraper.py           # crawl official law sources
python ingest.py            # build the Chroma vector DB
python learn.py             # (optional) rebuild verified memory
streamlit run app.py
```

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub (done — you're here!)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select this repo
3. Branch: `develop` · Main file: `app.py`
4. In **Secrets** add:
   ```toml
   GEMINI_API_KEY = "your_new_rotated_key_here"
   ```
   ⚠️ Never commit the real API key to the repo — use Secrets.
5. Deploy → you get a public URL like `https://uae-labor-law-ai.streamlit.app`

First run downloads the multilingual embedding model (~2–5 min warm-up). To skip the crawler on the server, run `scraper.py` + `ingest.py` locally and commit the `chroma_db/` folder.

## 📄 License / disclaimer

AI legal **information**, not legal advice. For binding advice consult a licensed UAE advocate or MOHRE (600 59 0000).
