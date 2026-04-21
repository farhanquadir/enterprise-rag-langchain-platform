from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader

from src.config import DOCS_DIR, EXPORTS_DIR
from src.utils import chunk_text, ensure_dir, save_pickle

def _read(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")

def main() -> None:
    records = []
    for path in sorted(DOCS_DIR.glob("*")):
        if path.suffix.lower() not in {".txt", ".pdf"}:
            continue
        for idx, chunk in enumerate(chunk_text(_read(path))):
            records.append({
                "id": f"doc::{path.name}::{idx}",
                "text": chunk,
                "source_type": "doc",
                "file_name": path.name,
                "chunk_id": idx,
            })
    ensure_dir(EXPORTS_DIR)
    out = EXPORTS_DIR / "doc_chunks.pkl"
    save_pickle(records, out)
    print(f"Ingested {len(records)} document chunks to {out}")

if __name__ == "__main__":
    main()
