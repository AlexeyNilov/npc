# Decisions

This document owns consequential choices and their rationale.

### 2026-07-25: Use YAML scenarios for the initial trader experiment

**Status:** Accepted

**Context:** The first trader-decision experiment needs checked-in,
human-readable, reproducible inputs. Python's standard library does not parse
YAML.

**Decision:** Store the initial experiment scenario in YAML and use PyYAML to
load it.

**Consequences:** The scenario is reviewable outside Python and PyYAML is the
only current runtime dependency.

### 2026-07-25: Start evolution testing with paired deterministic decisions

**Status:** Accepted

**Context:** The conversation, language-model extraction, and formal actor-loop
experiments produced safe components but did not show that one hard-coded
trader path could evolve. A single successful scenario is insufficient evidence
for a reusable model.

**Decision:** Before adding another runtime boundary, choose two contrasting
actor decisions and use the second as a change test for the first. Inputs and
authoritative decisions remain explicit and deterministic. Retain only the
model elements that both decisions use.

**Consequences:** Conversational and language-model work is deferred. The next
architectural decision is based on observed change pressure rather than a
pre-designed framework.
