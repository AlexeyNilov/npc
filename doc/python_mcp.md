# Python stdio MCP server

This document captures the reusable structure and contracts of a Python MCP
server that runs over stdio.

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
│       ├── __main__.py       # process entry point
│       ├── cli.py            # configuration and stdio startup
│       ├── config.py         # configuration loading and validation
│       ├── server.py         # server construction and tool registration
│       ├── <domain>.py       # business rules
│       └── <external>.py     # external-system client
└── tests/
    ├── test_config.py
    ├── test_<domain>.py
    ├── test_<external>.py
    ├── test_cli.py
    ├── test_mcp_tools.py
    └── test_stdio_integration.py
```

Expose the stdio server as a `[project.scripts]` entry point in
`pyproject.toml`. Document local development installation with
`pipx install --editable .` in `doc/install.md`.

Keep the entry point and tool handlers focused on orchestration. Put business
rules in domain modules, isolate side effects, and inject external clients or
lookup functions for tests. Let the official MCP SDK own protocol framing,
version negotiation, discovery, serialization, and protocol errors.

Keep exceptions in the module that defines their meaning: configuration errors
in `config.py`, external-system errors in the corresponding client, and domain
errors in the corresponding domain module. Translate expected failures to MCP
tool errors at the `server.py` boundary. Add a shared `exceptions.py` for a
deliberate exception hierarchy used by multiple modules.

## Stdio runtime

- Reserve stdout for MCP messages while the server runs. Send diagnostics and
  logs to stderr, including output from libraries and child processes.
- Receive runtime input through MCP requests and configuration. Load and
  validate configuration explicitly at startup, and establish network
  connections through the server lifespan.
- Let `config.py` own environment names, defaults, normalization, and
  validation. Load it once in `cli.py` and pass the typed configuration to the
  server and domain modules.
- Resolve packaged resources and configured paths independently of the client's
  working directory.
- Reuse long-lived clients where useful and close every server-owned resource
  through a typed server lifespan.
- Use async APIs in async handlers and run blocking functions in worker threads.
  Give external operations finite timeouts and apply bounded retries to
  idempotent operations.
- Let cancellation propagate. Put cleanup in `finally` and bound any shielded
  asynchronous cleanup. Make long synchronous operations check for cancellation.
- Report monotonic progress unconditionally for operations long enough to
  appear stalled; the SDK delivers it to callers that requested progress.

## Tool selection

Support optional tool switches in `~/.<project-name>/config.toml`, resolved
with `Path.home()`. Use stable MCP tool names as keys:

```toml
[tools]
lookup_host = true
lookup_pods = false
```

- Read the file once at startup in `config.py` using the standard library's
  `tomllib`. Pass the enabled tool names to server construction as a typed,
  immutable set.
- Enable all tools when the file is missing and enable omitted switches by
  default. Allow every tool to be disabled. This default also exposes newly
  added tools unless their switches are explicitly disabled.
- Accept only the `[tools]` table, known tool names, and boolean values. Fail
  startup with a diagnostic identifying the file and cause when an existing
  file is invalid or unreadable.
- Register only enabled tools using the existing registration functions. Let
  the SDK handle discovery and reject calls to unregistered tools.
- Apply edits after a server restart. Read the optional file without creating
  it automatically.
- Keep tool exposure separate from data-source access. Disabling an individual
  lookup tool leaves its source available to enabled combined tools. Define
  credential requirements separately from tool switches.

Document the concrete location, switches, defaults, restart requirement, and
credential behavior in the project's `doc/install.md`.

## Security and artifacts

- Limit tool results and logs to sanitized, actionable information suitable for
  their audience.
- For file-writing tools, define the destination, cache reuse, overwrite, and
  refresh behavior. Construct and validate paths so every write remains within
  the configured root.
- Use atomic replacement when interruption could corrupt an existing artifact.
  Return paths accessible to the MCP client.

## Tool contracts

- Give each tool one purpose and a stable, descriptive name. Its description
  shall state when to use it, accepted identifiers, scope boundaries, and
  observable side effects.
- Express argument constraints and defaults in the input schema. Validate
  semantic constraints before network calls or filesystem writes.
- Prefer Pydantic models or other fully typed return values. Let the SDK derive
  and validate the output schema and produce both model-readable `content` and
  machine-readable `structuredContent`. Keep field names stable and describe
  fields intended as inputs to downstream tools.
- Return bounded results. Use pagination, aggregation, or saved artifacts for
  large data, and report truncation or partial results explicitly.
- Distinguish an empty result, a missing object, an unavailable dependency, and
  an invalid upstream response. Represent incomplete data explicitly as a
  partial result or an error.
- Report expected validation, dependency, and business failures as safe,
  actionable tool errors. Let the SDK handle request validation, tool lookup,
  and protocol failures.
- Set read-only, destructive, idempotent, and open-world annotations to match
  actual behavior. Use annotations as client hints and enforce access controls
  in server code.
- Treat tool names, descriptions, schemas, defaults, annotations, result
  semantics, and expected errors as public API contracts.

## Contract verification

- Test tool names, descriptions, schemas, defaults, annotations, structured
  results, and expected errors through the SDK interface.
- Verify tool-selection defaults, explicit switches, invalid and unreadable
  files, discovery, rejected calls to disabled tools, and combined-tool source
  access. Isolate the home directory in tests and stdio subprocesses so the
  user's configuration cannot affect results.
- Verify validation completes before external calls or writes. Cover
  sanitization, bounded output, cancellation, and resource cleanup where
  relevant.
- Include a real stdio subprocess test that connects through the SDK, discovers
  the server, lists tools, calls one tool successfully, and receives one
  expected tool error using local fixtures.

## Recommended packages

Add packages for the features the project uses:

- Prefer [httpx2](https://pypi.org/project/httpx2/) for synchronous and
  asynchronous HTTP clients.
- Prefer [keyring](https://keyring.readthedocs.io/en/stable/) for storing and
  retrieving credentials through the operating system's credential store.
- Prefer [mcp](https://github.com/modelcontextprotocol/python-sdk), the official
  Model Context Protocol Python SDK, within the 2.x release line (`mcp>=2.3,<3`),
  for MCP clients and servers.
- Prefer [Pydantic](https://docs.pydantic.dev/) for validated configuration
  objects and structured MCP input and output models.
- Prefer [loguru](https://loguru.readthedocs.io/en/stable/) for application logging.
