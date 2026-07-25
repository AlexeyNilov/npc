# Information Flow

This document owns the visual map of how durable information moves through the
repository. It is a map, not a procedure: ordinary discussion and read-only
exploration do not enter the implementation loop. For task lifecycle and
delegation rules, use [agent workflow](agent-workflow.md).

```mermaid
flowchart TB
  User[User feedback, requests, and discussion]

  subgraph Control[Control plane — outside the implementation loop]
    PM[Product Manager]
    Roadmap[Roadmap\nfuture outcomes]
    Planner[Planner]
    Packet[Ready task packet]
    Registry[Task registry\nopen packets]

    PM --> Roadmap
    Roadmap --> Planner
    User --> PM
    User --> Planner
    Planner --> Packet
    Packet --> Registry
  end

  subgraph Delivery[Implementation loop — one bounded packet]
    Role{Delivery role}
    Explorer[Explorer\nread-only discovery]
    Implementer[Implementer\nchange and verify]
    Simplifier[Simplifier\nremove excess complexity]
    Handoff[Evidence handoff]

    Packet --> Role
    Role --> Explorer
    Role --> Implementer
    Role --> Simplifier
    Explorer --> Handoff
    Implementer --> Handoff
    Simplifier --> Handoff
  end

  Handoff --> Planner

  subgraph Owners[Canonical durable-information owners]
    Vision[README\nvision and use]
    Requirements[Requirements\naccepted behavior]
    Architecture[Architecture\ncurrent mechanism]
    Decisions[Decisions\naccepted rationale]
    Evidence[Experiment evidence\nobserved results]
    Issues[Issue records\nunresolved problems]
    History[Git history\naccepted completed changes]
  end

  Planner --> Requirements
  Planner --> Architecture
  Planner --> Decisions
  Planner --> Evidence
  Planner --> Issues
  Planner --> History
  PM --> Vision
  PM --> Roadmap
  Evidence --> PM
  Issues --> PM
  Decisions --> PM

  Policy[AGENTS.md\ngeneric interaction defaults and owner map]
  Route[Route a durable fact\nto one canonical owner]
  Policy -. when recording a durable fact .-> Route
  Route --> Requirements
  Route --> Architecture
  Route --> Decisions
  Route --> Evidence
  Route --> Issues
  Route --> Vision
  Route --> Roadmap
```

## Reading the map

- The Product Manager and Planner are control-plane actors. They set direction,
  prepare a bounded packet, and accept its result; they are not delivery roles.
- Explorer, Implementer, and Simplifier operate only after a packet enters the
  implementation loop. Each returns evidence to the Planner rather than making
  unaccepted product or authority choices.
- The Planner routes accepted findings to one canonical owner. A finding may
  link to related records, but it is recorded in only one owner.
- `AGENTS.md` applies the owner rule only when a durable fact is recorded. It
  does not require a workflow for ordinary discussion, review, or read-only
  exploration.
