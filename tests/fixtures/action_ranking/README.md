# Action ranking benchmark

`cases.json` contains 16 synthetic scenarios with human-authored expectations.
They test next-step relevance under explicit facts and constraints, rather than
general similarity to the intent. Review these labels before treating them as a
benchmark for a particular application.

Each case contains:

- `id`: stable case identifier.
- `pair_id`: shared identifier for cases with identical intent and actions;
  `null` for standalone cases.
- `intent`, `state`, `actions`: the only fields supplied to the ranker.
- `expected_tiers`: action groups, best first. Every action appears once. Earlier
  groups should score strictly above later groups; order within a group is
  unconstrained and does not require equal probabilities.
- `relevant_actions`: actions labeled useful now, including information gathering
  and prerequisites. An empty list means none is useful in the stated situation.
- `rationale`: human-authored explanation of the expected ordering, used only
  when reviewing benchmark labels.

The five pairs cover diagnosis versus recovery, refund prerequisites, report
approval, shipment progress, and an instruction embedded in untrusted text.
Standalone cases cover several useful actions, credential prerequisites, a
specific build failure, an already completed intent, an unsuitable catalog, and
an empty catalog. Catalog order deliberately varies relative to expected rank.

## Comparing a model run

Send only the three input fields. Keep labels and rationales out of the request.
System One returns `answers.<question_id>.noul` probabilities for these questions;
the benchmark expects no generated rationale. Python maps probabilities to action
names and sorts them, producing only `action` and `probability` per ranked entry.
For each case save raw scores, returned order, model identifier/version, prompt
version, endpoint/server version, and elapsed time. A failed request is an
evaluation error, not a zero relevance score; report errors separately.

Measure:

1. **Pairwise ordering accuracy:** among all pairs of actions in different tiers,
   the fraction where the preferred action has a strictly higher probability.
   An exact score tie counts as a failure of a strict preference. Average per-case
   accuracies so large catalogs do not dominate; omit cases with no comparable
   pairs and report their count separately.
2. **Top-action relevance:** the fraction of cases with useful actions where the
   returned first action belongs to `relevant_actions`. This alone is insufficient:
   a model can get first place right while badly ranking the rest.
3. **State sensitivity:** report ordering accuracy for each member of a pair and
   whether both satisfy their expected comparisons. The first four pairs require
   a changed preference; the injection pair requires the preference to hold.
4. **Abstention:** report the maximum score for nonempty catalogs with no useful
   action. Ranking cannot reveal this failure by itself. A pass/fail cutoff needs
   separate calibration; this fixture supplies no invented target probabilities.
5. **Empty catalog:** expect an empty result without a model request.

These fixtures are a development set, not evidence of general model quality or
probability calibration. Keep a separate, human-reviewed set for final evaluation
after tuning prompts. Action-order permutations can reveal position sensitivity;
compare scores by action name, not positional question ID.
