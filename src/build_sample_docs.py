from __future__ import annotations
from src.config import DOCS_DIR
from src.utils import ensure_dir

DOCS = {
    "refund_policy.txt": '''Refund Policy

Customers may request refunds within 30 days of invoice date for damaged, defective, or duplicate items.
Orders above $5,000 should be reviewed by premium support before approval.
If multiple refunds occur for a high-value customer, notify the account manager.
''',
    "loyalty_program.txt": '''Loyalty Program

Customers are grouped into Standard, Growth, and Premium tiers based on annual revenue and purchase consistency.
Premium customers receive priority support and proactive account reviews.
Growth customers should be evaluated for upsell campaigns when their recent monthly purchase volume is rising.
''',
    "support_escalation.txt": '''Support Escalation Guide

Any customer with lifetime revenue above $50,000 and repeated issues should be escalated to customer success.
Refund disputes above $2,500 should be reviewed jointly by finance and support.
If multiple customers from the same country report delays, the regional operations manager should be notified.
''',
    "sales_strategy.txt": '''Sales Strategy Memo

Focus retention and upsell efforts on high-revenue customers and countries.
Where monthly revenue dips, commercial teams should investigate support, discounting, and fulfillment issues.
The customer summary context table should be used to prioritize outreach.
''',
}

def main() -> None:
    ensure_dir(DOCS_DIR)
    for name, content in DOCS.items():
        (DOCS_DIR / name).write_text(content.strip() + "\n", encoding="utf-8")
    print(f"Wrote {len(DOCS)} documents to {DOCS_DIR}")

if __name__ == "__main__":
    main()
