# Architecture

This document owns the current verified system design.

## Shared target-aware threat detection

`npc.experiments.threat_detection` builds the one target-aware threat prompt,
makes the configured completion call, and parses and validates the common JSON
candidate. Its `perceive_threat` result contains only the raw candidate, parsed
candidate, and validation result; it never selects an action. The exact object
has `threat`, `certainty`, and `evidence`: threat is boolean, certainty is a
finite in-range number, and true evidence is a non-empty verbatim substring of
the player message while false evidence is null.

`python -m npc.experiments.wolf_threat` and
`python -m npc.experiments.fox_threat` load independent cases from
`scenarios/wolf_threat.yaml` and `scenarios/fox_threat.yaml` respectively. Both
call the shared perception module once per case and print a trace with their
target and expected threat/action pair. Their explicit local policies consume
only accepted threat: wolf maps true to `attack`, fox maps true to `flee`, and
false or invalid perception maps to `do_nothing` for both. Certainty is traced
but has no policy threshold or branch. The delivery has no creature state,
dialogue, world model, registry, or shared actor framework.
