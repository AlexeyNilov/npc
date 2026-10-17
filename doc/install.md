# Installation

Requires Python 3.12 or newer. From the project root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

For a runtime-only installation, install `-e .` instead.

## System One (planned)

The planned action-ranking adapter will use `httpx2` as a runtime dependency.
Configure the complete System One endpoint URL before running the benchmark CLI:

```sh
export SYSTEM_ONE=http://127.0.0.1:12346/v1/systemone
```

The CLI will require `SYSTEM_ONE` to contain an absolute HTTP or HTTPS URL and
pass it unchanged to the adapter. The URL already includes `/v1/systemone`;
the adapter will POST directly to it. Missing, blank, or invalid values will
produce a configuration error before any network request.
