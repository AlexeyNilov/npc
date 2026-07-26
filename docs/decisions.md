# Decisions

This document owns consequential choices and their rationale.

### 2026-07-25: Keep LLM perception separate from fox authority

**Status:** Accepted

**Context:** The verified fox loop uses LLM-backed threat and food-offer
perceptions. The model can propose a player-text fact and cite player text, but
it cannot be allowed to choose whether the fox flees, approaches, or does
nothing.

**Decision:** Treat each fox perception as an untrusted sensor. It emits only
its boolean result, `certainty`, and player-text evidence. Deterministic
validation accepts a finite in-range certainty and grounds a `true` answer in
the player message. The fox-local policy alone maps accepted perceptions to
action; false or rejected results do nothing. Certainty is trace-only.

**Consequences:** The sensors remain narrow functions, not a registry or
generic actor framework. A later abstraction needs new evidence from a
materially different capability or creature policy.

### 2026-07-25: Render completed actor outcomes with a non-authoritative LLM narrator

**Status:** Accepted

**Context:** In the text-based actor reality, the player needs a textual account
of what the fox did. The completed closed rendering experiment preserves the
authority boundary, but its two preapproved sentences and fixture renderer do
not exercise an LLM narrator.

**Decision:** After deterministic perception, choice, action execution, and
feedback are complete, use the configured LLM to narrate the completed action
for the player. The narrator receives only the completed event data required to
describe that action. Its response is presentation data: it cannot choose or
change an action, distance, outcome, or feedback, and it never becomes
canonical world state or input to a later turn. An unavailable or unusable
response has a deterministic fallback. Arbitrary concise narration is allowed
to keep the implementation small and the player experience expressive, rather
than structurally rejecting every claim beyond the completed action.

**Consequences:** The configured-model boundary is verified. Free-form flavour
may still be misleading or false to a player even though it cannot alter
canonical state; this is an accepted residual risk. The action-only input,
instruction to best-effort narrate only the completed action and avoid
unsupported claims, explicit `Narration (non-authoritative)` presentation
label, response-length limit, deterministic fallback, and retained trace
mitigate it without enforcing factual accuracy. If player trust remains a
demonstrated problem, revisit claim validation or a more constrained
presentation.

### 2026-07-25: Preserve experiment evidence independently of implementation

**Status:** Accepted

**Context:** The project deliberately removes unsuccessful scaffolding, but
without a durable record its observations are compressed into later decisions
or lost. That encourages re-running the same work and makes roadmap choices
look like implementation preferences rather than evidence-led bets.

**Decision:** Keep one concise experiment-evidence record for every bounded
experiment. The record owns what the experiment demonstrated or refuted;
requirements, architecture, roadmap, and decisions retain their existing,
separate ownership.

**Consequences:** Removing code does not remove its learning. A small
documentation step is required before an experiment starts and when it is
reviewed.

### 2026-07-25: Use YAML scenarios for fixed corpora

**Status:** Accepted

**Context:** The fixed creature corpora need checked-in, human-readable,
reproducible inputs. Python's standard library does not parse YAML.

**Decision:** Store the initial experiment scenario in YAML and use PyYAML to
load it.

**Consequences:** PyYAML is the only current runtime dependency because the fox
feedback and outcome-rendering corpora use YAML.

### 2026-07-26: Test deterministic utility selection before behavioural randomness

**Status:** Accepted

**Context:** The fox currently resolves its independently validated threat and
food-offer perceptions through a fixed threat-first policy. The next learning
goal is to determine whether the authoritative-loop pattern supports a real
conflict between safety and food-seeking. Random action variation would not
answer that question and would make the initial policy evidence less direct.

**Decision:** Run the next experiment as a fox-local deterministic utility
policy with a persistent authoritative need state. The policy will score
existing candidate actions from authoritative state and accepted perceptions;
the LLM remains a narrow, evidence-grounded perception source. Do not add
randomness in this experiment.

**Consequences:** The experiment must make policy inputs, utility results,
selection, and state transitions explainable and replayable. It tests an
explicit intent stage without authorizing an actor framework, generic utility
system, or stochastic action selection. Randomness may be reconsidered only
after this deterministic experiment yields evidence about the policy.

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
