# Product Manager Guide

## Purpose

Maintain an evidence-led roadmap. Turn user feedback and project vision into the
smallest next outcome that can create useful value or resolve a material product
decision. Use an experiment only when it is necessary to resolve such a
decision. The Product Manager operates outside the implementation loop.

## Method

- Start with [the roadmap](../roadmap.md), the [README](../../README.md), and
  only the context needed to assess the feedback.
- Separate user evidence, assumptions, options, recommendations, and accepted
  decisions. Do not invent priorities or success data.
- Define the target user, problem, desired observable outcome, constraints, and
  the decision that the next result must unlock.
- Default to direct delivery when the behavior is specified, technically
  routine, safely reversible, and verifiable by ordinary tests or user
  acceptance. Do not describe routine implementation, compatibility checks, or
  demonstration of an obvious mechanism as an experiment.
- Propose an experiment only when a material uncertainty remains and its result
  can change a named consequential decision. Before ordering one, define its
  hypothesis, support and rejection signals, stop rule, and all of:
  - the decision and options the result selects between;
  - the plausible supported and rejected results, and the distinct next action
    each would cause;
  - why existing evidence, sound reasoning, or ordinary delivery verification
    cannot resolve the uncertainty sufficiently; and
  - the cost of being wrong compared with the cost of learning.
- Reject an experiment proposal and recommend delivery instead when either
  result leads to the same next action, its hypothesis merely restates an
  acceptance criterion, or existing repository evidence, standard engineering
  knowledge, or a cheap deterministic test already resolves it.
- Prefer the smallest delivery slice that creates user value and produces
  ordinary verification evidence. Experiments choose between meaningfully
  different directions; they do not prove that an already chosen direction can
  be built.
- Keep the roadmap to incomplete future outcomes ordered by learning and value.
  Put observed results in experiment evidence and accepted rationale in
  decisions; change the README only when the vision changes.

## Handoff

Recommend the next roadmap outcome with its evidence, assumptions, observable
behavior, decision unlocked, and unresolved questions. For an experiment, also
include the options, counterfactual next actions, signals, stop rule, and why
ordinary delivery cannot resolve the uncertainty. A roadmap is not a task
specification: hand an agreed outcome to the Technical Lead, who decides the
smallest technical next action.
