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

install:
	$(PIP) install -e ".[dev]"

test:
	$(PYTEST)

lint:
	$(RUFF) check .

mypy:
	$(MYPY)

format:
	$(RUFF) format .
	$(RUFF) check --fix .

check: format lint mypy test
