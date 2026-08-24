import json
import re
from pathlib import Path


ORDERS_FILE = Path("data/orders.json")


def load_orders():
    with open(ORDERS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["orders"]


def normalize_order_id(order_id):
    if not order_id:
        return None

    normalized = order_id.strip().upper()
    normalized = re.sub(r"^[^\w]*|[^\w]*$", "", normalized)

    return normalized


def sanitize_order(order):
    safe = {
        "order_id": order["order_id"],
        "membership_tier": order.get("membership_tier"),
        "items": [
            {
                "name": item["name"],
                "quantity": item["quantity"],
                "final_sale": item["final_sale"]
            }
            for item in order.get("items", [])
        ],
        "placed_at": order.get("placed_at"),
        "status": order.get("status"),
        "status_updated_at": order.get("status_updated_at"),
        "shipped_at": order.get("shipped_at"),
        "delivered_at": order.get("delivered_at"),
        "carrier": order.get("carrier"),
        "tracking_number": order.get("tracking_number"),
        "estimated_delivery": order.get("estimated_delivery"),
        "customer_safe_message": order.get("customer_safe_message")
    }

    return safe


def lookup_order(order_id):
    normalized_id = normalize_order_id(order_id)

    if not normalized_id:
        return {
            "found": False,
            "error": "Order ID is required."
        }

    orders = load_orders()

    for order in orders:

        if order.get("order_id") != normalized_id:
            continue

        safe_order = sanitize_order(order)

        status = safe_order.get("status")

        # Status is authoritative.
        # Remove stale shipping information for cancelled/returned orders.
        if status in {"cancelled", "returned"}:
            safe_order["shipped_at"] = None
            safe_order["delivered_at"] = None
            safe_order["carrier"] = None
            safe_order["tracking_number"] = None
            safe_order["estimated_delivery"] = None

        # Do not invent an ETA when none exists.
        if status == "shipped" and not safe_order.get("estimated_delivery"):
            safe_order["estimated_delivery"] = None

        return {
            "found": True,
            "order": safe_order
        }

    return {
        "found": False,
        "error": (
            "Order was not found. "
            "Please check the order ID or contact support."
        )
    }


if __name__ == "__main__":

    test_ids = [
        "ORD-1007",
        "ord-1007",
        "  ORD-1007  ",
        "ORD-1004",
        "ORD-1011",
        "ORD-9999"
    ]

    for order_id in test_ids:
        print(f"\nLookup: {order_id}")
        print(lookup_order(order_id))