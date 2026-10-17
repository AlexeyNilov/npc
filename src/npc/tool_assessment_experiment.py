"""Compare one-shot tool assessment with unchanged relevance ranking."""

import argparse
import json
import os
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx2

from npc.action_ranking import PROMPT_VERSION as RELEVANCE_VERSION
from npc.action_ranking import (
    InvalidEvaluationError,
    Question,
    SystemOneEvaluator,
    rank_actions,
)
from npc.system_one import SystemOneClient, SystemOneError
from npc.tool_assessment import PROMPT_VERSION, ToolScore, assess_tools


@dataclass(frozen=True)
class ExperimentCase:
    """Caller inputs and annotations kept outside model requests."""

    id: str
    family: str
    split: str
    intent: str
    state: str
    tools: tuple[str, ...]
    expected: tuple[str | None, ...]
    ready_tools: tuple[str, ...]
    preparation_tools: tuple[str, ...]


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonblank string")
    return value


def _names(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError("Expected an array of unique names")
    names = tuple(_text(item) for item in value)
    if len(set(names)) != len(names):
        raise ValueError("Names must be unique")
    return names


def _case(value: object) -> ExperimentCase:
    if not isinstance(value, dict):
        raise ValueError("Expected a case object")
    expected = value.get("expected")
    if not isinstance(expected, list) or not expected:
        raise ValueError("Expected at least one acceptable recommendation")
    case = ExperimentCase(
        id=_text(value.get("id")),
        family=_text(value.get("family")),
        split=_text(value.get("split")),
        intent=_text(value.get("intent")),
        state=_text(value.get("state")),
        tools=_names(value.get("tools")),
        expected=tuple(None if name is None else _text(name) for name in expected),
        ready_tools=_names(value.get("ready_tools")),
        preparation_tools=_names(value.get("preparation_tools")),
    )
    if case.split not in {"development", "held-out"}:
        raise ValueError("split must be development or held-out")
    labels = set(case.ready_tools + case.preparation_tools + case.expected)
    if not labels <= set(case.tools) | {None}:
        raise ValueError("Labels must name available tools")
    if any(name is not None and name not in case.ready_tools for name in case.expected):
        raise ValueError("Expected recommendations must be ready")
    return case


def load_cases(path: Path) -> list[ExperimentCase]:
    """Validate fixture annotations and keep each family in a single split."""
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Expected a JSON array of cases")
    cases = [_case(value) for value in payload]
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("Case IDs must be unique")
    splits: dict[str, str] = {}
    for case in cases:
        if splits.setdefault(case.family, case.split) != case.split:
            raise ValueError("Each family must belong to one split")
    return cases


class _Recorder:
    def __init__(self, evaluator: SystemOneEvaluator) -> None:
        self.evaluator = evaluator
        self.request: dict[str, object] | None = None
        self.response: object = None

    def evaluate(self, state: dict[str, str], questions: dict[str, Question]) -> object:
        self.request = {"state": state, "questions": questions}
        self.response = self.evaluator.evaluate(state, questions)
        return self.response


@dataclass
class _Result:
    case: ExperimentCase
    strategy: str
    prompt_version: str
    recommendation: str | None
    scores: list[dict[str, object]]
    request: dict[str, object] | None
    response: object
    model: str | None
    input_tokens: int | None
    elapsed_seconds: float
    error: str | None
    readiness_correct: int = 0
    readiness_judgments: int = 0


def _metadata(payload: object) -> tuple[str | None, int | None]:
    if not isinstance(payload, dict):
        return None, None
    model = payload.get("model")
    usage = payload.get("usage")
    tokens = usage.get("input_tokens") if isinstance(usage, dict) else None
    return (
        model if isinstance(model, str) else None,
        tokens if type(tokens) is int and tokens >= 0 else None,
    )


def _response_for_report(payload: object) -> object:
    # Retain invalid nonfinite values as text so the surrounding report stays JSON.
    try:
        json.dumps(payload, allow_nan=False)
    except ValueError:
        return {"nonfinite_response": json.dumps(payload, ensure_ascii=False)}
    return payload


def _evaluate(
    case: ExperimentCase,
    strategy: str,
    evaluator: SystemOneEvaluator,
    usefulness_cutoff: float,
    readiness_cutoff: float,
) -> _Result:
    recorder = _Recorder(evaluator)
    result = _Result(
        case,
        strategy,
        PROMPT_VERSION if strategy == "assessment" else RELEVANCE_VERSION,
        None,
        [],
        None,
        None,
        None,
        None,
        0,
        None,
    )
    start = perf_counter()
    try:
        if strategy == "assessment":
            assessment = assess_tools(
                case.intent,
                case.state,
                case.tools,
                evaluator=recorder,
                usefulness_cutoff=usefulness_cutoff,
                readiness_cutoff=readiness_cutoff,
            )
            result.recommendation = assessment.recommendation
            result.scores = [asdict(score) for score in assessment.scores]
            _readiness(result, assessment.scores, readiness_cutoff)
        else:
            ranking = rank_actions(
                case.intent, case.state, case.tools, evaluator=recorder
            )
            result.recommendation = ranking[0].action if ranking else None
            result.scores = [asdict(score) for score in ranking]
    except (SystemOneError, InvalidEvaluationError) as error:
        result.error = f"{type(error).__name__}: {error}"
    result.elapsed_seconds = perf_counter() - start
    result.request = recorder.request
    result.response = _response_for_report(recorder.response)
    result.model, result.input_tokens = _metadata(recorder.response)
    return result


def _readiness(result: _Result, scores: tuple[ToolScore, ...], cutoff: float) -> None:
    result.readiness_judgments = len(scores)
    result.readiness_correct = sum(
        (score.readiness >= cutoff) == (score.tool in result.case.ready_tools)
        for score in scores
    )


def _metrics(results: list[_Result]) -> dict[str, object]:
    successful = [result for result in results if result.error is None]
    reported = [
        result.input_tokens for result in results if result.input_tokens is not None
    ]
    return {
        "successful_cases": len(successful),
        "error_cases": len(results) - len(successful),
        "correct_recommendations": sum(
            r.recommendation in r.case.expected for r in successful
        ),
        "blocked_recommendations": sum(
            r.recommendation is not None and r.recommendation not in r.case.ready_tools
            for r in successful
        ),
        "unnecessary_preparation": sum(
            r.recommendation in r.case.preparation_tools
            and r.recommendation not in r.case.expected
            for r in successful
        ),
        "abstentions": sum(r.recommendation is None for r in successful),
        "readiness_correct": sum(r.readiness_correct for r in successful),
        "readiness_judgments": sum(r.readiness_judgments for r in successful),
        "model_calls": sum(r.request is not None for r in results),
        "calls_with_reported_tokens": len(reported),
        "input_tokens": sum(reported),
        "elapsed_seconds": sum(r.elapsed_seconds for r in results),
    }


def run_experiment(
    cases: list[ExperimentCase],
    *,
    evaluator: SystemOneEvaluator,
    usefulness_cutoff: float,
    readiness_cutoff: float,
) -> dict[str, object]:
    """Compare both strategies, recording errors separately from valid abstentions.

    Accuracy uses successful_cases as its denominator; readiness accuracy uses
    readiness_judgments. Token totals include only reported usage. Relevance
    ranking recommends its first entry and has no readiness gate or abstention
    threshold. Call order is fixed: assessment followed by relevance per case.
    """
    # Validate configuration even for an empty experiment, without a model call.
    assess_tools(
        "validate",
        "configuration",
        [],
        evaluator=evaluator,
        usefulness_cutoff=usefulness_cutoff,
        readiness_cutoff=readiness_cutoff,
    )
    results = [
        _evaluate(case, strategy, evaluator, usefulness_cutoff, readiness_cutoff)
        for case in cases
        for strategy in ("assessment", "relevance")
    ]
    return {
        "created_at": datetime.now(UTC).isoformat(),
        "cutoffs": {"usefulness": usefulness_cutoff, "readiness": readiness_cutoff},
        "results": [asdict(result) for result in results],
        "metrics": {
            strategy: _metrics([r for r in results if r.strategy == strategy])
            for strategy in ("assessment", "relevance")
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Requires SYSTEM_ONE containing the complete endpoint URL. Tune on development "
            "cases, then freeze prompts and cutoffs before held-out evaluation. Example: "
            "python -m npc.tool_assessment_experiment --input tests/fixtures/tool_assessment/cases.json "
            "--split development --usefulness-cutoff 0.6 --readiness-cutoff 0.7 "
            "--output /tmp/tool-assessment.json. Exit codes: 0 completed, 1 configuration/I/O "
            "error, 2 report saved with model errors. Recommendation mismatches are measurements."
        ),
    )
    parser.add_argument(
        "--input", required=True, type=Path, help="UTF-8 JSON case array"
    )
    parser.add_argument(
        "--split",
        required=True,
        choices=("development", "held-out"),
        help="Evaluate only this split",
    )
    parser.add_argument(
        "--usefulness-cutoff",
        required=True,
        type=float,
        help="Inclusive minimum usefulness in [0, 1]",
    )
    parser.add_argument(
        "--readiness-cutoff",
        required=True,
        type=float,
        help="Inclusive minimum readiness in [0, 1]",
    )
    parser.add_argument(
        "--output", required=True, type=Path, help="Write the JSON report here"
    )
    parser.add_argument(
        "--timeout",
        default=30.0,
        type=float,
        help="Positive finite HTTP timeout in seconds (default: 30)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the explicitly selected split using the existing HTTP transport."""
    args = _parser().parse_args(argv)
    try:
        cases = [case for case in load_cases(args.input) if case.split == args.split]
        if not cases:
            raise ValueError("Selected split has no cases")
        endpoint = os.environ.get("SYSTEM_ONE", "")
        with httpx2.Client() as client:
            evaluator = SystemOneClient(endpoint, client=client, timeout=args.timeout)
            report = run_experiment(
                cases,
                evaluator=evaluator,
                usefulness_cutoff=args.usefulness_cutoff,
                readiness_cutoff=args.readiness_cutoff,
            )
        report.update(endpoint=endpoint, split=args.split, timeout_seconds=args.timeout)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    except (ValueError, OSError) as error:
        print(f"Experiment failed: {error}", file=sys.stderr)
        return 1
    metrics = report["metrics"]
    assert isinstance(metrics, dict)
    return 2 if any(item["error_cases"] for item in metrics.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
