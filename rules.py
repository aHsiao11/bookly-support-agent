"""Bookly business rules: the deterministic gate.

The model NEVER decides refund eligibility. It asks this layer.
Policy enforcement in code = provable behavior where money moves,
immune to a persuasive customer talking the model into caving.
"""

from datetime import date, datetime

RETURN_WINDOW_DAYS = 30
TODAY = date(2026, 10, 15)  # frozen for reproducible demos


def check_refund_eligibility(order: dict) -> dict:
    """The single authority on whether a refund may proceed."""
    status = order.get("status")

    if status == "refunded":
        return {"eligible": False, "reason": "This order has already been refunded."}

    if status in ("processing", "shipped"):
        return {
            "eligible": False,
            "reason": (
                f"Order {order['order_id']} hasn't been delivered yet, so it can't "
                "be refunded as a return. It may be eligible for cancellation instead."
            ),
        }

    if status == "delivered":
        delivered = datetime.strptime(order["delivered_date"], "%Y-%m-%d").date()
        days_since = (TODAY - delivered).days
        if days_since <= RETURN_WINDOW_DAYS:
            return {
                "eligible": True,
                "reason": f"Delivered {days_since} days ago — within the {RETURN_WINDOW_DAYS}-day window.",
                "refund_amount": order["price"],
            }
        return {
            "eligible": False,
            "reason": (
                f"Delivered {days_since} days ago — outside the {RETURN_WINDOW_DAYS}-day "
                "window. Not refundable, but the customer may request store credit "
                "via an escalation to the support team."
            ),
        }

    return {"eligible": False, "reason": f"Unrecognized order status: {status}."}