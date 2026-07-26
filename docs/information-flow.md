# Information Flow

This document owns the visual map of how durable information moves through the
repository. It is a map, not a procedure: ordinary discussion and read-only
exploration do not enter the implementation loop. For task lifecycle and
delegation rules, use [agent workflow](agent-workflow.md).

```mermaid
flowchart TB
  User[User feedback, requests, and discussion]

  subgraph Control[Control plane — outside the implementation loop]
    Strategist[Product Strategist]
    Strategy[Strategy\nvision-to-capability path]
    PM[Product Manager]
    Roadmap[Roadmap\nfuture outcomes]
    TechLead[Technical Lead]
    Packet[Ready task packet]
    Registry[Task registry\nopen packets]

    Strategist --> Strategy
    Strategy --> PM
    PM --> Roadmap
    Roadmap --> TechLead
    User --> Strategist
    User --> PM
    User --> TechLead
    TechLead --> Packet
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

  Handoff --> TechLead

  subgraph Owners[Canonical durable-information owners]
    Vision[README\nvision and use]
    StrategyOwner[Strategy\ncapability path and constraints]
    Requirements[Requirements\naccepted behavior]
    Architecture[Architecture\ncurrent mechanism]
    Decisions[Decisions\naccepted rationale]
    Evidence[Experiment evidence\nobserved results]
    Issues[Issue records\nunresolved problems]
    History[Git history\naccepted completed changes]
  end

  TechLead --> Requirements
  TechLead --> Architecture
  TechLead --> Decisions
  TechLead --> Evidence
  TechLead --> Issues
  TechLead --> History
  TechLead -. removes completed outcome only .-> Roadmap
  Strategist --> StrategyOwner
  Vision --> Strategist
  Evidence --> Strategist
  Issues --> Strategist
  Decisions --> Strategist
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
  Route --> StrategyOwner
  Route --> Roadmap
```

## Reading the map

- The Product Strategist, Product Manager, and Technical Lead are control-plane
  actors. The Strategist maintains the capability path from vision; the Product
  Manager orders the next outcomes within it; the Technical Lead prepares a
  bounded packet and accepts its result. None is a delivery role.
- Explorer, Implementer, and Simplifier operate only after a packet enters the
  implementation loop. Each returns evidence to the Technical Lead rather than
  making unaccepted product or authority choices.
- The Technical Lead routes accepted findings to one canonical owner. A finding may
  link to related records, but it is recorded in only one owner.
- `AGENTS.md` applies the owner rule only when a durable fact is recorded. It
  does not require a workflow for ordinary discussion, review, or read-only
  exploration.
