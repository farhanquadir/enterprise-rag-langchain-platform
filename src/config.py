from __future__ import annotations
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
DATA_DIR = ROOT / "data"
EXPORTS_DIR = DATA_DIR / "exports"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"
WAREHOUSE_DB = Path(os.environ.get("WAREHOUSE_DB", ROOT / "data" / "warehouse" / "warehouse.db"))
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TOP_K = int(os.environ.get("TOP_K", "6"))
