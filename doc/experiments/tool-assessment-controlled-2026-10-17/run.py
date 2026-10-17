"""Replay the controlled experiment from the repository root: run.py PHASE.

PHASE is development, freeze, held-out, or summarize. Live phases make 16 model
requests each. Use a copy of this artifact directory for subsequent runs.
"""

import argparse
import hashlib
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx2

from npc.system_one import SystemOneClient
from npc.tool_assessment import assess_tools
from npc.tool_assessment_experiment import load_cases

ROOT = Path(__file__).resolve().parent
METHODS = ("usefulness_only", "usefulness_readiness")


def write(name, payload):
    (ROOT / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def read(name):
    return json.loads((ROOT / name).read_text())


def recommend(scores, method, u, r):
    eligible = [
        s
        for s in scores
        if s["usefulness"] >= u and (method == "usefulness_only" or s["readiness"] >= r)
    ]
    best = max(eligible, key=lambda s: s["usefulness"], default=None)
    return best["tool"] if best else None


def metrics(rows, u, r):
    correct = blocked = unnecessary = abstentions = 0
    recommendations = []
    for row in rows:
        c = row["case"]
        chosen = recommend(row["scores"], row["method"], u, r)
        correct += chosen in c["expected"]
        blocked += chosen is not None and chosen not in c["ready_tools"]
        unnecessary += chosen in c["preparation_tools"] and chosen not in c["expected"]
        abstentions += chosen is None
        recommendations.append(
            dict(
                case=c["id"],
                method=row["method"],
                tool=chosen,
                correct=chosen in c["expected"],
            )
        )
    return dict(
        correct=correct,
        total=len(rows),
        blocked=blocked,
        unnecessary_preparation=unnecessary,
        abstentions=abstentions,
        recommendations=recommendations,
    )


class ControlledEvaluator:
    def __init__(self, client, method):
        self.client = client
        self.method = method
        self.request = None
        self.response = None

    def evaluate(self, state, questions):
        actual = (
            questions
            if self.method == "usefulness_readiness"
            else {k: v for k, v in questions.items() if k.endswith("_useful")}
        )
        self.request = dict(state=state, questions=actual)
        self.response = self.client.evaluate(state, actual)
        if self.method == "usefulness_readiness":
            return self.response
        # Reuse the public scorer's validation and stable identity mapping.
        # Internal constant readiness values only adapt the interface: they are
        # never sent to the model, saved as judgments, or used for selection.
        adapted = dict(self.response)
        answers = dict(adapted["answers"])
        answers.update(
            {k: dict(type="noul", noul=1.0) for k in questions if k.endswith("_ready")}
        )
        adapted["answers"] = answers
        return adapted


def evaluate_case(c, method, client, u, r, split):
    adapter = ControlledEvaluator(client, method)
    started = perf_counter()
    try:
        result = assess_tools(
            c.intent,
            c.state,
            c.tools,
            evaluator=adapter,
            usefulness_cutoff=u,
            readiness_cutoff=r if method == "usefulness_readiness" else 0,
        )
    except Exception as error:
        write(
            f"{split}-connection-or-evaluation-error.json",
            dict(
                time=datetime.now(UTC).isoformat(),
                case=c.id,
                method=method,
                error=str(error),
                request=adapter.request,
                response=adapter.response,
            ),
        )
        raise
    scores = [asdict(s) for s in result.scores]
    if method == "usefulness_only":
        for score in scores:
            del score["readiness"]
    row = dict(
        case=asdict(c),
        method=method,
        scores=scores,
        request=adapter.request,
        response=adapter.response,
        elapsed_seconds=perf_counter() - started,
        recorded_at=datetime.now(UTC).isoformat(),
    )
    return row


def live(split):
    path = ROOT / f"{split}.json"
    if path.exists() or (ROOT / f"{split}-partial.json").exists():
        raise RuntimeError("Preserve existing results; replay in a copied directory")
    frozen = read("cutoff-selection.json") if split == "held-out" else None
    u, r = (
        (frozen["selected"][k] for k in ("usefulness", "readiness"))
        if frozen
        else (0.6, 0.7)
    )
    cases = [c for c in load_cases(ROOT / "cases.json") if c.split == split]
    rows = []
    with httpx2.Client() as transport:
        client = SystemOneClient(
            read("protocol.json")["endpoint"], client=transport, timeout=30
        )
        for index, c in enumerate(cases):
            methods = METHODS if index % 2 == 0 else METHODS[::-1]
            for method in methods:
                row = evaluate_case(c, method, client, u, r, split)
                rows.append(row)
                write(f"{split}-partial.json", rows)
                print(c.id, method, recommend(row["scores"], method, u, r), flush=True)
    write(f"{split}.json", rows)
    (ROOT / f"{split}-partial.json").unlink()


def freeze():
    if (ROOT / "cutoff-selection.json").exists():
        raise RuntimeError("Cutoffs already frozen")
    rows = read("development.json")
    candidates = []
    for u in read("protocol.json")["grid"]:
        for r in read("protocol.json")["grid"]:
            m = metrics(rows, u, r)
            candidates.append(
                dict(
                    usefulness=u,
                    readiness=r,
                    **{k: v for k, v in m.items() if k != "recommendations"},
                )
            )
    winner = min(
        candidates,
        key=lambda c: (
            -c["correct"],
            c["blocked"],
            c["unnecessary_preparation"],
            (c["usefulness"] - 0.6) ** 2 + (c["readiness"] - 0.7) ** 2,
            c["usefulness"],
            c["readiness"],
        ),
    )
    write(
        "cutoff-selection.json",
        dict(
            frozen_at=datetime.now(UTC).isoformat(),
            selected=winner,
            development_sha256=hashlib.sha256(
                (ROOT / "development.json").read_bytes()
            ).hexdigest(),
            candidates=candidates,
        ),
    )
    print(json.dumps(winner))


def summarize():
    selection = read("cutoff-selection.json")["selected"]
    u, r = selection["usefulness"], selection["readiness"]
    summary = dict(cutoffs=dict(usefulness=u, readiness=r), splits={})
    for split in ("development", "held-out"):
        rows = read(f"{split}.json")
        paired = {}
        for method in METHODS:
            selected = [row for row in rows if row["method"] == method]
            m = metrics(selected, u, r)
            m["input_tokens"] = sum(
                row["response"]["usage"]["input_tokens"] for row in selected
            )
            if method == "usefulness_readiness":
                m["readiness_labels_correct"] = sum(
                    (score["readiness"] >= r)
                    == (score["tool"] in row["case"]["ready_tools"])
                    for row in selected
                    for score in row["scores"]
                )
                m["readiness_labels_total"] = sum(
                    len(row["scores"]) for row in selected
                )
            m["readiness_gate_changes"] = (
                sum(
                    recommend(row["scores"], method, u, r)
                    != recommend(row["scores"], method, u, 0)
                    for row in selected
                )
                if method == "usefulness_readiness"
                else None
            )
            paired[method] = m
        summary["splits"][split] = paired
        grouped = {
            c["case"]["id"]: [
                row for row in rows if row["case"]["id"] == c["case"]["id"]
            ]
            for c in rows
        }
        for pair in grouped.values():
            a, b = pair
            assert a["request"]["state"] == b["request"]["state"]
            aq = {
                k: v
                for k, v in a["request"]["questions"].items()
                if k.endswith("_useful")
            }
            bq = {
                k: v
                for k, v in b["request"]["questions"].items()
                if k.endswith("_useful")
            }
            assert aq == bq
        summary["splits"][split]["max_usefulness_score_difference"] = max(
            abs(a["usefulness"] - b["usefulness"])
            for pair in grouped.values()
            for a, b in zip(pair[0]["scores"], pair[1]["scores"])
        )
    write("summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Run the controlled usefulness/readiness experiment from the repository root. "
            "Each live phase makes 16 model requests. To replay, copy run.py, cases.json, "
            "and protocol.json into an empty directory; existing completed runs are preserved. "
            "Use PYTHONPATH=src .venv/bin/python PATH/run.py development, then freeze, "
            "held-out, and summarize, in that order. Freeze and summarize are offline."
        )
    )
    parser.add_argument(
        "phase", choices=("development", "freeze", "held-out", "summarize")
    )
    phase = parser.parse_args().phase
    if phase in ("development", "held-out"):
        live(phase)
    elif phase == "freeze":
        freeze()
    elif phase == "summarize":
        summarize()
    else:
        raise ValueError("Expected development, freeze, held-out, or summarize")
