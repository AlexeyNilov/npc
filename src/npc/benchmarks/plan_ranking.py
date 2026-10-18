"""Benchmark production plan ranking against local suitability labels."""

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import cast

from npc.benchmarks.runner import Case, run_cases
from npc.model.evaluation import Evaluator, State
from npc.plan_ranking import PROMPT_VERSION, rank_plans, validate_ranking_inputs


@dataclass(frozen=True)
class BenchmarkCase:
    """Ranking inputs and local-only suitability labels."""

    id: str
    state: State
    plans: list[str]
    acceptable_plans: list[str]


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
        plans=_names(value.get("plans")),
        acceptable_plans=_names(value.get("acceptable_plans")),
    )
    validate_ranking_inputs(case.state, case.plans)
    if not set(case.acceptable_plans) <= set(case.plans):
        raise ValueError(f"{case.id}: relevance labels must name available plans")
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
    """Score every plan equally; labels stay local and request errors stay unscored."""
    return run_cases(
        [
            Case(case.id, case.state, case.plans, case.acceptable_plans)
            for case in cases
        ],
        predict=lambda case: [
            (item.plan, item.probability)
            for item in rank_plans(case.state, case.candidates, evaluator=evaluator)
        ],
        evaluator=evaluator,
        benchmark="plan-ranking",
        prompt_version=PROMPT_VERSION,
        candidate_name="plan",
        label_name="acceptable_plans",
    )


def run(path: Path, *, evaluator: Evaluator) -> dict[str, object]:
    """Load a dataset and include its SHA-256 file hash in the report."""
    data = path.read_bytes()
    report = run_benchmark(_load(data), evaluator=evaluator)
    report["dataset_hash"] = sha256(data).hexdigest()
    return report
