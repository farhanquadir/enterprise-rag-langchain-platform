from __future__ import annotations

from src.langchain_hybrid_retriever import LangChainHybridRetriever
from src.answer_engine import build_grounded_answer

QUERIES = [
    "Which customers are high value and what support policy applies to them?",
    "What does the loyalty program say about premium customers?",
    "Which countries generate the most revenue?",
    "Summarize the monthly revenue trend and the sales strategy.",
]


def main():
    retriever = LangChainHybridRetriever()

    for query in QUERIES:
        output = retriever.search(query)
        print("=" * 100)
        print(build_grounded_answer(query, output))
        print()


if __name__ == "__main__":
    main()