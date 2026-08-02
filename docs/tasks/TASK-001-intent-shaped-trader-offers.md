# TASK-001: Inspect intent-shaped trader decisions over ordered offers

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `d0d6244b9e27fe3919aa807e6836feb2b80a56a5`

**Depends on:** None

**Write scope:** `src/npc/experiments/trader_offers.py`,
`actors/trader_greedy.yaml`, `actors/trader_cautious.yaml`,
`scenarios/trader_offers.yaml`, `tests/test_trader_offers.py`,
`docs/evidence/2026-08-02-intent-shaped-trader-offers.md`, and this packet

**Parallel-safe with:** None; the packet introduces a complete executable slice
and its evidence handoff.

**Durable information changed:** Experiment result ->
`docs/evidence/2026-08-02-intent-shaped-trader-offers.md`. Current verified
mechanism -> `docs/architecture.md` only during Technical Lead completion
reconciliation. No requirement change is authorized by this bounded proof.

**Simplifier review:** Required because the work adds an executable module,
scenario contract, and domain state types.

## Outcome

Running one YAML-defined sequence through two independently stateful traders
shows, for every trader and offer, the intent-bearing LLM question and validated
answer, attempted choice, authoritative transaction result, and resulting cash
and inventory. This is the smallest vertical proof that intent can shape a
proposal while the engine retains transaction authority.

## Concept provenance

| Concept | Source | Accepted transformation or meaning | Authority | Lifecycle | Decision if new |
| --- | --- | --- | --- | --- | --- |
| Trader intent | Roadmap outcome 1 and Glossary `Intent` | Immutable plain-language context supplied to the binary decision request; it does not resolve a transaction | Trader actor profile YAML | Entire trader run | Existing accepted milestone meaning |
| Offer side | Roadmap outcome 1 | `buy` means the trader buys the item; `sell` means the trader sells it | Ordered scenario offer | One offer evaluation | User-confirmed 2026-08-02 |
| Offer price | Roadmap outcome 1 | Total cash consideration for the complete offered quantity, not a per-unit price | Ordered scenario offer | One offer evaluation | User-confirmed 2026-08-02 |
| Cash and inventory | Roadmap outcome 1 | Canonical per-trader balances; inventory maps item names to integer quantities | Experiment resolver | Initialized once, changed only by accepted transactions, retained through the sequence | Fixture-local representation of accepted milestone state |
| Actor-owned question and binary answer | Roadmap outcome 1, Requirements `Enduring authoring boundaries` and `Language-mediated actor decisions`, and Glossary `Actor-owned question` | Each trader profile declares the same question; its validated answer proposes the offered transaction when `true` and doing nothing when `false` | Actor profile owns the question; LLM proposes the answer; experiment boundary validates | Question persists with the profile; answer is ephemeral for one trader-offer decision | Existing milestone and actor-profile contracts |
| Transaction proposal | Roadmap outcome 1 and Glossary `Action proposal` | A bounded request to accept the current offer; it cannot mutate balances | Trader decision boundary | Created only for a validated `true`; consumed by one resolution | Existing accepted authority boundary |
| Transaction result | Roadmap outcome 1 | Accepted buy/sell mutates balances; insufficient cash or item quantity rejects without mutation; no proposal also leaves state unchanged | Experiment resolver | One offer evaluation; presented with the resulting state | Minimum authoritative semantics implied by cash, inventory, buy, and sell |

The fixture uses non-negative integer cash, prices, and inventory quantities and
strictly positive offer quantities. These are disposable experiment input
constraints, not a proposed public schema. General validation is out of scope.

## Terminology

| Term | Glossary entry or packet-local classification | Reason / affected boundary |
| --- | --- | --- |
| Intent | Glossary `Intent` | Reused across YAML, LLM input, trace, and evidence |
| Actor-owned question | Glossary `Actor-owned question` | Reused across actor YAML, the LLM boundary, trace, and evidence |
| Action proposal | Glossary `Action proposal` | Preserves the actor/engine authority boundary |
| Trader, offer, transaction result | Packet-local experiment terms | No reusable trading or market boundary is claimed |

## Experiment evidence

- **Evidence record:**
  `docs/evidence/2026-08-02-intent-shaped-trader-offers.md`.
- **Hypothesis and decision unlocked:** A real LLM can answer the same binary
  question for an ordered offer sequence with each trader's intent and current
  state in its input, while only deterministic resolution changes balances.
  The result determines whether this intent-to-proposal boundary is sufficient
  for a later outcome or must be revised before adding broader actor behavior.
- **Result handoff:** At Review, record the exact real-LLM command and observed
  trace, automated verification, interpretation, and limitations; set the
  evidence status to `Review` even if the result is negative or inconclusive.

## Vision alignment

- **Vision behavior made observable:** An actor's plain-language intent and
  current situation mediate a bounded decision, while authoritative state and
  transaction resolution remain outside the LLM.
- **Classification:** `Disposable experiment scaffolding`
- **Reuse pressure:** Not in scope — scaffolding only.
- **Boundary rejection signal:** The experiment cannot expose intent in the
  request, distinguish proposal from resolution, retain authoritative state
  across offers, or run both traders without trader-specific engine branches.

## Canonical context

- [README `Simulation loop`](../../README.md#simulation-loop) and `The intended
  actor loop is`.
- [Decisions `Use Natural Language as the Default Interface Between Actors and
  the World`](../decisions.md#2026-07-26-use-natural-language-as-the-default-interface-between-actors-and-the-world).
- [Roadmap outcome 1](../roadmap.md#1-intent-shaped-trader-decisions-over-a-sequence-of-offers).
- [Requirements `Enduring authoring boundaries` and `Language-mediated actor
  decisions`](../requirements.md), including separate YAML actor profiles and
  actor-owned binary questions.
- [Architecture `Runtime shape`, `Turn processing and authority`, and
  `Deliberate absences`](../architecture.md); these constrain reuse claims but
  do not define the target trader design.
- Initial source entry point:
  `src/npc/infrastructure/language_model.py::complete_text`.
- Do not broaden Requirements with experiment-specific trader behavior; obey
  its existing actor/scenario authoring and actor-owned-question boundaries.

Read [AGENTS.md](../../AGENTS.md), this packet, the
[Implementer guide](../agent_roles/implementer.md), and only the context named
above. Do not read the task registry, sibling packets, completed tasks, or
unrelated planning history.

## Task-specific scope

- Add `npc.experiments.trader_offers` as a directly executable, isolated
  experiment. Reuse `complete_text`; do not retrofit trading into
  `npc.simulation` or extract a shared abstraction from the existing
  experiment code.
- Add separate `greedy` and `cautious` actor-profile YAML files. Each profile
  owns the trader identifier, its distinct plain-language intent, and the same
  exact binary decision question. These files are experiment-local profiles,
  not a new reusable actor schema.
- Load one scenario containing references to exactly those two actor profiles,
  one shared starting cash and inventory declaration, and one ordered offer
  list. Both traders receive independent copies of the same starting balances
  and offers.
- Keep independent mutable canonical balances for each trader. Process every
  offer in YAML order for one trader without allowing the other trader's state
  or answers into its request.
- For each trader-offer pair, make one non-streaming completion request. Include
  the trader's intent, current cash and inventory, the offer description and
  authoritative side/item/quantity/total price, and the exact question: `Does
  accepting this offer fit your intent in your current situation?`
- Require a JSON object containing exactly that question as its sole key and a
  JSON boolean as its value. A standalone `json` Markdown fence may be accepted
  consistently with the existing proof. A request or validation failure exits
  non-zero before proposing or resolving that trader-offer pair and prints a
  diagnostic to stderr.
- A validated `true` creates a proposal for the current offer. A validated
  `false` records `do nothing` and does not call transaction resolution.
- Resolve proposed buys by requiring sufficient cash, then subtracting the
  offer's total price and adding its quantity. Resolve proposed sells by
  requiring sufficient item quantity, then removing that quantity and adding
  the offer's total price. A rejection changes neither cash nor inventory.
- Print a deterministic block for every trader-offer pair containing trader,
  intent, offer facts, question and answer, attempted choice, authoritative
  result (`accepted`, `rejected`, or `no transaction proposed`), and resulting
  cash and inventory. Do not add generative narration.
- Keep all experiment mechanics in the one experiment module unless separating
  code is required by a concrete test failure. Do not add dependencies, a
  market model, negotiation, other traders, prompt-effectiveness scoring,
  persistence, a public schema, or a reusable action/transaction framework.

## Acceptance and verification

- First add a failing behavioral test that runs a scripted answer sequence and
  proves later LLM requests receive state produced by earlier accepted offers.
- A request-capture test proves every request includes only the current trader's
  intent and state, the complete current offer, and the one exact binary
  question; it excludes the other trader and future offers.
- A YAML-authoring test proves changing one actor profile's intent or question
  changes that trader's request without an engine-code or scenario-content
  change, while changing scenario offers requires no actor-profile or
  engine-code change.
- Strict-response tests prove malformed JSON, wrong keys, and non-boolean
  values fail before proposal or balance mutation.
- Resolution tests cover accepted buy, rejected buy for insufficient cash,
  accepted sell, rejected sell for insufficient inventory, and validated
  `false`; every rejected or unproposed transaction leaves balances unchanged.
- A YAML/CLI test proves the fixture runs the same ordered offers for `greedy`
  and `cautious`, starts them from equal balances, keeps their state independent,
  and emits every required trace boundary. Mock only the external completion
  call in automated tests.
- Run one real-LLM smoke execution and preserve its inspectable output in the
  evidence result without claiming that intents caused different answers:
  `.venv/bin/python -m npc.experiments.trader_offers scenarios/trader_offers.yaml`.
- Run `.venv/bin/pytest tests/test_trader_offers.py`, then `make check`, then
  `git diff --check`.

## Stop conditions

- Stop if implementation would require changing the meaning of buy, sell,
  total price, intent, proposal authority, or canonical balances.
- Stop if actor-specific intent or the actor-owned question must be embedded in
  the scenario or Python implementation rather than its actor profile.
- Stop if correct behavior requires integrating with or refactoring the
  existing experiment simulation rather than keeping this proof isolated.
- Stop if the scenario needs a general schema, market participant, matching,
  negotiation, or another capability excluded by the roadmap.
- Stop on conflicting canonical evidence, required scope expansion,
  unexpected user-owned changes in write scope, unavailable real-LLM access,
  or an unapproved external mutation or dependency.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
