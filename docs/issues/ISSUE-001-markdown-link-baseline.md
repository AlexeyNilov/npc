# ISSUE-001: Repository Markdown links lack a passing baseline

**Status:** Open

**Observed:** 2026-07-25

**Scope:** Documentation completion verification

## Problem

The repository has local Markdown links whose targets do not exist or whose
anchors were removed when completed roadmap outcomes left the incomplete-only
roadmap.

## Evidence

- `rg -n --glob '*.md' '\]\\([^)]*\.md(?:#[^)]*)?\)' .` identifies completed
  evidence records that formerly linked to removed roadmap headings.
- `AGENTS.md` and `README.md` link to `docs/decisions.md`, but that file is not
  present in the repository.

## Impact

The new completion-reconciliation rule requires Markdown-link checking, but a
repository-wide automated gate cannot be introduced as passing verification
until the baseline is classified and repaired or accepted as an explicit
tradeoff.

## Open question

What is the smallest link-checking mechanism and baseline repair that verifies
local file and heading links without adding an unnecessary dependency?

## Routing

- **Requirements:** None.
- **Architecture:** None.
- **Decision:** None.
- **Roadmap:** None.
- **Task:** None.

## Resolution

Pending.
