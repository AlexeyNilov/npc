# TASK-001: Inspectable intent-shaped trader offer sequence

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `7d18831b13e5a5dbfa6dd75703ac8b7c206c6a53`

**Depends on:** None

**Write scope:** `actors/`, `scenarios/`, `src/npc/`, `tests/`,
`docs/evidence/`, `docs/requirements.md`, `docs/architecture.md`

**Parallel-safe with:** None — the proof changes the CLI execution path and
its canonical state model.

**Durable information changed:** observable behavior ->
[Requirements](../requirements.md), verified mechanism ->
[Architecture](../architecture.md), bounded result ->
`docs/evidence/2026-08-02-intent-shaped-trader-offers.md`. The roadmap stays
unchanged until Technical-Lead acceptance.

**Simplifier review:** Required: the work adds a distinct stateful proof path
and experiment entry point.

## Outcome

Implement the roadmap's first milestone as one runnable YAML fixture that
runs the same ordered offers independently for `greedy` and `cautious`
traders. For each offer, the run must show the binary LLM decision question
and validated answer, the resulting accept-or-do-nothing proposal, and the
engine's transaction outcome. This establishes the intended authority boundary
over more than one decision and more than one canonical transaction state.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| trader intent | [Roadmap §1](../roadmap.md#1-intent-shaped-trader-decisions-over-a-sequence-of-offers); [Glossary: Intent](../glossary.md#actor-loop-terms) | YAML-declared `greedy` or `cautious` context is supplied verbatim to the binary decision request; it does not itself mutate state or determine acceptance. | Actor decision path proposes only. | Static per trader run. | Not new; accepted roadmap input. |
| offer | [Roadmap §1](../roadmap.md#1-intent-shaped-trader-decisions-over-a-sequence-of-offers) | Ordered YAML record: descriptive text plus buy/sell, item, quantity, and price. | Scenario supplies it; engine interprets the transaction facts. | Read in declared order; not mutated. | Accepted roadmap input. |
| cash and inventory | [Roadmap §1](../roadmap.md#1-intent-shaped-trader-decisions-over-a-sequence-of-offers) | Integer cash and per-item integer quantities used in a transaction precondition and transition. | Engine resolver exclusively. | Initialized for each trader; updated only by accepted transactions. | Accepted roadmap state. |
| transaction proposal and outcome | [Roadmap §1](../roadmap.md#1-intent-shaped-trader-decisions-over-a-sequence-of-offers); [Glossary: Action proposal](../glossary.md#actor-loop-terms) | A validated `true` proposes accepting the current offer; `false` proposes no transaction. Resolver accepts or rejects only the former from current cash/inventory. | Actor proposes; engine resolves and mutates. | One per trader/offer decision; outcome is presentation input after resolution. | Accepted roadmap behavior. |

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| intent | Existing [Intent](../glossary.md#actor-loop-terms) entry | It crosses YAML, LLM input, observer trace, and resolver authority boundaries. |
| offer, trader, cash, inventory, transaction | Packet-local, disposable proof vocabulary | The roadmap authorizes their behavior only for this bounded proof; do not add glossary entries unless acceptance establishes a project-wide meaning. |

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-08-02-intent-shaped-trader-offers.md`.
- **Hypothesis and decision unlocked:** an LLM-mediated, intent-shaped binary
  assessment can drive repeated actor proposals while an authoritative resolver
  retains sole control of transaction state.
- **Result handoff:** at Review, complete the record and mark it `Review`; the
  Technical Lead finalizes it after Simplifier review and roadmap closure.

## Canonical context

- [Roadmap §1](../roadmap.md#1-intent-shaped-trader-decisions-over-a-sequence-of-offers).
- [Requirements: LLM-backed perception](../requirements.md#llm-backed-perception)
  and [Observer inspection and narration](../requirements.md#observer-inspection-and-narration),
  as the existing boundary to preserve and extend after verification.
- [Architecture: Runtime shape](../architecture.md#runtime-shape),
  [Canonical runtime model](../architecture.md#canonical-runtime-model), and
  [Turn processing and authority](../architecture.md#turn-processing-and-authority).
- Entry points: `src/npc/__main__.py`, `src/npc/simulation.py`, and
  `tests/test_yaml_beast_proof.py`.

## Task-specific scope

- Add a trader-offer YAML fixture, including two trader definitions with the
  same initial cash and inventory, distinct declared intents, and one shared
  ordered offer list. The fixture must include both a buy and a sell offer and
  be long enough to prove that the next LLM request receives state changed by
  an accepted preceding transaction.
- Add the smallest trader execution path. For each trader and each offer, send
  one non-streaming LLM request containing the common binary question, “Does
  accepting this offer fit your intent in your current situation?”, the offer
  description and authoritative transaction facts, the trader's current cash
  and inventory, and the trader's intent. Parse only a boolean answer (with
  the existing standalone `json` fence allowance if using the established
  parser).
  A malformed, missing, or non-boolean response must fail before that offer's
  proposal or resolution.
- On `true`, construct only an accept-current-offer proposal. On `false`, emit
  a no-action outcome without a transaction. The resolver alone checks that a
  buy has cash at least equal to its price or that a sell has at least the
  offered quantity; an accepted buy subtracts price and adds quantity, while
  an accepted sell adds price and subtracts quantity. Rejection leaves both
  cash and inventory unchanged.
- Render a stable per-offer observer record that makes the decision question,
  answer, attempted choice, and authoritative result distinguishable. Add an
  independent experiment entry point, for example
  `python -m npc.experiments.trader_offers <scenario>`. Do not alter
  `python -m npc <scenario>` or dispatch from it: it remains the completed
  beast-proof runner. The trader entry point and YAML shape are disposable
  experiment scaffolding, not a published scenario schema or a general CLI
  mode system.
- Write behavioral tests before changing implementation logic. Capture the
  LLM requests to prove intent, current state, both parts of the offer, and no
  resolver/action-control data beyond the current offer are supplied. Test:
  two independent identical initial states; both offer directions; accepted
  and rejected transactions; false/no-action; per-offer ordering and state
  feedback; invalid response fail-fast; and observer trace distinction. Use
  deterministic doubles; run a real LLM only as evidence when the configured
  endpoint is available.
- At Review, add the evidence record. Update Requirements and Architecture
  only with verified behavior and mechanism. Do not modify the roadmap until
  Technical-Lead acceptance.

**Explicit exclusions:** market pricing, matching, negotiation, counterparties,
other traders, persistence or replay, a general trading schema, any claim that
the two intents reliably produce different answers, and changes to existing
beast-proof semantics.

## Acceptance and verification

- The new fixture completes an ordered offer sequence for both traders through
  the configured real LLM; its observer output contains a separate record for
  every trader/offer decision. The captured-test path proves the exact LLM
  decision inputs include intent and updated authoritative state.
- Tests prove only the engine mutates cash and inventory, including rejection
  for insufficient cash or inventory; a false answer changes neither.
- A malformed, incomplete, or non-boolean decision response raises a
  diagnostic failure before proposal/resolution for that offer.
- Existing beast tests and its CLI behavior continue to pass unchanged. Add
  focused trader tests first, then run `.venv/bin/python -m pytest -q`,
  `make check`, and `git diff --check`.
- Run the trader fixture against the configured endpoint and record the exact
  command plus a bounded trace in the evidence record. If the endpoint is not
  available, retain deterministic evidence and move the task to `Blocked` only
  if live execution is required to claim acceptance.

## Stop conditions

- The roadmap's accepted facts cannot determine a transaction precondition,
  state transition, or scenario form without inventing a market or domain rule.
- A correct proof requires the LLM to supply transaction facts, mutate state,
  decide resolution, or receive another trader's state.
- The trader proof requires changing the beast CLI, folding the two proof state
  models into one abstraction, or a proposed reusable boundary lacks the
  stated second-use evidence.
- Required live LLM access is unavailable, or unrelated user changes overlap
  this packet's write scope.

## Handoff

**Status and outcome:** Ready; implementation has not begun.

**Changed files and ownership impact:** This planning packet and task registry
only. No product behavior or canonical design fact changed.

**Verification:** Planning context inspected; working tree was clean before
these planning edits.

**Assumptions, risks, and next action:** The milestone authorizes the stated
cash/inventory transitions but not a reusable commerce model. Assign one
Implementer to this packet, then route its Review diff to a Simplifier before
Technical-Lead acceptance.
