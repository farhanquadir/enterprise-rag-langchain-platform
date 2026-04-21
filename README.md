# Enterprise RAG LangChain Platform

A production-style hybrid Retrieval-Augmented Generation (RAG) system built using LangChain that integrates:

- Structured analytics data from a DuckDB warehouse  
- Unstructured business documents  
- Parallel, source-aware retrieval pipelines  
- Grounded answer synthesis with full source traceability  

This repository is an advanced extension of the original  
`enterprise-rag-ai-platform`, introducing LangChain-based orchestration, modular retrieval, and improved reasoning capabilities.

---

## 🚀 Key Capabilities

- LangChain-native architecture  
- Dual vector store design (SQL + documents)  
- Hybrid retrieval with routing + re-ranking  
- Business-aware reasoning  
- Grounded responses with source attribution  
- Streamlit UI  
- Google Colab-friendly workflow  

---

## 📊 Data Sources

### Structured Data (DuckDB Warehouse)

- ai_customer_context  
- mart_top_customers  
- mart_country_sales  
- mart_monthly_revenue  

### Unstructured Documents

- refund_policy.txt  
- loyalty_program.txt  
- support_escalation.txt  
- sales_strategy.txt  

---

## ⚙️ Quickstart (Google Colab)

```python
from google.colab import drive
drive.mount('/content/drive')
```

```python
from pathlib import Path
import os

BASE = Path('/content/drive/MyDrive/projects/enterprise-rag-langchain-platform')
DATA_PLATFORM_BASE = Path('/content/drive/MyDrive/projects/modern-data-platform-blueprint')
WAREHOUSE_DB = DATA_PLATFORM_BASE / 'data' / 'warehouse' / 'warehouse.db'

os.chdir(BASE)
os.environ['WAREHOUSE_DB'] = str(WAREHOUSE_DB)
```

```python
!pip install -q -r requirements.txt
```

```python
!python -m src.build_sample_docs
!python -m src.extract_sql_context
!python -m src.ingest_documents
!python -m src.build_langchain_indexes
!python -m src.run_demo
```

---

## 🧠 System Architecture

User Query → Router → SQL + Doc Retrieval → Re-ranking → Grounded Answer → UI

---

## 🧠 Why LangChain

- Standardized orchestration  
- FAISS vector store integration  
- HuggingFace embeddings  
- Modular retrieval pipelines  

---

## 🏁 Summary

This project demonstrates a production-ready hybrid RAG system that combines structured analytics with unstructured knowledge to produce explainable, decision-ready outputs.
