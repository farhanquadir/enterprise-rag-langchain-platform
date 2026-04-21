from __future__ import annotations

import streamlit as st

from src.langchain_hybrid_retriever import LangChainHybridRetriever
from src.answer_engine import build_grounded_answer

st.set_page_config(page_title="Enterprise RAG LangChain Platform", layout="wide")
st.title("Enterprise RAG LangChain Platform")
st.caption(
    "LangChain-orchestrated hybrid retrieval over warehouse-derived business context and operational documents."
)


@st.cache_resource
def get_retriever():
    return LangChainHybridRetriever()


retriever = get_retriever()

query = st.text_input(
    "Ask a question",
    value="Which customers are high value and what support policy applies to them?",
)

if st.button("Search"):
    output = retriever.search(query)

    st.subheader(f"Routing mode: {output['mode']}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### SQL results")
        for item in output["sql_results"][:5]:
            st.write(item["text"])
            st.caption(
                f"{item.get('table')} | raw_score={item['score']:.4f} | adjusted_score={item['adjusted_score']:.4f}"
            )

    with col2:
        st.markdown("### Document results")
        for item in output["doc_results"][:5]:
            st.write(item["text"])
            st.caption(
                f"{item.get('file_name')} | raw_score={item['score']:.4f} | adjusted_score={item['adjusted_score']:.4f}"
            )

    st.markdown("### Final grounded answer")
    st.text(build_grounded_answer(query, output))

    st.markdown("### Top combined sources")
    for item in output["combined"][:6]:
        label = item.get("table") or item.get("file_name") or item.get("id")
        st.markdown(f"**{label}** [{item.get('source_type')}]")
        st.write(item["text"])
        st.caption(
            f"raw_score={item['score']:.4f} | adjusted_score={item['adjusted_score']:.4f}"
        )