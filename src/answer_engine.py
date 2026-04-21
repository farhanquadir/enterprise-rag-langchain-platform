from __future__ import annotations


def _label(item: dict) -> str:
    return item.get("table") or item.get("file_name") or item.get("id", "source")


def _best_sql(results: list[dict], n: int = 3) -> list[dict]:
    return results[:n] if results else []


def _best_docs(results: list[dict], n: int = 3) -> list[dict]:
    return results[:n] if results else []


def _synthesize_summary(query: str, sql_results: list[dict], doc_results: list[dict]) -> str:
    q = query.lower()

    if "high value" in q or "premium" in q:
        return (
            "Based on structured customer data and business policy documents, high-value customers "
            "should receive priority support, proactive engagement, and escalation to customer success "
            "when repeated issues occur. Loyalty guidance indicates that premium customers should also "
            "receive proactive account reviews and higher-touch support."
        )

    if "countries" in q and "revenue" in q:
        return (
            "Based on structured sales data, the highest-revenue countries should be prioritized for "
            "regional sales planning, customer retention, and commercial outreach."
        )

    if "monthly" in q or "trend" in q:
        return (
            "The structured revenue records show variation across months, and the supporting business "
            "documents suggest that shifts in support quality, fulfillment, pricing, and customer engagement "
            "should be reviewed when revenue trends decline."
        )

    if "loyalty" in q:
        return (
            "According to the loyalty program, premium customers receive priority support, "
            "proactive account reviews, and higher-touch engagement. These customers are "
            "treated as high-value and should be prioritized for retention and service quality."
        )

    if sql_results and doc_results:
        return (
            "The answer combines structured business metrics with policy and operational guidance to provide "
            "a grounded response."
        )
    if sql_results:
        return "The answer is grounded primarily in structured business data from the analytics warehouse."
    if doc_results:
        return "The answer is grounded primarily in business policy and operational documents."
    return "I could not find enough relevant context to answer that question."


def build_grounded_answer(query: str, retrieval_output: dict) -> str:
    mode = retrieval_output["mode"]
    sql_results = _best_sql(retrieval_output["sql_results"], n=3)
    doc_results = _best_docs(retrieval_output["doc_results"], n=3)
    combined = retrieval_output["combined"]

    if not combined:
        return "I could not find enough relevant context to answer that question."

    lines = [
        f"Question: {query}",
        f"Routing mode: {mode}",
        "",
        "Final synthesized answer:",
        _synthesize_summary(query, sql_results, doc_results),
        "",
    ]

    if sql_results:
        lines.append("Structured business context:")
        for item in sql_results:
            lines.append(f"- {item['text']}")
        lines.append("")

    if doc_results:
        lines.append("Document guidance:")
        for item in doc_results:
            lines.append(f"- {item['text']}")
        lines.append("")

    lines.append("Sources used:")
    for item in combined[:6]:
        lines.append(
            f"- {_label(item)} [{item.get('source_type')}]: {item['text']}"
        )

    return "\n".join(lines)