import asyncio
import json
import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from npc.infrastructure.language_model import complete_text

Completion = Callable[[str, str], Awaitable[str]]
Action = Literal["attack", "do_nothing"]

AFFECT_SENSOR_PROMPT = """You are an untrusted affect sensor for one player message.
Return JSON only with exactly `affect` and `evidence`. `affect` must be one of
`hostile`, `non_hostile`, or `unclear`. `evidence` must be one non-empty,
verbatim substring from the player message that supports the affect reading.
Assess emotional tone only. Never invent text or facts beyond the player
message."""

SUPPORTED_AFFECTS = frozenset({"hostile", "non_hostile", "unclear"})


@dataclass(frozen=True)
class CandidateAffect:
    affect: str
    evidence: str


@dataclass(frozen=True)
class AffectTrace:
    case_id: str | None
    player_message: str
    expected_affect: str | None
    expected_action: str | None
    raw_candidate: str
    candidate: CandidateAffect | None
    validation_result: str
    action: Action


def parse_candidate(raw_candidate: str) -> CandidateAffect | None:
    try:
        payload = json.loads(_unwrap_json_fence(raw_candidate))
    except json.JSONDecodeError:
        return None
    if (
        not isinstance(payload, dict)
        or set(payload) != {"affect", "evidence"}
        or not isinstance(payload["affect"], str)
        or not isinstance(payload["evidence"], str)
    ):
        return None
    return CandidateAffect(affect=payload["affect"], evidence=payload["evidence"])


def _unwrap_json_fence(raw_candidate: str) -> str:
    stripped = raw_candidate.strip()
    fenced = re.fullmatch(r"```json\s*\n(?P<body>.*?)\n```", stripped, re.DOTALL | re.IGNORECASE)
    return fenced.group("body") if fenced else stripped


def validate_candidate(candidate: CandidateAffect, player_message: str) -> str:
    if candidate.affect not in SUPPORTED_AFFECTS:
        return "unsupported_affect"
    if not candidate.evidence:
        return "evidence_empty"
    if candidate.evidence not in player_message:
        return "evidence_not_in_player_message"
    return "accepted"


def decide_action(accepted_affect: str | None) -> Action:
    return "attack" if accepted_affect == "hostile" else "do_nothing"


async def run_case(
    player_message: str,
    completion: Completion = complete_text,
    expected: Mapping[str, str] | None = None,
) -> AffectTrace:
    raw_candidate = await completion(player_message, AFFECT_SENSOR_PROMPT)
    candidate = parse_candidate(raw_candidate)
    validation_result = "invalid_candidate" if candidate is None else validate_candidate(candidate, player_message)
    accepted_affect = candidate.affect if validation_result == "accepted" and candidate is not None else None
    return AffectTrace(
        case_id=expected.get("id") if expected else None,
        player_message=player_message,
        expected_affect=expected.get("expected_affect") if expected else None,
        expected_action=expected.get("expected_action") if expected else None,
        raw_candidate=raw_candidate,
        candidate=candidate,
        validation_result=validation_result,
        action=decide_action(accepted_affect),
    )


def load_corpus(path: Path) -> list[dict[str, str]]:
    data = cast(dict[str, Any], yaml.safe_load(path.read_text()))
    return [cast(dict[str, str], case) for case in cast(list[dict[str, object]], data["cases"])]


async def main_async() -> None:
    corpus_path = Path(__file__).parents[3] / "scenarios" / "wolf_affect.yaml"
    for case in load_corpus(corpus_path):
        trace = await run_case(case["player_message"], expected=case)
        print(json.dumps(asdict(trace), sort_keys=True))


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
