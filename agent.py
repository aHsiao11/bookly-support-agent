"""Bookly agent orchestrator.

The loop: user message → model → (tool requests → real functions →
results back to model, repeat) → final text reply.

The deterministic refund gate lives HERE (see run_tool): eligibility
is checked in code before issue_refund can execute. The model cannot
bypass it, no matter what the customer says.
"""

import json
import anthropic
from dotenv import load_dotenv

from tools import (
    lookup_customer,
    get_orders_for_customer,
    get_order_details,
    issue_refund,
)
from policies import search_policies
from rules import check_refund_eligibility
from data import ORDERS

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"  # one place to change, per our deprecation lesson

SYSTEM_PROMPT = """You are Bookly's customer support agent. Bookly is an online bookstore.

Core rules — these define how you operate:

1. GROUNDING: Never state facts about orders, accounts, or policies from
   your own knowledge. Every fact must come from a tool result. When you
   cite a policy, mention it ("Per our returns policy..."). If a tool
   returns found=False, say so honestly and offer a next step. Never guess.

2. IDENTITY FIRST: Before discussing any order or account details, verify
   the customer with lookup_customer using their email. Until verified,
   you may only answer general policy questions.

3. CLARIFY WITH OPTIONS, NEVER OPEN QUESTIONS: If a request is ambiguous
   (e.g. "where's my order?" and they have several), fetch their orders
   FIRST, then present the specific options. Never ask the customer to
   rephrase or repeat information they've already given.

4. CONFIRM BEFORE MONEY MOVES: Before calling issue_refund, state the
   exact item and refund amount and get an explicit yes from the customer.

5. FORWARD PROGRESS ALWAYS: Every reply either resolves something, asks a
   question that narrows the problem, or hands off with full context. If
   you can't help (policy says no, or topic is beyond you), acknowledge
   warmly, explain why with the cited reason, and offer the path forward
   (store credit request, human escalation). Never leave a dead end.

Tone: warm, concise, plain language. No corporate filler.
"""

# ---- Tool schemas: the menu the model sees --------------------------------

TOOLS = [
    {
        "name": "lookup_customer",
        "description": "Verify a customer account by email. Must be called before discussing any order/account details.",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string", "description": "Customer's email address"}},
            "required": ["email"],
        },
    },
    {
        "name": "get_orders_for_customer",
        "description": "List all orders for a verified customer's email. Use this BEFORE asking which order they mean.",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string"}},
            "required": ["email"],
        },
    },
    {
        "name": "get_order_details",
        "description": "Get full details for one order by its ID (e.g. BK-1001).",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "search_policies",
        "description": "Look up Bookly policy text (returns, shipping, account/password help). Answer policy questions ONLY from this.",
        "input_schema": {
            "type": "object",
            "properties": {"topic": {"type": "string", "description": "The customer's question or topic"}},
            "required": ["topic"],
        },
    },
    {
        "name": "check_refund_eligibility",
        "description": "Check whether an order is eligible for refund per Bookly's rules. Call this before ever discussing a specific refund.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "issue_refund",
        "description": "Execute a refund for an order. Only call AFTER eligibility was confirmed and the customer explicitly said yes to the stated amount.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
]

# ---- Tool execution: where code, not the model, is in charge --------------

def run_tool(name: str, tool_input: dict) -> dict:
    """Dispatch a model tool request to the real function.

    THE DETERMINISTIC GATE: issue_refund re-checks eligibility in code
    before executing. Even if the model skips the check or gets talked
    into a refund, the gate holds.
    """
    if name == "lookup_customer":
        return lookup_customer(tool_input["email"])

    if name == "get_orders_for_customer":
        return get_orders_for_customer(tool_input["email"])

    if name == "get_order_details":
        return get_order_details(tool_input["order_id"])

    if name == "search_policies":
        return search_policies(tool_input["topic"])

    if name == "check_refund_eligibility":
        order = ORDERS.get(tool_input["order_id"].strip().upper())
        if order is None:
            return {"eligible": False, "reason": f"No order with ID {tool_input['order_id']}."}
        return check_refund_eligibility(order)

    if name == "issue_refund":
        order = ORDERS.get(tool_input["order_id"].strip().upper())
        if order is None:
            return {"success": False, "error": f"No order with ID {tool_input['order_id']}."}
        gate = check_refund_eligibility(order)          # <-- the gate
        if not gate["eligible"]:
            return {"success": False, "blocked_by_policy": True, "reason": gate["reason"]}
        return issue_refund(tool_input["order_id"])

    return {"error": f"Unknown tool: {name}"}


# ---- The orchestration loop ------------------------------------------------

def get_agent_reply(conversation: list) -> str:
    """Send the conversation to the model; loop until it stops requesting tools."""
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation,
        )

        # No tool requests -> the text is the final answer
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # The model's turn (including its tool requests) joins the history
        conversation.append({"role": "assistant", "content": response.content})

        # Run every requested tool; send results back
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"   [tool] {block.name}({json.dumps(block.input)})")
                output = run_tool(block.name, block.input)
                print(f"   [tool] -> {json.dumps(output)}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output),
                })
        conversation.append({"role": "user", "content": results})