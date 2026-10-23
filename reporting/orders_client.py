"""Client for the orders API.

Reporting reads most of what it needs straight from the shared database, but an
order's live detail (including items) is owned by the API, so enrichment goes
through HTTP rather than reaching into another service's write path.
"""
from __future__ import annotations

import os

import httpx

ORDERS_API_URL = os.environ.get("ORDERS_API_URL", "http://orders-api.acme.internal:4010")


class OrdersClient:
    def __init__(self, base_url: str | None = None, timeout: float = 5.0):
        self.base_url = (base_url or ORDERS_API_URL).rstrip("/")
        self._client = httpx.Client(timeout=timeout)

    def get_order(self, order_id: int) -> dict | None:
        """Fetch one order with its line items. None when it no longer exists."""
        response = self._client.get(f"{self.base_url}/api/v1/orders/{order_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def mark_shipped(self, order_id: int) -> dict:
        """Used by the nightly fulfilment job."""
        response = self._client.request(
            "PATCH",
            f"{self.base_url}/api/v1/orders/{order_id}/status",
            json={"status": "shipped"},
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()
