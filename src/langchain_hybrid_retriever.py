from __future__ import annotations

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL, VECTORSTORE_DIR
from src.hybrid_router import route_query, is_high_value_query


class LangChainHybridRetriever:
    def __init__(self):
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        self.sql_store = FAISS.load_local(
            str(VECTORSTORE_DIR / "sql_store"),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        self.doc_store = FAISS.load_local(
            str(VECTORSTORE_DIR / "doc_store"),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    def _format_results(self, docs_scores, label: str):
        results = []
        for doc, score in docs_scores:
            item = dict(doc.metadata)
            item["text"] = doc.page_content
            item["score"] = float(score)
            item["store"] = label
            results.append(item)
        return results

    def _adjust_score(self, item: dict, mode: str, query: str) -> float:
        # LangChain FAISS returns lower-is-better distance
        score = -item["score"]

        source_type = item.get("source_type", "")
        table = item.get("table", "")
        text = item.get("text", "").lower()

        # Route-based source preference
        if mode == "sql" and source_type == "sql":
            score += 0.20
        elif mode == "doc" and source_type == "doc":
            score += 0.20
        elif mode == "hybrid":
            score += 0.05

        # Query-aware table preference
        q = query.lower()

        if "country" in q or "countries" in q:
            if table == "mart_country_sales":
                score += 0.25

        if "monthly" in q or "trend" in q or "revenue" in q:
            if table == "mart_monthly_revenue":
                score += 0.18

        if "customer" in q or "customers" in q:
            if table == "ai_customer_context":
                score += 0.12
            if table == "mart_top_customers":
                score += 0.10

        if "sales strategy" in q or "strategy" in q:
            if source_type == "doc" and "sales strategy" in text:
                score += 0.25

        if "loyalty" in q or "premium" in q:
            if source_type == "doc" and "loyalty program" in text:
                score += 0.25

        # High-value filtering preference
        if is_high_value_query(query):
            if "high_value" in text:
                score += 0.45
            elif "mid_value" in text:
                score += 0.10
            elif "low_value" in text:
                score -= 0.35

            if "priority support" in text or "customer success" in text:
                score += 0.20

        return score

    def _filter_sql_results(self, results: list[dict], query: str) -> list[dict]:
        if not is_high_value_query(query):
            return results

        high_value = [r for r in results if "high_value" in r.get("text", "").lower()]
        summary = [
            r for r in results
            if r.get("table") == "summary"
            and (
                "high value customers" in r.get("text", "").lower()
                or "priority support" in r.get("text", "").lower()
            )
        ]

        if high_value or summary:
            filtered = summary + high_value
            seen = set()
            deduped = []
            for item in filtered:
                key = item.get("id", item.get("text", ""))
                if key not in seen:
                    seen.add(key)
                    deduped.append(item)
            return deduped

        return results

    def search(self, query: str):
        mode = route_query(query)

        if mode == "sql":
            k_sql, k_doc = 10, 3
        elif mode == "doc":
            k_sql, k_doc = 3, 10
        else:
            k_sql, k_doc = 8, 8

        sql_results = self._format_results(
            self.sql_store.similarity_search_with_score(query, k=k_sql),
            "sql_store",
        )
        doc_results = self._format_results(
            self.doc_store.similarity_search_with_score(query, k=k_doc),
            "doc_store",
        )

        sql_results = self._filter_sql_results(sql_results, query)

        combined = sql_results + doc_results
        for item in combined:
            item["adjusted_score"] = self._adjust_score(item, mode, query)

        combined.sort(key=lambda x: x["adjusted_score"], reverse=True)

        # Also sort per-channel for cleaner UI
        sql_results = sorted(
            sql_results,
            key=lambda x: self._adjust_score(x, mode, query),
            reverse=True,
        )
        doc_results = sorted(
            doc_results,
            key=lambda x: self._adjust_score(x, mode, query),
            reverse=True,
        )

        return {
            "mode": mode,
            "sql_results": sql_results,
            "doc_results": doc_results,
            "combined": combined,
        }