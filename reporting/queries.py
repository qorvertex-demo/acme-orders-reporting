"""Read-side queries over the shared order tables."""
from __future__ import annotations

from .db import cursor


def daily_revenue(days: int = 30) -> list[dict]:
    """Revenue and order count per day, excluding cancelled orders."""
    with cursor() as cur:
        cur.execute(
            """
            SELECT date_trunc('day', placed_at)::date AS day,
                   COUNT(*)                            AS order_count,
                   SUM(total_cents)                    AS revenue_cents
              FROM orders
             WHERE status <> 'cancelled'
               AND placed_at >= now() - make_interval(days => %s)
             GROUP BY 1
             ORDER BY 1 DESC
            """,
            (days,),
        )
        return list(cur.fetchall())


def top_customers(limit: int = 10) -> list[dict]:
    """Customers by lifetime spend."""
    with cursor() as cur:
        cur.execute(
            """
            SELECT c.email,
                   c.display_name,
                   COUNT(o.id)          AS order_count,
                   SUM(o.total_cents)   AS lifetime_cents
              FROM customers c
              JOIN orders o ON o.customer_id = c.id
             WHERE o.status <> 'cancelled'
             GROUP BY c.id, c.email, c.display_name
             ORDER BY lifetime_cents DESC
             LIMIT %s
            """,
            (limit,),
        )
        return list(cur.fetchall())


def best_selling_skus(limit: int = 10) -> list[dict]:
    """Units shipped per SKU, straight off the line items."""
    with cursor() as cur:
        cur.execute(
            """
            SELECT i.sku,
                   SUM(i.quantity)                    AS units,
                   SUM(i.quantity * i.unit_cents)     AS gross_cents
              FROM order_items i
              JOIN orders o ON o.id = i.order_id
             WHERE o.status <> 'cancelled'
             GROUP BY i.sku
             ORDER BY units DESC
             LIMIT %s
            """,
            (limit,),
        )
        return list(cur.fetchall())


def totals_drift() -> list[dict]:
    """Orders whose cached total disagrees with their items.

    Reads the `order_totals` view the schema repo defines. A non-empty result
    means someone wrote `orders` without calling `recalc_order_total`.
    """
    with cursor() as cur:
        cur.execute(
            """
            SELECT t.order_id, t.customer_email, t.computed_cents, o.total_cents
              FROM order_totals t
              JOIN orders o ON o.id = t.order_id
             WHERE t.computed_cents <> o.total_cents
            """
        )
        return list(cur.fetchall())
