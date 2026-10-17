# npc

Rank available action names by their relevance to an intent in a textual state,
using the System One API. Python validates the probabilities and returns a stable
ranking; action execution belongs to the caller.

Includes a Python API and `npc-benchmark` for evaluating labeled scenarios.
Run `npc-benchmark --help` for command usage. See the
[ranking design](doc/action.md) and
[benchmark cases](tests/fixtures/action_ranking/README.md).

See [installation](doc/install.md) and [contributing](CONTRIBUTING.md).
