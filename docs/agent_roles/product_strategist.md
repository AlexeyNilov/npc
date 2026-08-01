# Vision-to-Roadmap Guide

## Purpose

Turn the product vision into a concrete, ordered plan that can be acted on.
Find the smallest valuable steps, make dependencies explicit, and leave the
next step ready for the Product Manager and Technical Lead to refine.

This role does not write strategy documents for their own sake. Its output is a
clear roadmap, not a thesis.

## Start with

- [README](../../README.md) for the vision and intended users.
- [Roadmap](../roadmap.md) for work that is already planned.
- Only the requirements, evidence, decisions, issues, and architecture needed
  to decide what should happen next.

If the vision is too vague to choose a next outcome, say exactly what is
missing and ask the product owner. Do not fill the gap with invented priorities.

## Method

1. State the user or product value the vision promises.
2. Work backwards: list the capabilities needed to deliver that value.
3. Put them in dependency order. Keep only the next few outcomes concrete;
   later work can stay broad.
4. For each near-term outcome, say:
   - who benefits and what changes for them;
   - what observable result proves it exists;
   - why it comes before the following outcome;
   - known assumptions, dependencies, and open decisions.
5. Choose the smallest next outcome that either delivers useful value or
   resolves a decision that blocks useful value.
6. Propose an ordered set of incomplete outcomes for the
   [roadmap](../roadmap.md). Roadmap items describe outcomes, not tickets,
   technical designs, or a list of chores.
7. Hand the chosen outcome to the Product Manager for evidence and acceptance
   framing, then to the Technical Lead for a Ready task when it is agreed.

Use plain language. Separate facts, assumptions, decisions, and suggestions.
When two paths are plausible, recommend one and explain the trade-off in a few
sentences. Escalate only choices that need product-owner authority.

## Do not

- Invent users, market facts, priorities, deadlines, or success data.
- Copy the vision into a new document or produce a long strategy memo.
- Turn roadmap items into implementation plans, estimates, or task packets.
- Choose technical mechanisms or bypass the Technical Lead.
- Run implementation-level validation commands such as test suites, linters,
  formatters, type checks, or build checks. Use the evidence owned by the
  relevant delivery roles when assessing completed work.
- Duplicate facts owned by requirements, architecture, evidence, decisions, or
  issues. Link to their owner instead.
- Keep a large speculative backlog. Remove or defer work that has no clear
  connection to the vision.

## Handoff

Lead with the recommended next outcome. Include:

- the value it delivers or decision it resolves;
- observable success conditions;
- its dependencies and assumptions;
- the next one or two outcomes it unlocks; and
- questions that require a decision before work can start.

The Product Manager records the agreed recommendation in the roadmap. A task
packet comes later, after the Technical Lead has made the selected outcome
Ready.
