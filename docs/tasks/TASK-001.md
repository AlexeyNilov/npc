# TASK-001: Reproducible trader decision experiment

**Status:** Ready

**Owner:** Unassigned

**Role guide:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `5941592`

**Depends on:** None

**Write scope:** `pyproject.toml`, `src/npc/`, `tests/`, `scenarios/`,
`README.md`, and this packet's handoff only.

**Parallel-safe with:** None; the task changes the project manifest, public
command documentation, core package, and tests.

**Durable information changed:**

- What must the system do? ->
  [Requirements: Trader decision experiment](../requirements.md#trader-decision-experiment)
- Why was a consequential choice made? ->
  [Decisions: Use YAML scenarios for the initial trader experiment](../decisions.md#2026-07-25-use-yaml-scenarios-for-the-initial-trader-experiment)
- What is this project, and how do I use it? -> README usage instructions for
  the implemented command.

**Simplifier review:** Required: the task adds a runtime dependency, CLI
boundary, scenario format, and core decision module.

## Outcome

A developer can run one checked-in YAML scenario that evaluates two player
offers independently from the same trader state, then inspect each proposal,
the deterministic decision and reason code, and the resulting state. This
tests the project’s decision determinism boundary before chat or LLM work is
introduced.

## Canonical context

- [Roadmap: Outcome 1](../roadmap.md#1-establish-a-reproducible-trader-decision-experiment)
- [Requirements: Trader decision experiment](../requirements.md#trader-decision-experiment)
- [Decision: deterministic actor decisions](../decisions.md#2026-07-25-keep-core-actor-decisions-deterministic)
- [Decision: YAML scenarios](../decisions.md#2026-07-25-use-yaml-scenarios-for-the-initial-trader-experiment)
- Current package root: `src/npc/`; test entry point: `tests/`; project command
  configuration: `pyproject.toml`.

Read [AGENTS.md](../../AGENTS.md), this packet, the
[Implementer guide](../agent_roles/implementer.md), and only the context named
above. Do not read the task registry, sibling packets, completed tasks, or
unrelated planning history.

## Task-specific scope

- Add PyYAML as the single runtime dependency and bump the patch version.
- Add a checked-in YAML scenario containing one initial trader: zero healing
  herbs, 30 gold, target stock of three herbs, a maximum unit price of five
  gold, and a ten-gold reserve.
- The scenario defines exactly two independent one-herb purchase proposals:
  four gold and six gold. Each begins from a fresh copy of the initial state.
- Implement pure deterministic decision and state-transition logic, isolated
  from YAML loading and terminal output. An accepted four-gold offer yields one
  herb and 26 gold. The six-gold offer is refused with `price_above_limit` and
  leaves the initial state unchanged.
- Add a Python module CLI runnable with `python -m ...` that loads the
  checked-in scenario and prints one readable result per proposal, including
  its decision reason and resulting state. It must make no network or LLM call.
- Document the exact command and its purpose in the README.
- Do not add interactive input, multiple traders, general market mechanics,
  player persistence, chat integration, or LLM-assisted behavior. Do not make
  malformed YAML handling more elaborate than necessary for the checked-in
  scenario.

## Acceptance and verification

- Begin with failing behavioral tests for the core policy and the CLI-visible
  experiment result.
- Tests prove that the four-gold offer is accepted with the specified state
  transition; the six-gold offer is refused with `price_above_limit` and no
  transition; and independently evaluating the same inputs repeatedly returns
  identical results.
- A test proves the two checked-in scenario cases each start from identical
  initial state, isolating offered price as the changed input.
- A CLI test proves the command exposes both proposals, their decisions/reason
  codes, and resulting states without needing an LLM or network access.
- Run focused tests, then `make check` and `git diff --check`. Manually run the
  documented command once and record its exact result in the handoff.

## Stop conditions

- A required change would alter an accepted rule, add another dependency, or
  expand into a stateful multi-proposal trade loop.
- The scenario or proposed output cannot represent the specified initial state,
  independent cases, decision reasons, and resulting state unambiguously.
- Existing user-owned changes overlap the write scope.
- Any command needs external access or an LLM to make an authoritative
  decision.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
