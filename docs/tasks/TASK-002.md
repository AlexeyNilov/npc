# TASK-002: Bilateral healing-herb purchase loop

**Status:** Ready

**Owner:** Unassigned

**Role guide:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `7d9460f`

**Depends on:** None

**Write scope:** `src/npc/trader_experiment.py`, `tests/test_trader_experiment.py`, `scenarios/trader_decision.yaml`, `README.md`, and this packet's handoff only.

**Parallel-safe with:** None; the task changes the trade model, checked-in scenario, public command output, and its tests.

**Durable information changed:**

- What must the system do? -> [Requirements: Trader decision experiment](../requirements.md#trader-decision-experiment)
- What is this project, and how do I use it? -> README trader-experiment usage instructions, if its command description changes.

**Simplifier review:** Required: the task changes the experiment's data model and public CLI output boundary.

## Outcome

A developer can run one checked-in, deterministic paired scenario in which the player sells exactly one healing herb to the trader. The trader accepts the four-gold proposal because it advances its stock goal within its price and reserve rules, and refuses the six-gold proposal. Each outcome visibly reports both party states, demonstrating an economically self-interested trade loop with conserved goods and funds.

## Canonical context

- [Roadmap: Demonstrate an economically self-interested trade loop](../roadmap.md#2-demonstrate-an-economically-self-interested-trade-loop)
- [Requirements: Trader decision experiment](../requirements.md#trader-decision-experiment)
- [Decision: Keep core actor decisions deterministic](../decisions.md#2026-07-25-keep-core-actor-decisions-deterministic)
- Existing module: `src/npc/trader_experiment.py`; test entry point: `tests/test_trader_experiment.py`; scenario: `scenarios/trader_decision.yaml`.

Read [AGENTS.md](../../AGENTS.md), this packet, the [Implementer guide](../agent_roles/implementer.md), and only the context named above. Do not read the task registry, sibling packets, completed tasks, or unrelated planning history.

## Task-specific scope

- Keep the supported trade class to a player selling exactly one healing herb to one trader. Do not add trader sales, multiple goods, multiple actors, persistence, chat integration, interactive input, or LLM behavior.
- Preserve the agreed deterministic trader policy: accept only below a target stock of three herbs, at a price at or below five gold, and only when the resulting trader gold is at least ten. Preserve the existing reason codes; the six-gold case is `price_above_limit`.
- Extend the proposal/state model and YAML scenario with explicit player state. The checked-in paired cases start independently with the player holding one herb and zero gold, and the trader state already defined in the scenario.
- On acceptance, transfer one herb from player to trader and the offered gold from trader to player. On refusal, return both original states unchanged.
- Make CLI output expose each proposal's outcome, reason, and resulting trader and player states. Update README only if its command description needs a factual correction.
- Do not add a dependency or alter the deterministic-authority boundary.

## Acceptance and verification

- Begin with failing behavioral tests proving the four-gold proposal transfers one herb and four gold across the parties, and that the six-gold proposal leaves both parties unchanged with `price_above_limit`.
- Test each paired scenario case starts from identical explicit trader and player states, isolating price as the changed interest.
- Test accepted trades conserve combined healing herbs and gold; retain a test proving repeated evaluation of identical input is deterministic.
- Test the CLI exposes both party states, the proposal decision, and its reason for both checked-in cases.
- Run focused tests, then `make check`, `git diff --check`, and the documented `python -m npc.trader_experiment` command. Record results in the handoff.

## Stop conditions

- A required change broadens the supported trade class, changes the agreed target/price/reserve policy, adds a dependency, or requires an LLM/network call for an authoritative decision.
- The scenario cannot unambiguously represent both initial party states and independent proposals, or acceptance cannot conserve both goods and funds.
- Existing user-owned changes overlap the write scope.
- A new durable behavior or consequential design choice lacks a canonical owner or user acceptance.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
