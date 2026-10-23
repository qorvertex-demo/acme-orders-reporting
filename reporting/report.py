"""Command-line entry point: print the daily report."""
from __future__ import annotations

import argparse
import json

from .orders_client import OrdersClient
from .queries import best_selling_skus, daily_revenue, top_customers, totals_drift


def build_report(days: int, enrich_order_id: int | None = None) -> dict:
    report = {
        "daily_revenue": daily_revenue(days),
        "top_customers": top_customers(),
        "best_selling_skus": best_selling_skus(),
        "totals_drift": totals_drift(),
    }
    if enrich_order_id is not None:
        client = OrdersClient()
        try:
            report["sample_order"] = client.get_order(enrich_order_id)
        finally:
            client.close()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Acme order reporting")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--order", type=int, default=None, help="enrich with one order from the API")
    args = parser.parse_args()
    print(json.dumps(build_report(args.days, args.order), indent=2, default=str))


if __name__ == "__main__":
    main()
