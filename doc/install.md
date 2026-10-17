# Installation

Requires Python 3.12 or newer. From the project root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

For a runtime-only installation, install `-e .` instead.

## System One

The action-ranking adapter uses `httpx2`, installed as a runtime dependency.
Configure the complete System One endpoint URL before running the benchmark CLI:

```sh
export SYSTEM_ONE=http://127.0.0.1:12346/v1/systemone
```

The CLI requires `SYSTEM_ONE` to contain an absolute HTTP or HTTPS URL and
passes it unchanged to the adapter. The URL already includes `/v1/systemone`;
the adapter POSTs directly to it. Missing, blank, or invalid values produce a
configuration error before any network request. Export it in the shell that
launches the command.
