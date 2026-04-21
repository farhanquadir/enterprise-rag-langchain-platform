from __future__ import annotations
from langchain_core.documents import Document

def sql_records_to_documents(records: list[dict]) -> list[Document]:
    docs = []
    for r in records:
        docs.append(
            Document(
                page_content=r["text"],
                metadata={
                    "source_type": r.get("source_type", "sql"),
                    "table": r.get("table", ""),
                    "entity_id": r.get("entity_id", ""),
                    "id": r.get("id", ""),
                },
            )
        )
    return docs

def doc_records_to_documents(records: list[dict]) -> list[Document]:
    docs = []
    for r in records:
        docs.append(
            Document(
                page_content=r["text"],
                metadata={
                    "source_type": r.get("source_type", "doc"),
                    "file_name": r.get("file_name", ""),
                    "chunk_id": r.get("chunk_id", ""),
                    "id": r.get("id", ""),
                },
            )
        )
    return docs
