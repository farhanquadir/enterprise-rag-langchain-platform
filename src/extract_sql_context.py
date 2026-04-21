from __future__ import annotations

from typing import Any
import duckdb
import pandas as pd

from src.config import WAREHOUSE_DB, EXPORTS_DIR
from src.utils import ensure_dir, save_pickle


def _safe_fetch(con: duckdb.DuckDBPyConnection, table: str) -> pd.DataFrame:
    try:
        return con.execute(f"select * from {table}").fetchdf()
    except Exception:
        return pd.DataFrame()


def _value_segment(lifetime_value: float) -> str:
    if lifetime_value >= 50000:
        return "high_value"
    if lifetime_value >= 10000:
        return "mid_value"
    return "low_value"


def extract_sql_context() -> list[dict[str, Any]]:
    con = duckdb.connect(str(WAREHOUSE_DB), read_only=True)
    try:
        tables = [t[0] for t in con.execute("show tables").fetchall()]
        print("Available tables:", tables)

        records: list[dict[str, Any]] = []

        # -----------------------------
        # mart_monthly_revenue
        # -----------------------------
        df = _safe_fetch(con, "mart_monthly_revenue")
        if not df.empty:
            df = df.sort_values("year_month")
            for _, row in df.iterrows():
                records.append(
                    {
                        "id": f"mart_monthly_revenue::{row.get('year_month', 'unknown')}",
                        "text": (
                            f"In {row.get('year_month', 'unknown')}, revenue was "
                            f"{float(row.get('revenue', 0.0)):.2f} from "
                            f"{int(row.get('invoices', 0) or 0)} invoices and "
                            f"{int(row.get('order_lines', 0) or 0)} order lines."
                        ),
                        "source_type": "sql",
                        "table": "mart_monthly_revenue",
                        "entity_id": str(row.get("year_month", "unknown")),
                    }
                )

            # Synthetic monthly summary
            top_month = df.sort_values("revenue", ascending=False).iloc[0]
            low_month = df.sort_values("revenue", ascending=True).iloc[0]
            records.append(
                {
                    "id": "summary::monthly_revenue_trend",
                    "text": (
                        f"Monthly revenue peaked in {top_month['year_month']} at "
                        f"{float(top_month['revenue']):.2f}. The lowest month was "
                        f"{low_month['year_month']} at {float(low_month['revenue']):.2f}. "
                        f"Revenue fluctuated across the year and should be reviewed alongside sales strategy and customer retention efforts."
                    ),
                    "source_type": "sql",
                    "table": "summary",
                    "entity_id": "monthly_revenue_trend",
                }
            )

        # -----------------------------
        # mart_country_sales
        # -----------------------------
        df = _safe_fetch(con, "mart_country_sales")
        if not df.empty:
            # Keep top countries only for cleaner retrieval
            df = df.sort_values("total_revenue", ascending=False).head(20)

            for _, row in df.iterrows():
                records.append(
                    {
                        "id": f"mart_country_sales::{row.get('country', 'Unknown')}",
                        "text": (
                            f"Country {row.get('country', 'Unknown')} generated "
                            f"{float(row.get('total_revenue', 0.0)):.2f} in revenue across "
                            f"{int(row.get('invoice_count', 0) or 0)} invoices and "
                            f"{int(row.get('customer_count', 0) or 0)} customers."
                        ),
                        "source_type": "sql",
                        "table": "mart_country_sales",
                        "entity_id": str(row.get("country", "Unknown")),
                    }
                )

            top_country = df.iloc[0]
            records.append(
                {
                    "id": "summary::top_country_revenue",
                    "text": (
                        f"The top revenue-generating country was {top_country['country']} "
                        f"with {float(top_country['total_revenue']):.2f} in revenue. "
                        f"Country-level performance should be used to guide regional sales prioritization."
                    ),
                    "source_type": "sql",
                    "table": "summary",
                    "entity_id": "top_country_revenue",
                }
            )

        # -----------------------------
        # mart_top_customers
        # -----------------------------
        df = _safe_fetch(con, "mart_top_customers")
        if not df.empty:
            df = df.sort_values("total_revenue", ascending=False).head(100)

            for _, row in df.iterrows():
                customer_key = str(row.get("customer_key", "UNKNOWN"))
                records.append(
                    {
                        "id": f"mart_top_customers::{customer_key}",
                        "text": (
                            f"Top customer {customer_key} from {row.get('country', 'Unknown')} generated "
                            f"{float(row.get('total_revenue', 0.0)):.2f} in revenue across "
                            f"{int(row.get('invoice_count', 0) or 0)} invoices. "
                            f"Last order timestamp was {row.get('last_order_ts', 'unknown')}."
                        ),
                        "source_type": "sql",
                        "table": "mart_top_customers",
                        "entity_id": customer_key,
                    }
                )

        # -----------------------------
        # ai_customer_context
        # -----------------------------
        df = _safe_fetch(con, "ai_customer_context")
        if not df.empty:
            df = df.sort_values("lifetime_value", ascending=False)

            # Keep top 200 customers for retrieval quality
            top_df = df.head(200).copy()

            high_count = 0
            mid_count = 0
            low_count = 0

            for _, row in top_df.iterrows():
                customer_key = str(row.get("customer_key", "UNKNOWN"))
                lifetime_value = float(row.get("lifetime_value", 0.0))
                value_segment = _value_segment(lifetime_value)

                if value_segment == "high_value":
                    high_count += 1
                elif value_segment == "mid_value":
                    mid_count += 1
                else:
                    low_count += 1

                records.append(
                    {
                        "id": f"ai_customer_context::{customer_key}",
                        "text": (
                            f"Customer {customer_key} is a {value_segment} customer from {row.get('country', 'Unknown')}. "
                            f"Lifetime value is {lifetime_value:.2f} across "
                            f"{int(row.get('invoice_count', 0) or 0)} invoices. "
                            f"Last order timestamp was {row.get('last_order_ts', 'unknown')}. "
                            f"They purchased {int(row.get('distinct_products_purchased', 0) or 0)} distinct products."
                        ),
                        "source_type": "sql",
                        "table": "ai_customer_context",
                        "entity_id": customer_key,
                        "value_segment": value_segment,
                        "lifetime_value": lifetime_value,
                    }
                )

            records.append(
                {
                    "id": "summary::customer_value_segments",
                    "text": (
                        f"Among the top 200 customers by lifetime value, there are "
                        f"{high_count} high_value customers, {mid_count} mid_value customers, "
                        f"and {low_count} low_value customers. "
                        f"High value customers should receive priority support, proactive engagement, and escalation when repeated issues occur."
                    ),
                    "source_type": "sql",
                    "table": "summary",
                    "entity_id": "customer_value_segments",
                }
            )

            records.append(
                {
                    "id": "summary::high_value_customers",
                    "text": (
                        "High value customers are those with lifetime value above $50,000. "
                        "These customers should receive priority support, proactive account reviews, "
                        "and escalation to customer success when issues arise."
                    ),
                    "source_type": "sql",
                    "table": "summary",
                    "entity_id": "high_value_customers",
                }
            )

        return records

    finally:
        con.close()


def main() -> None:
    records = extract_sql_context()
    ensure_dir(EXPORTS_DIR)
    out = EXPORTS_DIR / "sql_context.pkl"
    save_pickle(records, out)
    print(f"Extracted {len(records)} SQL records to {out}")


if __name__ == "__main__":
    main()