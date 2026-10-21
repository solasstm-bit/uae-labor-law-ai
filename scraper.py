"""Official-source crawler for the UAE Labour Law RAG knowledge base.

Scrapes ONLY official UAE government sources (no random blogs):
  - u.ae            (UAE Government portal — private sector employment)
  - uaelegislation.gov.ae (official legislation portal — FD-L 33/2021 + amendments)

Saves clean text (+ official PDFs, auto-extracted) into ./data/raw.

Usage:  python scraper.py
"""
import io
import pathlib
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

RAW_DIR = pathlib.Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

SEEDS = [
    "https://u.ae/en/information-and-services/jobs/employment-in-the-private-sector",
    "https://uaelegislation.gov.ae/en/legislations/1541",   # FD-L 33/2021
    "https://uaelegislation.gov.ae/en/legislations/1547",   # amendment
]

ALLOWED_PREFIXES = (
    "https://u.ae/en/information-and-services/jobs",
    "https://uaelegislation.gov.ae/en/legislations",
)
MAX_PAGES = 60
TIMEOUT = 20
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; UAELawBot/1.0; research)"}

visited = set()
queue = list(SEEDS)
saved = 0


def clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
        tag.decompose()
    lines = [ln.strip() for ln in soup.get_text("\n").splitlines()]
    return "\n".join(ln for ln in lines if ln)


def save_doc(url: str, title: str, text: str):
    global saved
    fname = RAW_DIR / f"{abs(hash(url)) % 10**8:08d}.txt"
    fname.write_text(f"TITLE: {title}\nSOURCE: {url}\n\n{text}", encoding="utf-8")
    saved += 1
    print(f"[{saved:03d}] saved: {title[:70]}")


def handle_pdf(url: str, content: bytes):
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(content))
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        name = urlparse(url).path.split("/")[-1] or "official-law.pdf"
        save_doc(url, name, text)
    except Exception as e:
        print("  ! pdf failed:", e)


def crawl():
    while queue and len(visited) < MAX_PAGES:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
        except Exception as e:
            print("  ! skip:", url, e)
            continue
        ctype = r.headers.get("content-type", "")
        if "pdf" in ctype or url.lower().endswith(".pdf"):
            handle_pdf(url, r.content)
            continue
        if "html" not in ctype:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        save_doc(url, title, clean_text(soup))
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"].split("#")[0])
            if link.startswith(ALLOWED_PREFIXES) and link not in visited:
                queue.append(link)
        time.sleep(1.0)  # polite crawl delay — respect the servers
    print(f"\nDone. {saved} documents saved to {RAW_DIR}/")
    if not saved:
        print("Nothing saved — check your internet / the sites' robots policy.")


if __name__ == "__main__":
    crawl()