"""Self-learning layer — reward-based feedback loop (practical RL-lite).

How it learns:
  1. Every answer can be rated 👍 / 👎 by real users (the reward signal).
  2. 👍 answers become VERIFIED MEMORY: injected as high-trust context for
     similar future questions, and indexed into a separate `chroma_verified`
     collection so retrieval improves from human feedback.
  3. 👎 answers are logged and the model is steered away from that pattern.

CLI:  python learn.py retrain    (rebuild verified-answer memory from feedback)
"""
import json
import os
import pathlib
from datetime import datetime, timezone

LOG = pathlib.Path("data/feedback.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)


def log_feedback(question: str, answer: str, sources: str, reward: int, lang: str):
    """reward: +1 (good answer) or -1 (bad answer)."""
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "answer": answer,
            "sources": (sources or "")[:4000],
            "reward": reward,
            "lang": lang,
        }, ensure_ascii=False) + "\n")


def _records():
    if not LOG.exists():
        return []
    out = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def feedback_stats():
    recs = _records()
    return {
        "up": sum(1 for r in recs if r.get("reward") == 1),
        "down": sum(1 for r in recs if r.get("reward") == -1),
        "total": len(recs),
    }


def _overlap(a: str, b: str) -> float:
    A, B = set(a.lower().split()), set(b.lower().split())
    return len(A & B) / (len(A | B) or 1)


def best_verified(question: str, k: int = 2):
    """High-reward past Q&A pairs most similar to this question -> trusted memory."""
    scored = [(_overlap(r["question"], question), r) for r in _records() if r.get("reward") == 1]
    scored.sort(key=lambda x: -x[0])
    return [rec for score, rec in scored[:k] if score >= 0.25]


def retrain():
    """Rebuild the verified-answer vector collection from thumbs-up feedback."""
    recs = [r for r in _records() if r.get("reward") == 1]
    if not recs:
        print("No positive feedback yet — nothing to learn.")
        return
    import shutil
    if os.path.isdir("chroma_verified"):
        shutil.rmtree("chroma_verified")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
    emb = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    docs = [Document(page_content=f"Q: {r['question']}\nA: {r['answer']}",
                     metadata={"type": "verified", "lang": r.get("lang", "English")})
            for r in recs]
    Chroma.from_documents(docs, emb, persist_directory="chroma_verified")
    print(f"Learned {len(docs)} verified answers into chroma_verified.")


if __name__ == "__main__":
    retrain()