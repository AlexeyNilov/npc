# Experiment: deterministic fox safety-versus-food utility

**Status:** Complete

**Date:** 2026-07-26

**Roadmap outcome:** Completed; see the current roadmap.

## Decision unlocked

Whether the next capability-path step should assess recurrence of a
fox-local, authoritative persistent-need and deterministic-utility boundary,
or retain the current fixed threat-first policy and seek a different
contrasting decision. A supported result starts the recurrence assessment; a
rejected result rules out promoting a need/utility policy from this experiment.

## Hypothesis

Given the existing independently validated threat and explicit-food-offer
perceptions, an authoritative persistent hunger value and fixed utility scores
can produce a replayable, explainable safety-versus-food choice without giving
the LLM authority over state, scores, selection, reachability, or execution.

Assumptions: `hunger` is a fox-local integer where `0` means no food-seeking
pressure and `100` means maximum pressure; the proposed score magnitudes below
are experiment parameters, not a general utility model; and each completed
turn represents one fixed time step.

## Observable behavior

A developer can run a checked-in corpus and inspect each turn's authoritative
starting hunger, accepted/rejected perceptions, candidate-action utilities,
deterministic selection and tie resolution, executed action, resulting
distance, and resulting hunger used by the following turn.

- **Goal:** establish whether one retained internal motive can visibly alter a
  choice when an accepted threat and an accepted food offer conflict.
- **Perception:** retain the existing hearing-gated, independently validated
  threat and explicit-food-offer sensors; their outputs remain untrusted until
  validated.
- **Intent or choice:** score `flee`, `approach`, and `do_nothing` from only
  accepted perceptions and authoritative hunger; select the highest score.
  A tie uses the fixed order `flee`, then `approach`, then `do_nothing`.
- **Action:** retain the current action contracts: `flee` adds `5` distance,
  `approach` subtracts `3` without going below `1`, and `do_nothing` preserves
  distance.
- **Outcome:** execution changes only distance under those existing contracts.
- **Feedback or retained history:** after every completed turn, hunger becomes
  `min(100, starting_hunger + 10)` and is the following turn's hunger.
- **Later decision affected:** whether this local retained-motive policy is a
  candidate recurring boundary worth assessing before any reuse decision.

## Design

- **Authoritative inputs and initial state:** each fixture supplies starting
  distance and a non-boolean integer hunger in `[0, 100]`. Invalid hunger is
  rejected before perception or execution. The hearing range, distance
  transitions, and validated perception contracts remain as currently
  specified.
- **Need state and transitions:** hunger has the inclusive valid range
  `[0, 100]`. It increases by `10` at the completion of every valid turn and
  saturates at `100`. No event in this experiment reduces it. In particular,
  an accepted `food_offer` means only that the food-offer sensor produced
  grounded valid evidence; it neither establishes food reachability nor means
  the fox has consumed food. `approach` is movement only. A future reduction
  would require a separately specified, authoritative completed consumption
  outcome; consumption is deliberately out of scope here.
- **Scenario timeline or action contracts:** calculate `flee = 60` only for
  an accepted threat, `approach = hunger` only for an accepted food offer, and
  `do_nothing = 1`. All other action scores are `0`. Required corpus cases are:
  neither perception at hunger `0` (`do_nothing`); offer only at hunger `20`
  (`approach`); threat only (`flee`); the same accepted threat-and-offer
  conflict at hunger `30` (`flee`) and hunger `90` (`approach`); and a
  three-turn retained-state case starting at hunger `50`: neither perception
  raises it to `60`, the next conflict selects `flee` on the safety tie and
  raises it to `70`, and the final identical audible conflict selects
  `approach`. Rejected candidates remain unavailable to scoring. The retained
  case starts at distance `1`, so `flee` produces distance `6` and the final
  turn remains audible.
- **Expected trace or outputs:** each trace names the starting and resulting
  hunger, every candidate score, selected score and tie rule when applicable,
  accepted perception facts, action, and distance feedback. Re-running the
  fixture produces the same trace.
- **Deliberate exclusions:** consumption, food inventory or reachability,
  reduction of hunger, new LLM calls or fields, certainty thresholds, dialogue,
  inferred world facts, stochasticity, another actor, a generic need/utility
  framework, and changing the existing action contracts.
- **Candidate durable elements and disposable scaffolding:** the fox-local
  authoritative hunger -> fixed scores -> deterministic choice -> outcome ->
  hunger-feedback sequence is under test. The numeric range, increment,
  scores, corpus, trace types, and wrapper are disposable experiment
  parameters unless later evidence supports them.

## Signals and stop rule

- **Support signal:** the corpus shows both distinct outcomes for otherwise
  equivalent accepted threat-and-offer conflicts at low and high hunger; the
  retained-state case changes from safety-tie `flee` to high-hunger `approach`;
  every result is reproducible from trace inputs and fixed scores; rejected
  perceptions never contribute a score; and no model output changes
  authoritative state or selection.
- **Rejection signal:** explaining the required conflict outcomes needs an
  inferred world fact, model-provided score/transition/action, food consumption
  without an authoritative completed consumption outcome, or a generic actor
  or utility abstraction. It is also rejected if hunger cannot change a
  conflict outcome while preserving the stated authority boundary.
- **Inconclusive condition:** traces omit a starting/resulting hunger, action
  utilities, accepted-perception status, or the selected tie rule, so they
  cannot distinguish a retained-motive choice from the old fixed priority.
- **Stop rule:** run only the named baseline, single-motive, two fixed-conflict,
  retained-state, and rejected-perception cases. Stop after recording their
  reproducible traces. Do not introduce consumption, broader world state,
  randomness, another actor, or a reusable abstraction to improve a result.

## Result

Recorded at task Review. The Technical Lead finalizes this record's status
after the required Simplifier review and roadmap closure.

- **Observed result:** Supported. The corpus records `flee` for the accepted
  threat-and-offer conflict at hunger 30 and `approach` for the otherwise
  equivalent conflict at hunger 90. Its retained-state path starts at hunger
  50, advances 50 -> 60 -> 70, selects `flee` at the safety tie, then selects
  `approach`; rejected perceptions score only `do_nothing`.
- **Reproducibility evidence:** `.venv/bin/pytest
  tests/test_fox_deterministic_utility.py` passed (9 tests);
  `.venv/bin/python -m npc.experiments.fox_deterministic_utility` printed 9
  JSON-safe turn traces; `make check` passed Ruff, mypy, and the 35-test
  repository suite; and `git diff --check` passed.
- **Interpretation and limits:** This supports only the stated fox-local,
  deterministic experiment parameters and authority boundary. It neither
  establishes consumption, reachability, a reusable utility abstraction, nor
  behavior for another actor or stochastic policy.
- **Decision or unresolved question created:** The supported local result
  unlocks the decision of whether its authoritative hunger-to-selection-to-
  feedback sequence recurs under a contrasting decision before any reuse
  decision.
- **Canonical follow-up:** Strategy recurrence assessment.
