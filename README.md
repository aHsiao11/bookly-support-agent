# Bookly Support Agent

A prototype customer-support agent for Bookly, a fictional online
bookstore. Built for the Decagon SE take-home.

**Thesis: a great support agent never takes the customer backward.**
Every turn makes verifiable forward progress — grounded answers with
cited sources, clarification as concrete options rather than open
questions, and refusals that always include a path forward. The model
understands and communicates; tools and code decide and act.

## Architecture

customer → main.py (chat loop) → agent.py (orchestration + gate)
→ tools.py (the only access to data) → data.py (mock world)

agent.py also consults:
- policies.py — retrieved policy text the agent cites (what it SAYS)
- rules.py — deterministic eligibility logic (what it MAY DO)

Three design rules operationalize the thesis:

1. **No unsourced claims.** The model never answers order or policy
   questions from its own knowledge — every fact comes from a tool
   result, and misses are reported honestly instead of guessed.
2. **Clarification must collapse the solution space.** When a request
   is ambiguous, the agent fetches data first and offers specific
   options — never "please rephrase."
3. **The model proposes, code disposes.** Refund eligibility is
   enforced in rules.py and re-checked inside run_tool before
   issue_refund can execute. Irreversible actions also require an
   explicit customer confirmation. The conversation cannot reach
   around the gate.

## Run it

1. Python 3.9+
2. `python3 -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Create `.env` in the project root: `ANTHROPIC_API_KEY=sk-ant-...`
5. `python3 main.py`

### Try the demo script

- "where's my order?" → agent asks for your email (identity first)
- `sarah@example.com` → verified; agent presents her three orders as
  options
- Pick the Red Rising paperback → delivered status
- "I'd like to return it" → eligibility check, confirmation of the
  exact amount, then the refund
- Or verify as `mike@example.com` and request a refund on his order
  (delivered 44 days ago) — then push back and watch the policy gate
  hold while the agent offers store credit.

## Deliberate scoping choices

- **Mock data, frozen clock** (`TODAY = 2026-10-15` in rules.py):
  demo outcomes are reproducible on any machine, any day. Production
  swaps one line to `date.today()`.
- **Keyword policy retrieval**: stands in for semantic search. The
  retrieval contract — question in, official text or an honest miss
  out — is the real pattern; only the matcher is mocked.
- **In-memory state**: session-scoped conversation memory; restarts
  reset the world by design. Production persists transcripts and
  order state.

## What I'd do first in production

Evaluation & observability: log every tool call and cited source,
score transcripts for true resolution vs. silent failure, and
regression-test prompt changes against a conversation library before
shipping.