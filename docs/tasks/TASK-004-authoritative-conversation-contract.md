# TASK-004: Evidence-backed authoritative conversation contract

**Status:** Planned

**Owner:** Unassigned

**Role guide:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `d716c9b86cd56034a38b6c80d59b4e71165d454a`

**Depends on:** None

**Write scope:** `src/npc/trader_playtest.py`, `tests/test_trader_playtest.py`,
`README.md`, `docs/requirements.md`, `docs/architecture.md`, and
`docs/decisions.md`

**Parallel-safe with:** None; the task changes the sole conversation boundary
and its specification.

**Durable information changed:**

- What the system must do -> [Requirements](../requirements.md), Stateful
  conversational trader playtest.
- How the system works now -> [Architecture](../architecture.md), Conversational
  trader playtest.
- Why the LLM extraction boundary was chosen -> [Decisions](../decisions.md),
  new accepted decision.
- What this project is and how to use the supported offer -> [README](../../README.md),
  Conversational trader playtest.

**Simplifier review:** Required: this changes a public conversation boundary and
introduces structured evidence validation. Keep the schema and validator as
small as possible; do not add a general parser, dependency, or abstraction.

## Outcome

A player message reaches `evaluate_offer` only when an untrusted LLM extraction
describes the sole supported action—selling exactly one `healing herb` to the
trader for a positive decimal-integer number of `gold`—and cites verbatim
evidence in that message for direction, item, quantity, price, and currency.
All other messages remain non-transactional and leave authoritative state
unchanged. This preserves varied phrasing without allowing an LLM to create an
economic commitment.

## Canonical context

- [Roadmap: Outcome 4](../roadmap.md#4-establish-an-authoritative-conversation-contract).
- [Requirements: Stateful conversational trader playtest](../requirements.md#stateful-conversational-trader-playtest).
- [Decision: Deterministic actor decisions with LLM assistance](../decisions.md#2026-07-25-use-deterministic-actor-decisions-with-llm-assistance).
- [Architecture: Conversational trader playtest](../architecture.md#conversational-trader-playtest).
- Initial source entry point: `src/npc/trader_playtest.py` (`LocalTraderModel`,
  `TraderSession.handle_message`, and `offer_from_candidate`).
- Initial behavior tests: `tests/test_trader_playtest.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer role guide, and
only the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Dependency before implementation: define the deterministic vocabulary that
  makes each quoted evidence span prove offer direction and quantity one. Exact
  spans alone do not establish semantics; for example, an extractor could
  falsely label `a` as quantity `1` or `give` as a sale. The packet becomes
  Ready only after that vocabulary is accepted.
- Define one small, schema-aligned untrusted extraction shape for the existing
  model response. It represents only `sell_to_trader`, `healing_herb`, quantity
  `1`, and `unit_price_gold`, together with exact player-message evidence for
  offer direction, item, quantity, price, and currency.
- Implement a deterministic validator that accepts an extraction only when all
  schema values are supported by its evidence and the player message. Price
  evidence must be decimal digits matching a strictly positive `int`; reject
  zero, negatives, booleans, strings, omitted fields, malformed evidence, and
  evidence absent from or inconsistent with the message.
- Pass only the validated `Offer` to the existing `evaluate_offer`; do not
  modify that evaluator or expand the economy, item catalog, quantities,
  directions, currencies, persistence, or player actions.
- Preserve the terminal `TRADE_TRACE` for valid proposals. For rejected
  extraction, do not evaluate or emit a trade decision; retain sufficient
  conversation history for the next turn without treating the LLM candidate as
  authoritative.
- Make the model prompt/schema, README usage text, requirements, architecture,
  and decision record accurately distinguish untrusted extraction from
  authoritative validation. Do not claim model determinism.

## Acceptance and verification

- Write failing behavioral tests before changing application logic. With a
  scripted model, verify a direct offer with complete, matching evidence creates
  the expected `Offer`, reaches the evaluator, emits an accepted trace, and
  updates state.
- Verify each fixed negative case—question about buying, price without an offer,
  agreement after a prior refusal, zero price, negative price, and an LLM
  candidate with invented or mismatched evidence—does not reach the evaluator,
  emits no trade decision, and leaves both authoritative states unchanged.
- Verify the validator gives the same result for repeated calls with the same
  player message and extractor response. Verify a correctly shaped candidate
  cannot override the deterministic evaluator's refusal.
- Retain coverage for local-model JSON and terminal exit behavior, adapting
  fixtures to the new response shape.
- Update requirements in EARS form; describe current data flow in architecture;
  record the accepted evidence-gating decision and its rejected fixed-template
  alternative; give the README one supported explicit-offer example without
  promising that the LLM itself is deterministic.
- Run `make check` and `git diff --check`.

## Stop conditions

- A required economic fact cannot be represented with both an extraction field
  and verbatim evidence, or validation would require the LLM's unverified
  semantics to authorize state.
- The implementation would need a new action, item, quantity, currency,
  persistence mechanism, dependency, or a change to `evaluate_offer`.
- Conflicting requirements, an unaccepted contract choice, or unexpected
  user-owned changes within the write scope.
- Missing local dependencies or any external mutation not explicitly authorized.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
