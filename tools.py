"""Bookly agent tools.

These functions are the ONLY way the agent can read or change data.
Each returns a plain dict (JSON-able), including error cases.
Tools never raise exceptions at the model, they return honest
"not found" results so the agent can respond truthfully.
"""

from data import CUSTOMERS, ORDERS


def lookup_customer(email: str) -> dict:
    """Verify a customer exists. The agent's identity gate."""
    email = email.strip().lower()
    customer = CUSTOMERS.get(email)
    if customer is None:
        return {"found": False, "error": "No account found for that email."}
    return {"found": True, "name": customer["name"], "email": customer["email"]}


def get_orders_for_customer(email: str) -> dict:
    """All orders for a verified customer. Powers option-based clarification."""
    email = email.strip().lower()
    orders = [o for o in ORDERS.values() if o["customer_email"] == email]
    if not orders:
        return {"found": False, "error": "No orders found for that account."}
    return {"found": True, "count": len(orders), "orders": orders}


def get_order_details(order_id: str) -> dict:
    """Full detail on one specific order."""
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {"found": False, "error": f"No order with ID {order_id}."}
    return {"found": True, "order": order}


def issue_refund(order_id: str) -> dict:
    """Execute a refund. NOTE: eligibility is NOT checked here —
    the rules layer decides; this tool only executes."""
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {"success": False, "error": f"No order with ID {order_id}."}
    if order["status"] == "refunded":
        return {"success": False, "error": "This order was already refunded."}
    order["status"] = "refunded"
    return {
        "success": True,
        "order_id": order["order_id"],
        "amount": order["price"],
        "message": f"Refund of ${order['price']} issued. Funds arrive in 5-7 business days.",
    }