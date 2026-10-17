# Installation

Requires Python 3.12 or newer. From the project root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

For a runtime-only installation, install `-e .` instead.

## System One

```sh
export SYSTEM_ONE=http://127.0.0.1:12346/v1/systemone
```
