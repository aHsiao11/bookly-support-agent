"""Bookly policy knowledge base.

Policy TEXT the agent retrieves and cites when answering general
questions. In production this would be a vector-searched help center;
for the prototype, a keyword-matched dict proves the same pattern:
the agent answers policy questions FROM retrieved text, never from
the model's own knowledge.
"""

POLICIES = {
    "returns": (
        "Returns & Refunds Policy: Items may be returned within 30 days "
        "of delivery for a full refund to the original payment method. "
        "Books must be in resalable condition. Refunds process in 5-7 "
        "business days. Orders outside the 30-day window are not "
        "eligible for refund, but may qualify for store credit at "
        "Bookly's discretion via our support team."
    ),
    "shipping": (
        "Shipping Policy: Standard shipping (free over $25) takes 3-5 "
        "business days. Expedited shipping (2 days) is $9.99. Orders "
        "ship within 1 business day. Tracking numbers are emailed at "
        "ship time."
    ),
    "password": (
        "Account Help: To reset your password, use the 'Forgot Password' "
        "link on the sign-in page. A reset email arrives within a few "
        "minutes; check spam if not. Support agents can never see or "
        "set passwords directly."
    ),
}


def search_policies(topic: str) -> dict:
    """Keyword-match a policy. Honest miss if nothing matches."""
    topic_lower = topic.lower()
    keyword_map = {
        "returns": ["return", "refund", "money back", "exchange"],
        "shipping": ["ship", "delivery", "tracking", "arrive", "expedite", "package", "where is my"],
        "password": ["password", "login", "sign in", "account", "reset"],
    }
    for policy_key, keywords in keyword_map.items():
        if any(kw in topic_lower for kw in keywords):
            return {"found": True, "topic": policy_key, "policy_text": POLICIES[policy_key]}
    return {"found": False, "error": "No policy found on that topic. Offer to connect the customer with the support team."}