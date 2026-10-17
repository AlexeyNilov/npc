ifeq ($(OS),Windows_NT)
VENV_BIN = .venv/Scripts
EXE = .exe
else
VENV_BIN = .venv/bin
EXE =
endif

PYTHON = $(VENV_BIN)/python$(EXE)
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest
RUFF = $(PYTHON) -m ruff
MYPY = $(PYTHON) -m mypy

.PHONY: install test test-integration mutation lint mypy format format-check check

install:
	$(PIP) install -e ".[dev]"

test:
	$(PYTEST) -q

test-integration:
	$(PYTEST) -m integration

# Explicit selection reruns cached mutations, including after test-only changes.
# Usage: make mutation SCOPE='python_template.*'
mutation:
	$(if $(strip $(SCOPE)),,$(error Provide SCOPE, e.g. make mutation SCOPE='python_template.*'))
	@$(PYTHON) scripts/mutation.py "$(SCOPE)"

lint:
	$(RUFF) check .

mypy:
	$(MYPY)

format:
	$(RUFF) format .
	$(RUFF) check --fix .

# Keep style consistent without relying on contributors to run formatting separately.
# Apply automatic fixes before validation so style drift does not accumulate.
check: format mypy test
