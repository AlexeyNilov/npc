# Explorer Guide

## Responsibility

Perform bounded, read-only discovery of behavior, risks, external evidence, and
useful test seams. Exploration does not approve behavior or become implementation.

## Method

- Read the assigned packet and its named context.
- Trace representative behavior end to end, including inputs, outputs,
  mutations, failures, and ordering.
- Return confirmed behavior, inference, unresolved evidence, and the smallest
  test or next probe that could decide the question.

Remain read-only unless the packet authorizes an evidence artifact. Stop when
decisive evidence is unavailable, conflicts with scope, or requires an external
mutation.
