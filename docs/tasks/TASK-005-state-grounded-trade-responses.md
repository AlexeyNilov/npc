# TASK-005: State-grounded player-facing trade responses

**Status:** Ready

**Owner:** Unassigned

**Role guide:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `7114927e03a2ec5f96ab5ac55d057d7a6ed1e313`

**Depends on:** None

**Write scope:** `src/npc/trader_playtest.py`, `tests/test_trader_playtest.py`, `README.md`, `docs/requirements.md`, `docs/architecture.md`, and `docs/decisions.md`

**Parallel-safe with:** None; the task replaces the player-visible response boundary and its specification.

**Durable information changed:**

- What the system must do -> [Requirements](../requirements.md), Stateful conversational trader playtest.
- How the system works now -> [Architecture](../architecture.md), Conversational trader playtest.
- Why authoritative response composition was chosen -> [Decisions](../decisions.md), new accepted decision.
- What this project is and how to use the playtest -> [README](../../README.md), Conversational trader playtest.

**Simplifier review:** Required: this changes the public conversation boundary and model-response schema. Keep one small response composer and closed vocabularies; do not add a second LLM call, free-text checker, dependency, or general dialogue system.

## Outcome

Every terminal reply accurately reflects the authoritative transaction result and state. The LLM may select only approved non-economic flavor; it cannot write player-visible prose or assert a completed trade, transfer, balance, or other state change. This retains a minimal social tone while making the trader's economic behaviour trustworthy in play.

## Canonical context

- [Roadmap: Outcome 5](../roadmap.md#5-make-player-facing-trade-outcomes-state-grounded).
- [Requirements: Stateful conversational trader playtest](../requirements.md#stateful-conversational-trader-playtest).
- [Decision: Keep core actor decisions deterministic](../decisions.md#2026-07-25-keep-core-actor-decisions-deterministic).
- [Decision: Gate trade extraction with verbatim player-message evidence](../decisions.md#2026-07-25-gate-trade-extraction-with-verbatim-player-message-evidence).
- [Architecture: Conversational trader playtest](../architecture.md#conversational-trader-playtest).
- Initial source entry point: `src/npc/trader_playtest.py` (`ModelReply`, `LocalTraderModel`, and `TraderSession.handle_message`).
- Initial behavior tests: `tests/test_trader_playtest.py`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer role guide, and only the context named above. Do not read the task registry, sibling packets, completed tasks, or unrelated planning history.

## Task-specific scope

- Replace the model's open `narration` field with an untrusted, closed `flavor` value: `warm`, `neutral`, `attentive`, or `wary`. Unknown, malformed, or omitted flavor falls back deterministically to `neutral`. The LLM remains responsible for the existing untrusted trade extraction only.
- Render all player-visible text in one deterministic response composer. Flavor maps to a fixed, non-economic atmospheric clause; it may not name an item, price, balance, transfer, acceptance, refusal, promise, or completed action.
- Derive the remainder of the reply only from validation and evaluator results:
  - no extraction: render only the safe atmospheric clause;
  - malformed or evidence-rejected extraction: say that no supported trade was completed, without claiming a transfer or acceptance;
  - validated refusal: state that the trader refused the specified offer and use the evaluator's actual refusal reason;
  - validated acceptance: state the exact accepted `healing herb` purchase and positive gold price from the evaluated `Offer` and result.
- Keep state mutation exclusively in `evaluate_offer`. Keep `TRADE_TRACE` for evaluated offers; do not emit it for no extraction or rejected extraction. Store the rendered authoritative reply, not model-authored prose, in turn history.
- Do not widen the economy, validation grammar, actor memory, persistence, social decision model, or the LLM's authority. In particular, do not add an LLM grounding-check/retry loop.
- Update the model prompt/schema, README, EARS requirements, architecture, and a decision record to distinguish allowed atmospheric flavor from authoritative response facts.

## Acceptance and verification

- Write failing behavioral tests before changing application logic.
- Test the reported sequence: `I want to sell some stuff`, `herbs`, a `magic healing herb`, `I can sell it to you for 10 golds`, `Its a deal then?`, and `here you go` produce no trade trace, no state change, and no player-visible claim that a herb or gold was transferred.
- With scripted model replies, test each response path: no extraction, malformed/unsupported extraction, evidence-rejected extraction, deterministic `price_above_limit` refusal, and acceptance. Assert exact authoritative response facts and that result states and trace agree.
- Test unknown/malformed flavor falls back to neutral, and model-provided free-text narration is absent from player-visible output and history.
- Retain valid extraction, local-model JSON, terminal exit, and determinism coverage; adapt fixtures to the revised model schema.
- Update all named durable owners, then run `make check` and `git diff --check`.

## Stop conditions

- A player-visible economic assertion cannot be sourced solely from the validated offer and evaluator result.
- The design would need free model-authored prose, a second LLM call, semantic claim detection, a new actor action, new state, or a change to the economic evaluator.
- Conflicting requirements, an unaccepted response vocabulary, or unexpected user-owned changes within the write scope.
- Missing dependencies or any external mutation not explicitly authorized.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
