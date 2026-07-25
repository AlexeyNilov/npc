# local_llm_project_template

TBD

## Setup

* Create new Git repo
* Copy content of https://github.com/AlexeyNilov/local_llm_project_template to the new repo
* Commit
* Rename from local_llm_project_template to new repo name `bash scripts/rename-template.sh your-new-repo-name`
* Create venv
* Install package `python -m pip install -e ".[dev]"`
* Copy `.env.example` to `.env` and adjust local settings if needed

## Project documentation

- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Decisions](docs/decisions.md)
- [Roadmap](docs/roadmap.md)
- [Development workflow](CONTRIBUTING.md)

## Install

```bash
python -m venv .venv
source .venv/bin/activate
make install
```