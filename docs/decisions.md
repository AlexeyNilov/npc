# Decisions

This document owns consequential choices and their rationale.

### 2026-07-25: Use YAML scenarios

**Status:** Accepted

**Context:** The fixed creature corpora need checked-in, human-readable,
reproducible inputs. Python's standard library does not parse YAML.

**Decision:** Store the initial experiment scenario in YAML and use PyYAML to
load it.

**Consequences:** PyYAML is the only current runtime dependency.

### 2026-07-26: Permit expressive hunger interpretation in utility narration

**Status:** Accepted

**Context:** The utility chat displays authoritative hunger numerically, but
the optional narration does not make that state legible as player-facing prose.
The player wants the configured narrator to use hunger as expressive context.

**Decision:** For a completed utility turn only, the narrator receives the
resulting authoritative hunger as an exact `0` through `100` value in addition
to the completed action only when that value is greater than `50`. It must
interpret supplied hunger as expressive food-seeking prose. The CLI's hunger
display remains authoritative, while narration remains non-authoritative and
cannot affect any later turn.

**Consequences:** The narration prompt intentionally carries one additional
canonical fact and permits flavor that may overstate or misdescribe an internal
state. It still excludes player text, perception evidence, distance, and
mutable state, and it does not validate the narrator's free-form wording.

### 2026-07-26: Center the product on a modular authoritative simulation engine

**Status:** Accepted

**Context:** The prior LLM-system effort attempted a broad simulation design at
once and became too complex to advance comfortably. This project deliberately
reduced that scope from a complete system, to an NPC, to a trader, and finally
to a small fox actor. That decomposition produced useful evidence, especially
for narrow binary LLM perception, but the product vision and strategy then
became too closely centered on the laboratory method and fox-local decisions.

**Decision:** The product destination is a modular simulation engine, not a
learning laboratory. Actor loops interact with a shared authoritative
simulation core: they interpret reality and propose actions, while the
simulation core resolves outcomes and maintains canonical state. Grow toward
that destination through the smallest causally complete vertical slices rather
than by recreating a comprehensive framework up front. Treat the fox as
completed foundational evidence and, where useful, a stable test actor; do not
make additional fox cognition the strategic objective.

The long-term product should let simulation builders author, run, inspect,
replay, and eventually branch scenarios with heterogeneous actors.

Use the prior LLM-system design and external approaches as decision inputs, not
as architectures to import wholesale. Comparative discovery must be bounded to
a capability choice or strategic constraint that it can change.

**Alternatives considered:**

- Continue with contrasting fox decisions or richer actor cognition first. This
  would add actor-policy evidence without establishing the causal simulation
  boundary required by the product vision.
- Recreate the prior LLM-system design as a comprehensive framework. This would
  abandon the incremental decomposition that made the current evidence
  tractable and repeat the complexity that prompted the new project.
- Grant a generative Game Master authority over world outcomes. This offers more
  expressive resolution but is not preferred while canonical validation and
  causal replay are the product's differentiating constraints.
- Choose an application-specific vertical immediately. No named external user
  or problem yet provides stronger capability requirements than the current
  domain-neutral discovery path. The triggers for revisiting these alternatives
  remain in
  [Strategy](strategy.md#reconsideration).

**Consequences:** The strategy pivots from recurring fox decisions to an
evidenced boundary between actor and simulation core, followed by shared-world
composition and cross-scale portability. Existing fox evidence and current
implementation remain valid within their recorded limits. The Product Manager
must replace the roadmap's now-obsolete product frame and order an outcome that
advances causal closure. Historical experiment follow-ups remain accurate
records of what their results unlocked at completion.

### 2026-07-26: Define determinism as replayable authoritative causality

**Status:** Accepted

**Context:** The current fox policies and transitions are deterministic, and
the earlier vision could be read as requiring all future actor behaviour to be
predictable. That interpretation would confuse the current experiment method
with the engine's durable value and unnecessarily exclude controlled variation.

**Decision:** Require authoritative causality to be explicit, traceable, and
replayable. Actor behaviour need not remain fully predictable. Randomness or
generative variation may be introduced for a defined outcome when the run
records the initial state, ordered inputs, submitted proposals, resolution
decisions, and controlled variation needed to reproduce its causal transitions.
Generated output never bypasses authoritative validation or directly mutates
canonical reality.

Treat bounded, verifiable proposals as the durable method for containing LLM
uncertainty. Binary evidence-grounded questions are its first supported
perception form, not a claim that every future LLM role must be binary.

**Consequences:** The completed deterministic utility experiment remains
unchanged and does not retroactively establish stochastic behaviour. Future
capability choices may introduce controlled variation without weakening
authority, inspection, or replay. The strategy no longer treats deterministic
action selection as a permanent product constraint.

### 2026-07-26: Use natural language as the default actor-world semantic interface

**Status:** Accepted

**Context:** Heterogeneous actors need to interpret simulation state without
embedding simulation-specific schemas and traversal logic in each actor. A
shared generic sensemaking model would couple actor cognition to the first
supported world, while a separate model request for every actor question would
make richer actors unnecessarily expensive. The current fox supports narrow,
independent LLM questions over one player message, but does not establish an
interface between a simulation-owned world representation and independently
described actor cognition.

**Decision:** For the target class of simulations, use natural human language
as the default semantic intermediary between simulation-owned observation and
actor-owned cognition. The simulation supplies an actor-accessible substate
after deterministically enforcing hard information limits. The actor supplies
an epistemic profile—sensory limitations, knowledge, worldview, biases, and
relevant current context—and actor-owned questions. Generic LLM mediation
combines the substate and profile into a recorded subjective percept, then
answers the actor's questions from that percept.

The engine should group the questions for one percept into one sensemaking
request while retaining each question, answer, and its percept evidence
separately. The subjective percept may be incomplete or distorted and may cause
an actor to form a false belief, but neither percept nor belief becomes
canonical reality. Only a bounded action proposal crosses from actor cognition
to authoritative resolution, and only the simulation core commits an
authoritative transition.

Natural language is a working product assumption rather than a guarantee for
every possible system. Add a structured supplementary or replacement cognition
interface only when evidence from a target simulation shows that language
cannot preserve required precision, cost, latency, or schema independence.

**Consequences:** Simulation and actor implementations can be described and
developed independently across a semantic boundary rather than sharing
schema-specific sensemaking code. Their semantics and bounded action-proposal
contract remain deliberate coupling; natural language does not eliminate those
contracts.

The causal trace must retain the actor-accessible substate,
epistemic-profile input, subjective percept, ordered question set, individual
answers and percept evidence, and controlled model variation needed to explain
and replay the resulting authoritative transition. The first causal-closure
slice must exercise this boundary, but one actor or world schema does not
establish portability. This changes the target product and capability sequence,
not the current verified fox architecture; a future implementation still
requires bounded evidence.

### 2026-07-26: Select village emergency-food rationing for the cross-scale experiment

**Status:** Accepted

**Context:** The next roadmap outcome needs one materially contrasting scenario
before Technical Lead planning can define its domain behavior. The completed
fox-and-hunter slice is a fixed, individual-scale clearing-and-trap scenario;
it cannot supply the new domain facts, claimant information boundaries, or
allocation authority required for a portability test.

**Decision:** Use a bounded village relief-organisation scenario in which the
organisation allocates a fixed emergency food reserve after a supply
disruption. Its user-visible decision is how to distribute the reserve between
household claims. Household information may remain local to the relevant
claimant, while the simulation core owns the canonical inventory and
authoritatively accepts or rejects allocations under explicit allocation rules.

**Consequences:** This supplies the Horizon-3 comparison with a materially
different actor scale, world schema, and system context without implying a
general village-management product. The Technical Lead may now specify the
scenario's observable behavior and bounded corpus, preserving the selected
information and authority boundaries. The experiment remains the test of the
language-default strategy; it does not authorize extraction of a shared
framework from the fox code.

### 2026-07-26: Set the village-rationing experiment policy

**Status:** Accepted

**Context:** Selecting village emergency-food rationing established the
contrasting context but not the actor/core split, information boundary, or
minimal allocation policy needed to make the experiment reproducible. Leaving
those meanings to implementation would let the Technical Lead invent product
policy and could weaken the established authority boundary.

**Decision:** Use two household claimant actors and one relief-organisation
actor. Each household receives only its private household view and submits one
bounded food claim. The organisation receives only the canonical reserve and a
public ledger containing each claim's household identifier, requested units,
and priority tier; it receives neither household's private food situation,
dependants, nor other private household facts. The organisation submits one
bounded allocation proposal. The simulation core, rather than the
organisation, validates the proposal and is the only authority that may commit
the allocation.

The initial corpus has a six-unit reserve; each household requests four units;
and the public ledger ranks the first household at priority tier one and the
second at tier two. The authoritative allocation rule fully serves claims in
ascending priority-tier order until the reserve is exhausted. Thus the unique
valid allocation at six units is four units to the first household and two to
the second. An allocation that exceeds a request or reserve, or differs from
that priority rule, is rejected without changing canonical reserve or
allocations. The required controlled variation changes only the canonical
reserve from six to four units; its unique valid allocation is four units to
the first household and zero to the second. That variation must alter the
organisation's derived observation and authoritative outcome without exposing
any private household facts.

**Consequences:** The Technical Lead is authorized to translate this accepted
policy into Requirements, a bounded experiment packet, fixture corpus, and
behavioral tests. Actor cognition remains separate from authoritative
resolution: a valid proposal is not itself an allocation, and an invalid one
fails closed. This intentionally tests one fixed allocation policy; it does
not establish a generic fairness, eligibility, or village-governance model.

### 2026-07-26: Prioritize builder-controlled composition

**Status:** Accepted

**Context:** The completed causal-closure, shared-world, and contrasting
village-rationing outcomes provide bounded evidence for the actor/simulation-core
authority and semantic boundaries. Their implementations remain fixed,
scenario-local scaffolding. They do not establish that a simulation builder can
independently supply compatible simulation and actor descriptions to a reusable
execution boundary, nor do they establish persistent execution or branching.

The next strategic capability could be an internal temporal runtime,
counterfactual branching over a fixed scenario, further disposable domain
experiments, or a builder-controlled composition boundary.

**Decision:** Prioritize builder-controlled composition. Treat the next product
seam as a semantic protocol among the builder-supplied simulation, the
builder-supplied actors, and the engine that orchestrates and enforces their
exchange. The simulation owns accessible-state derivation, admissible
proposals, authoritative resolution, canonical transitions, and feedback.
Actors own their descriptions, subjective cognition, the bounded proposals they
can form, and proposal selection. For the minimum composition test, the builder
explicitly pairs an actor-declared proposal vocabulary with
simulation-declared accepted proposals; this does not select a universal
proposal representation.

After that boundary is evidenced through one causally complete builder outcome,
extend composed scenarios through stateful shared-world execution and then
causal branching, as maintained in [Strategy](strategy.md#strategic-horizons).

**Alternatives considered:**

- Generalize temporal execution first. This could lock in time, state, and
  conflict semantics before a builder-facing outcome establishes their needs.
- Add branching to a fixed scenario first. This would test branch mechanics
  without establishing independent composition.
- Continue with disposable cross-domain slices. Another slice changes strategy
  only if composition exposes a material failure in the semantic or authority
  boundary.

**Consequences:** The Product Manager must define and order the smallest
builder-visible composition outcome in the [roadmap](roadmap.md). The Technical
Lead may choose the minimum interface and runtime mechanics only after that
outcome defines their required behavior. This decision does not select an API,
schema, transport, event model, authoring syntax, scenario domain, or general
runtime architecture.

### 2026-07-26: Retire superseded boundary-discovery implementations

**Status:** Accepted

**Context:** The causal-turn, fixed fox-and-hunter shared-world, and
village-rationing implementations established bounded evidence for the current
composition and stateful-execution path. They are not runtime dependencies of
that path, yet their code, corpora, tests, requirements, and architecture
descriptions continue to present them as supported behavior. Keeping those
parallel scenario implementations increases maintenance surface and obscures
the builder-facing product boundary. The interactive fox demo remains a
separately supported demonstration and is not part of this retirement.

**Decision:** Retire the three superseded scenario implementations and their
focused tests and YAML corpora. Remove their observable requirements and
current-architecture descriptions. Preserve their evidence records and the
accepted decisions that explain what they established; annotate affected
evidence with its implementation lifecycle. Retain the fox chat, perception,
utility, narration, configuration, and LLM-adapter path as the supported fox
demo.

**Consequences:** The active implementation surface is the builder-controlled
clearing composition and its bounded two-step timeline, plus the interactive
fox demo. PyYAML and the current LLM dependency remain required by that demo.
Future use of a retired scenario requires a new bounded outcome or explicit
restoration decision rather than treating historical code as supported.

### 2026-07-26: Validate the engine through a small clearing game before further platform expansion

**Status:** Accepted

**Context:** The completed composition, two-step execution, and fixed
initial-source comparison support the actor/simulation authority boundary and
causal replay within their bounded clearing fixtures. The resulting
[builder guide](builder-guide.md) remains a developer-facing experiment rather
than evidence that the engine creates player or builder value. In particular,
the fixed comparison does not establish demand for branching or a reason to
generalise temporal, persistence, or authoring machinery.

The next path could continue extracting a domain-neutral platform, deepen
runtime and branch mechanics, or use the existing boundary to create one
complete application. The user prioritised building something fun and
meaningful and postponing capabilities justified only in theory.

**Decision:** Adopt a reversible application-first sequence. Build a small
clearing game in which a player makes bounded interventions, differently
informed actors respond, and the simulation resolves inspectable consequences.
Treat the engine as internal technology during this horizon. Scenario-local
rules, sequencing, content, and presentation are acceptable; add reusable
engine machinery only when the playable outcome cannot be complete without a
named capability.

Restart and replay are sufficient for the first short session. Defer
persistence, arbitrary scheduling, branching, general variation, scenario
editing, plugins, and universal schemas until a demonstrated player or builder
job requires them.

This decision supersedes the capability sequence selected in
[Prioritize builder-controlled composition](#2026-07-26-prioritize-builder-controlled-composition),
not its evidenced component-ownership and authority boundaries. It does not
change the target user or product vision in the README and does not decide that
the game is the final product.

**Alternatives considered:**

- Continue directly toward a builder-facing composition platform. This would
  generalise a boundary before demonstrating that an application built with it
  is useful.
- Generalise temporal execution or branching. The completed bounded slices show
  feasibility but provide no player or builder demand for those capabilities.
- Change the product vision immediately from a builder tool to a game. One
  untested game concept does not justify that irreversible interpretation.

**Consequences:** Strategy now proceeds from a complete playable application,
to player-value evidence, and only then to application-earned reuse. The
roadmap orders one clearing-game delivery outcome and one bounded playtest
decision. Later outcomes remain unordered until that evidence identifies what
players value and whether the game, another application, or a builder product
deserves further investment.

### 2026-07-26: Run the clearing as an autonomous observer simulation

**Status:** Accepted

**Context:** The accepted application-first direction initially assumed that a
player would act as a forest warden and causally intervene in the clearing. The
user subsequently rejected that interaction model. The intended experience is
to observe a simulation in which events occur independently and differently
informed actors react to them.

The application could retain bounded player interventions, play one fixed
scripted history, build a general event framework, or introduce only the
scenario-owned random events needed for one autonomous clearing session.

**Decision:** The immediate application user is an observer, not a causal
participant. A launched session advances to its ending without observer input.
After it ends, the observer may inspect, replay, or restart it, but supplies no
simulation event, actor proposal, rule, random source, or other input that
changes canonical history.

The clearing simulation owns a bounded event vocabulary, the meaning and
effects of each event, and the policy under which an event may occur. Random
selection is controlled variation: the selected event and its causal position
are recorded before the simulation applies an authoritative effect. Actors
receive only their filtered observations and retained context, form bounded
reaction proposals, and remain unable to commit canonical changes. Exact replay
uses the recorded event and authoritative history without fresh selection or
actor mediation.

Use scenario-local event selection and sequencing. Do not infer a general
randomness, scheduling, event, persistence, or branching framework from this
application. A developer or launcher may select the bounded turn limit at
session start as recorded initial configuration; an observer may not select it.

For this first observer delivery, each actor identity owns one fixed question:
the fox asks whether it perceives food worth approaching, and the hunter asks
whether it can prepare or use a trap from what it perceives. Each actor makes
one real-LLM, actor-local call per turn using only its filtered observation and
retained feedback. The LLM answers that fixed question and proposes an action
from the actor's bounded vocabulary. A deterministic validator accepts only
the required structured output and vocabulary; malformed, unavailable, or
out-of-vocabulary output uses the existing observation-derived fallback
proposal. The simulation alone resolves the accepted or fallback proposal and
commits canonical state.

The LLM proposal is an untrusted, recorded actor candidate, not a direct state
transition. This tests whether differently informed actor perspectives make
the clearing readable and causally meaningful while preserving replay: exact
replay consumes the recorded accepted proposal without another model call.

The normal observer surface also makes one real-LLM narration call after each
completed turn. Narration is limited to the recorded causal account and has a
structured fallback. Both actor cognition and narration are retained for
inspection; exact replay consumes those records without another model call.

This decision supersedes the player-intervention and player-agency parts of
[Validate the engine through a small clearing game before further platform
expansion](#2026-07-26-validate-the-engine-through-a-small-clearing-game-before-further-platform-expansion).
It retains that decision's application-first sequencing, platform deferrals,
and conclusion that the README vision has not changed. It also does not alter
the current interactive fox demonstration or its player-message requirements;
that demonstration is not the input model for the new application.

**Alternatives considered:**

- Retain a forest-warden intervention loop. This directly conflicts with the
  accepted observer-only experience.
- Use one fixed scripted event sequence. This would be autonomous but would not
  test whether controlled variation and actor reactions create curiosity across
  fresh runs.
- Design a reusable random-event runtime first. The first observer session
  needs a bounded event source, not a universal event or scheduling model.

**Consequences:** Strategy and roadmap now measure observer value through
curiosity, anticipation, causal comprehension, meaningful consequences, and
interest in replay or another run—not agency, choices, or strategy. The first
delivery must record simulation-owned events and replay them exactly while
keeping all observer controls outside canonical causality. The first delivery
uses real-LLM actor cognition and narration only outside authoritative
proposal, event, and resolution paths; visible fallbacks cannot affect the
recorded session. Later outcomes remain gated by the observer evaluation.
