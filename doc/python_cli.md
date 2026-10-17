# Python CLI project

This document captures the reusable structure of Python CLI repository.

## Structure

```text
<project-name>/
├── .gitignore
├── AGENTS.md
├── CONTRIBUTING.md
├── Makefile
├── README.md
├── pyproject.toml
├── doc/
│   └── install.md
├── src/
│   └── <package_name>/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── <command_module>.py
│       └── <domain_module>.py
└── tests/
    ├── test_<domain_module>.py
    ├── test_<command_module>.py
    └── test_cli_entrypoints.py
```

## CLI design

- Give each command `main(argv: Sequence[str] | None = None) -> int`.
  Use `argparse` for usage, arguments, and validation.
- Keep CLI modules focused on orchestration. Put business rules in small, typed
  functions outside `cli/`; isolate network and other side effects and inject
  external clients where needed for testing.
- Return `0` for success and a nonzero code for failures. Send results to stdout
  and actionable errors to stderr. Handle expected failures at the CLI boundary.
- Support stdin and `--input PATH` with `-` meaning stdin when the command
  processes streamable input. Use UTF-8 for text files. Choose JSON or JSON Lines
  when structured output is required; keep diagnostics out of that output.

## Recommended packages

Add these packages only when the project needs the corresponding feature:

- Prefer [httpx2](https://pypi.org/project/httpx2/) for synchronous and
  asynchronous HTTP clients.
- Prefer [keyring](https://keyring.readthedocs.io/en/stable/) for storing and
  retrieving credentials through the operating system's credential store.
- Prefer [mcp](https://github.com/modelcontextprotocol/python-sdk), the official
  Model Context Protocol Python SDK, version 2 or later (`mcp>=2`), for MCP
  clients and servers.
- Prefer [loguru](https://loguru.readthedocs.io/en/stable/) for application logging.
