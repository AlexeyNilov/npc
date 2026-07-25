# TASK-002: Reuse target-aware threat detection for a fleeing fox

**Status:** Ready

**Owner:** Unassigned

**Delivery role:** [Implementer](../agent_roles/implementer.md)

**Agent profile:** `implementer`

**Base commit:** `03f1be77b39a5a2e7669e296ad4d7aa7a47409e9`

**Depends on:** None

**Write scope:** `src/npc/experiments/threat_detection.py`,
`src/npc/experiments/wolf_threat.py`, `src/npc/experiments/fox_threat.py`,
`scenarios/fox_threat.yaml`, `tests/test_threat_detection.py`,
`tests/test_wolf_threat.py`, `tests/test_fox_threat.py`, and
`docs/evidence/2026-07-25-shared-threat-detection.md`

**Parallel-safe with:** None — the extraction and both wrappers share the
binary contract and require one writer.

**Durable information changed:** Experiment result ->
`docs/evidence/2026-07-25-shared-threat-detection.md` at Review. Update
requirements and architecture only after Technical-Lead acceptance; add no
decision record unless a broader capability structure is accepted.

**Simplifier review:** Required — the task adds a candidate reusable module and
cross-module change. Review for a premature creature registry, generic actor
framework, or duplicated shared contract.

## Outcome

A developer can run the existing wolf corpus and a new fox corpus through one
shared target-aware threat-detection capability, inspect the identical
perception contract, and see accepted threats map deterministically to wolf
`attack` or fox `flee`.

## Experiment evidence

- **Evidence record:** `docs/evidence/2026-07-25-shared-threat-detection.md`.
- **Hypothesis and decision unlocked:** use the record's stated reuse hypothesis
  and its bounded-capability decision.
- **Result handoff:** complete all Result fields at Review, including an
  inconclusive or negative live-run result. Fixture results do not demonstrate
  general model accuracy.

## Vision alignment

- **Vision behavior made observable:** one LLM sensor contract is reusable
  while deterministic creature policies retain action authority.
- **Classification:** `Candidate durable system foundation`.
- **Reuse pressure:** wolf `attack` and fox `flee` consume the same accepted
  perception but need different action mapping.
- **Boundary rejection signal:** supporting these two policies requires
  creature-specific sensor contracts, a second LLM call, a registry, shared
  state, or a generic actor framework.

## Canonical context

- [Roadmap: Reuse threat detection for a fleeing fox](../roadmap.md#reuse-threat-detection-for-a-fleeing-fox).
- [Prior binary-gate evidence](../evidence/2026-07-25-wolf-binary-threat-gate.md),
  including its completed contract and limits.
- [Architecture: Wolf binary threat-perception experiment](../architecture.md#wolf-binary-threat-perception-experiment).
- Initial source/test/corpus references:
  `src/npc/experiments/wolf_threat.py`, `tests/test_wolf_threat.py`, and
  `scenarios/wolf_threat.yaml`.

Read [AGENTS.md](../../AGENTS.md), this packet, the Implementer guide, and only
the context named above. Do not read the task registry, sibling packets,
completed tasks, or unrelated planning history.

## Task-specific scope

- Extract only the threat candidate dataclass, prompt construction, one-call
  perception execution, JSON-fence transport normalization, parsing, and
  validation into `threat_detection.py`. Its prompt accepts a program-owned
  target name and asks only whether the player message contains a credible
  hostile threat toward that named creature.
- Preserve the exact candidate shape and deterministic validation already
  verified for the wolf. The shared component must return perception/validation
  data, never an action.
- Keep thin, explicit wolf and fox wrappers. Wolf policy maps accepted `true`
  to `attack`; fox policy maps accepted `true` to `flee`; both map all other
  results to `do_nothing`. Do not introduce a policy lookup table, creature
  enum, registry, or base class.
- Keep the wolf CLI and checked-in corpus working. Add a fox CLI and
  `scenarios/fox_threat.yaml` with independent direct-threat, calm/friendly,
  fearful, and ambiguous cases; its direct threat must be textually directed at
  the fox. Each trace displays its target and expected threat/action pair.
- Add failing behavior tests before extraction for: shared parser/validator
  contract; target-specific prompt text with no action/world instruction; one
  completion call for each wrapper; the same accepted candidate mapping to
  `attack` vs `flee`; malformed/ungrounded true candidates producing
  `do_nothing` for both; corpus coverage; and certainty-invariant policies.
- Complete only the experiment record at Review. Exclude changes to trader or
  affect experiments, memory, dialogue, state, LLM action selection, registry
  infrastructure, decision records, requirements, and architecture until
  Technical-Lead acceptance.

## Acceptance and verification

- `python -m npc.experiments.wolf_threat` and
  `python -m npc.experiments.fox_threat` print one JSON trace per checked-in
  case. Every trace includes target, expected threat/action, raw candidate,
  parsed candidate, validation result, and action.
- The two wrappers use one shared candidate schema and validation path. The
  same accepted grounded `true` maps to wolf `attack` and fox `flee`; no false,
  malformed, invalid-certainty, or ungrounded candidate can cause either
  non-null action.
- Changing only certainty leaves both policy results unchanged.
- Tests cover the extracted component, each policy/wrapper, both corpora, and
  the existing wolf behavior. Add tests before behavior-changing extraction.
- Run `.venv/bin/pytest tests/test_threat_detection.py`,
  `.venv/bin/pytest tests/test_wolf_threat.py`,
  `.venv/bin/pytest tests/test_fox_threat.py`, `make check`, and
  `git diff --check`. Record exact results and live-run limits in the evidence
  record/handoff.

## Stop conditions

- Stop if target awareness requires a model-proposed creature identity,
  creature-specific schema/validation, world facts, or a product definition of
  threat beyond the roadmap.
- Stop if the existing wolf corpus cannot run unchanged through the extracted
  capability, or if the fox corpus's expected threat requires disputed semantic
  interpretation.
- Stop if reuse requires a registry, base creature type, persistent state,
  second model call, or a certainty threshold; return the evidence and options
  to the Technical Lead rather than adding any of them.
- Stop for unexpected user-owned changes, missing completion access needed for
  a claimed live result, required scope expansion, or external mutation.

## Handoff

**Status and outcome:** Pending

**Changed files and ownership impact:** Pending

**Verification:** Pending

**Assumptions, risks, and next action:** Pending
