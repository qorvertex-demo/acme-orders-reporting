> **Part of the [QorVertex live demo](https://qorvertex.com).** A small sample application that shows a shared PostgreSQL database: one repository owns the schema, others read and write it, and a deployment repository wires them together. It is intentionally minimal and not production code.

# acme-orders-reporting

Read-only reporting over the **shared `acme_orders` database** — the same
database `acme-orders-api` writes and `acme-orders-schema` owns.

It couples to the rest of the system two ways:

- **Database**: reads `orders`, `order_items`, `customers` and the
  `order_totals` view directly.
- **HTTP**: calls `acme-orders-api` for live order detail and to mark orders
  shipped, rather than writing another service's tables.

```bash
pip install -r requirements.txt
DATABASE_URL=postgresql://user:pass@host:5432/acme_orders \
ORDERS_API_URL=http://orders-api:4010 \
python -m reporting.report --days 7
```
