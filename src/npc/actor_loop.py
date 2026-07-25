from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ActorLoopRecord:
    reality: object
    perception: object
    sensemaking: object
    intent: object
    action: object
    outcome: object
    feedback: object


@dataclass(frozen=True)
class ActorLoopResult:
    reality: object
    record: ActorLoopRecord


class ActorContract(Protocol):
    def perceive(self, reality: object, model_output: object) -> object: ...

    def sensemake(self, reality: object, perception: object) -> object: ...

    def intend(self, reality: object, sensemaking: object) -> object: ...

    def act(self, reality: object, sensemaking: object, intent: object) -> object: ...

    def resolve(self, reality: object, action: object) -> tuple[object, object]: ...

    def feedback(self, reality: object, outcome: object) -> object: ...


class ActorLoop:
    def run(self, reality: object, model_output: object, contract: ActorContract) -> ActorLoopResult:
        perception = contract.perceive(reality, model_output)
        sensemaking = contract.sensemake(reality, perception)
        intent = contract.intend(reality, sensemaking)
        action = contract.act(reality, sensemaking, intent)
        outcome, next_reality = contract.resolve(reality, action)
        feedback = contract.feedback(next_reality, outcome)
        return ActorLoopResult(
            next_reality,
            ActorLoopRecord(reality, perception, sensemaking, intent, action, outcome, feedback),
        )
