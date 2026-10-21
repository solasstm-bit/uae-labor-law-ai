"""Build the multilingual vector knowledge base from scraped documents.

Uses `paraphrase-multilingual-MiniLM-L12-v2` so questions in Sinhala/Singlish,
Tamil, Malayalam, Hindi, Kannada, Urdu, Bengali, Nepali, Tagalog or Arabic
match the English legal text correctly.

Usage:  python ingest.py   (run scraper.py first)
"""
import pathlib

from langchain_text_splitters import RecursiveCharacterTextSplitter

RAW_DIR = pathlib.Path("data/raw")
DB_DIR = "chroma_db"


def main():
    if not RAW_DIR.exists() or not list(RAW_DIR.glob("*.txt")):
        print("No documents found. Run `python scraper.py` first.")
        return

    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    documents = []
    n_files = 0
    for f in sorted(RAW_DIR.glob("*.txt")):
        text = f.read_text(encoding="utf-8")
        header, _, body = text.partition("\n\n")
        title = next((l[7:] for l in header.splitlines() if l.startswith("TITLE: ")), f.name)
        source = next((l[8:] for l in header.splitlines() if l.startswith("SOURCE: ")), str(f))
        for chunk in splitter.split_text(body):
            documents.append(Document(chunk, metadata={"title": title, "source": source}))
        n_files += 1

    print(f"Embedding {len(documents)} chunks from {n_files} documents...")
    emb = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    Chroma.from_documents(documents, emb, persist_directory=DB_DIR)
    print(f"Done. Vector DB saved to ./{DB_DIR}")


if __name__ == "__main__":
    main()