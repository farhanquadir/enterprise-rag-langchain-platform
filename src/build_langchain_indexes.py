from __future__ import annotations
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL, EXPORTS_DIR, VECTORSTORE_DIR
from src.utils import ensure_dir, load_pickle
from src.langchain_builders import sql_records_to_documents, doc_records_to_documents

def main() -> None:
    sql_records = load_pickle(EXPORTS_DIR / "sql_context.pkl")
    doc_records = load_pickle(EXPORTS_DIR / "doc_chunks.pkl")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    ensure_dir(VECTORSTORE_DIR)

    sql_docs = sql_records_to_documents(sql_records)
    doc_docs = doc_records_to_documents(doc_records)

    if sql_docs:
        sql_store = FAISS.from_documents(sql_docs, embeddings)
        sql_store.save_local(str(VECTORSTORE_DIR / "sql_store"))
        print(f"Built SQL LangChain FAISS store with {len(sql_docs)} documents")
    else:
        print("No SQL documents available for SQL store")

    if doc_docs:
        doc_store = FAISS.from_documents(doc_docs, embeddings)
        doc_store.save_local(str(VECTORSTORE_DIR / "doc_store"))
        print(f"Built DOC LangChain FAISS store with {len(doc_docs)} documents")
    else:
        print("No document chunks available for DOC store")

if __name__ == "__main__":
    main()
