from __future__ import annotations
from pathlib import Path
import pickle

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def save_pickle(obj, path: Path) -> None:
    ensure_dir(path.parent)
    with open(path, "wb") as f:
        pickle.dump(obj, f)

def load_pickle(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks
