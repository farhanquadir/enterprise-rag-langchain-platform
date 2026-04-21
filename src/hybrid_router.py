from __future__ import annotations

SQL_HINTS = {
    "customer",
    "customers",
    "country",
    "countries",
    "revenue",
    "invoice",
    "sales",
    "monthly",
    "trend",
    "value",
    "top",
    "highest",
    "lifetime",
    "ltv",
    "high",
}

DOC_HINTS = {
    "policy",
    "program",
    "escalation",
    "guide",
    "memo",
    "refund",
    "support",
    "loyalty",
    "workflow",
    "procedure",
    "priority",
}


def _normalize(query: str) -> set[str]:
    cleaned = (
        query.lower()
        .replace("?", "")
        .replace(",", "")
        .replace(".", "")
        .replace(":", "")
        .replace(";", "")
    )
    return set(cleaned.split())


def is_high_value_query(query: str) -> bool:
    q = query.lower()
    return (
        "high value" in q
        or "high-value" in q
        or "premium customer" in q
        or "premium customers" in q
        or "priority support" in q
        or "lifetime value" in q
    )


def route_query(query: str) -> str:
    tokens = _normalize(query)
    sql_hits = len(tokens & SQL_HINTS)
    doc_hits = len(tokens & DOC_HINTS)

    if sql_hits >= doc_hits + 1:
        return "sql"
    if doc_hits >= sql_hits + 1:
        return "doc"
    return "hybrid"