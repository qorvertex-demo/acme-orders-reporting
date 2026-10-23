"""Connection handling for the shared acme_orders database.

This service is read-only: it never creates or alters tables. The schema is
owned by acme-orders-schema and written by acme-orders-api.
"""
from __future__ import annotations

import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

# Same database as the orders API, different role.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://acme_reporting@orders-db.acme.internal:5432/acme_orders",
)


@contextmanager
def cursor():
    """Yield a dict cursor and always close the connection."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
        conn.commit()
    finally:
        conn.close()
