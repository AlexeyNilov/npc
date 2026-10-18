# Benchmarks

Benchmarks measure action usefulness and complete-plan suitability through the
production rankers. Maintained datasets live in [`benchmarks/`](../benchmarks/).
Reports retain inputs, labels, predictions, errors, and dataset identity.

Compare the two action rankers with
`python -m experiments.action_ranking_comparison` from the project root.
Its `--help` owns arguments and scoring details. The experiment reuses the
maintained action dataset and preserves the current benchmark's native metrics.
It adds paired top-action accuracy and mean reciprocal rank for both approaches.
Higher values are better. These metrics include only cases with a useful action
and successful requests from both approaches.

Cases with no useful action appear separately. Choice always distributes
probability among the supplied actions, so a high choice probability cannot
establish usefulness. The current ranker can abstain when every relevance score
is below its threshold. Binary Brier scores remain specific to the current ranker.
The experiment runs the current ranker first, then choice; timing from a single
run can reflect server load and warmup. The combined report is saved in `runs/`.

Run `npc-benchmark --help` for commands, dataset formats, and scoring behavior.
The default benchmark evaluates actions; select `plan-ranking` to evaluate plans.

Add cases to the JSON datasets to extend coverage. To add a benchmark, follow
[`action_ranking.py`](../src/npc/benchmarks/action_ranking.py) and register its `run`
function in [`cli/benchmark.py`](../src/npc/cli/benchmark.py). The shared runner owns
execution, timing, error recording, and binary scoring. Each benchmark owns input
validation and its call to the production ranker.

[`experiments/plan_context_sensitivity.py`](../experiments/plan_context_sensitivity.py)
preserves the four original context-change scenarios and reports score changes
without correctness labels. Run its `--help` for usage. The plan dataset includes
explicit complete recovery alternatives because some original scenarios offer
no plan that fixes the stated cause.

Brier scores measure squared error against binary labels; lower is better.
Request errors contribute no score, so inspect them alongside quality metrics.
Labels express expected behavior and need review when cases change. These small
datasets measure the supplied scenarios, not general model quality. Generated
reports in `runs/` are ignored by Git.
