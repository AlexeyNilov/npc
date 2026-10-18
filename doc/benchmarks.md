# Benchmarks

Benchmarks measure action usefulness and complete-plan suitability through the
production rankers. Maintained datasets live in [`benchmarks/`](../benchmarks/).
Reports retain inputs, labels, predictions, errors, and dataset identity.

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
