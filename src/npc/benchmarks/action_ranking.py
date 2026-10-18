"""Benchmark production action ranking against local usefulness labels."""

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import cast

from npc.action_ranking import PROMPT_VERSION, rank_actions, validate_ranking_inputs
from npc.benchmarks.runner import Case, run_cases
from npc.model.evaluation import Evaluator, State


@dataclass(frozen=True)
class BenchmarkCase:
    """Ranking inputs and local-only usefulness labels."""

    id: str
    state: State
    actions: list[str]
    relevant_actions: list[str]


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonblank string in benchmark fixture")
    return value


def _names(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("Expected a list in benchmark fixture")
    names = [_text(item).strip() for item in value]
    if len(names) != len(set(names)):
        raise ValueError("Benchmark names must be unique after trimming")
    return names


def _case(value: object) -> BenchmarkCase:
    if not isinstance(value, dict):
        raise ValueError("Expected a benchmark case object")
    case = BenchmarkCase(
        id=_text(value.get("id")),
        state=cast(State, value.get("state")),
        actions=_names(value.get("actions")),
        relevant_actions=_names(value.get("relevant_actions")),
    )
    validate_ranking_inputs(case.state, case.actions)
    if not set(case.relevant_actions) <= set(case.actions):
        raise ValueError(f"{case.id}: relevance labels must name available actions")
    return case


def load_cases(path: Path) -> list[BenchmarkCase]:
    """Load UTF-8 JSON cases, rejecting inconsistent labels and duplicate IDs."""
    return _load(path.read_bytes())


def _load(data: bytes) -> list[BenchmarkCase]:
    payload: object = json.loads(data.decode("utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Benchmark fixture must be a JSON array")
    cases = [_case(value) for value in payload]
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("Benchmark case IDs must be unique")
    return cases


def run_benchmark(
    cases: list[BenchmarkCase], *, evaluator: Evaluator
) -> dict[str, object]:
    """Score every action equally; labels stay local and request errors stay unscored."""
    return run_cases(
        [
            Case(case.id, case.state, case.actions, case.relevant_actions)
            for case in cases
        ],
        predict=lambda case: [
            (item.action, item.probability)
            for item in rank_actions(case.state, case.candidates, evaluator=evaluator)
        ],
        evaluator=evaluator,
        benchmark="action-ranking",
        prompt_version=PROMPT_VERSION,
        candidate_name="action",
        label_name="relevant_actions",
    )


def run(path: Path, *, evaluator: Evaluator) -> dict[str, object]:
    """Load a dataset and include its SHA-256 file hash in the report."""
    data = path.read_bytes()
    report = run_benchmark(_load(data), evaluator=evaluator)
    report["dataset_hash"] = sha256(data).hexdigest()
    return report
