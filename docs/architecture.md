# Architecture

This document owns the current verified system design.

For the project-specific vocabulary used below, see the [Glossary](glossary.md).

## First reboot proof

`python -m npc <scenario-path>` loads a scenario YAML document and the separate
actor-profile YAML document it references. The scenario provides one actor's
initial location and entities on a disposable one-dimensional scaffold. The
profile declares capabilities, motivations, and ordered rules.

For each turn, the first matching profile rule creates a bounded proposal. The
simulation core authoritatively accepts or rejects only movement and
consumption, updates canonical state only for accepted proposals, and returns
deterministic narration. Profile rules select tagged entities and give the
observer-facing action label; the core has no actor-specific policy.
