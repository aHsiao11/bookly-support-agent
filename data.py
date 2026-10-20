"""Mock Bookly database / dummy data.

In production this would be a real database or an API into the
order management system. For this example, hardcoded data keeps
the focus on agent architecture. Dates are chosen so the demo
scenarios work (one order inside the 30-day return window, one outside).
"""

CUSTOMERS = {
    "sarah@example.com": {
        "name": "Sarah Chen",
        "email": "sarah@example.com",
    },
    "mike@example.com": {
        "name": "Mike Rivera",
        "email": "mike@example.com",
    },
}

ORDERS = {
    "BK-1001": {
        "order_id": "BK-1001",
        "customer_email": "sarah@example.com",
        "item": "Red Rising by Pierce Brown (paperback)",
        "price": 17.99,
        "status": "delivered",
        "delivered_date": "2026-10-08",   # ~1 week ago: INSIDE return window
        "shipping_address": "Portland, OR",
    },
    "BK-1002": {
        "order_id": "BK-1002",
        "customer_email": "sarah@example.com",
        "item": "Kitchen Confidential by Anthony Bourdain",
        "price": 29.99,
        "status": "shipped",
        "tracking_number": "1Z999AA10123456784",
        "estimated_delivery": "2026-10-18",
        "shipping_address": "Portland, OR",
    },
    "BK-1003": {
        "order_id": "BK-1003",
        "customer_email": "sarah@example.com",
        "item": "Mistborn: The Final Empire by Brandon Sanderson (gift wrapped)",
        "price": 19.99,
        "status": "processing",
        "shipping_address": "Denver, CO",
    },
    "BK-0947": {
        "order_id": "BK-0947",
        "customer_email": "mike@example.com",
        "item": "Project Hail Mary by Andy Weir (hardcover)",
        "price": 28.99,
        "status": "delivered",
        "delivered_date": "2026-09-01",   # ~6 weeks ago: OUTSIDE return window
        "shipping_address": "Seattle, WA",
    },
}