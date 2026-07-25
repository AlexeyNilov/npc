# Decisions

This document owns consequential choices and their rationale.

### 2026-07-25: Preserve experiment evidence independently of implementation

**Status:** Accepted

**Context:** The project deliberately removes unsuccessful scaffolding, but
without a durable record its observations are compressed into later decisions
or lost. That encourages re-running the same work and makes roadmap choices
look like implementation preferences rather than evidence-led bets.

**Decision:** Keep one concise experiment-evidence record for every bounded
experiment. The record owns what the experiment demonstrated or refuted;
requirements, architecture, roadmap, and decisions retain their existing,
separate ownership.

**Consequences:** Removing code does not remove its learning. A small
documentation step is required before an experiment starts and when it is
reviewed.

### 2026-07-25: Use YAML scenarios for the initial trader experiment

**Status:** Accepted

**Context:** The first trader-decision experiment needs checked-in,
human-readable, reproducible inputs. Python's standard library does not parse
YAML.

**Decision:** Store the initial experiment scenario in YAML and use PyYAML to
load it.

**Consequences:** The scenario is reviewable outside Python and PyYAML is the
only current runtime dependency.
