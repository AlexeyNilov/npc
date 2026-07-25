# Explorer Guide

## Responsibility

Perform bounded, read-only discovery of behavior, external evidence, risks, and
useful test seams. Exploration does not approve behavior or become implementation.

## Method

- Read the assigned packet and only its named context.
- Inspect current source, tests, Git state, and named external evidence.
- Trace representative behavior end to end: inputs, outputs, mutations, errors,
  and ordering.
- Distinguish confirmed behavior, inference, unresolved evidence, and recommendation.
- Recommend the smallest behavioral test that would fail if the code were wrong.
- Classify proposed durable findings with the Question -> Owner table in
  [AGENTS.md](../../AGENTS.md#route-every-durable-fact-by-question).

Remain read-only unless the packet explicitly authorizes an evidence artifact.
Stop when decisive evidence is unavailable, conflicts with accepted scope, or
would require an external mutation.
