# Roadmap

This document owns incomplete future outcomes.

## Product frame

**Target user:** the project's developer, initially playing with a D&D/RPG-style
trader through a simple chat interface.

**Problem:** there is not yet evidence that a simulated actor can make
autonomous, repeatable economic and social choices that stay engaging in a
conversation. The first trader slices now exist, but the observed playtest
shows two risks: unconstrained chat can invent or misrepresent a trade, while
the safety repair has made ordinary social conversation repetitive. The current
trader-specific contract also does not yet demonstrate a reusable NPC model.

**Desired outcome:** a developer can run repeatable play sessions with one
trader whose inventory, funds, goals, relevant history, and choices affect the
conversation and a proposed deal. The trader may decline a deal for reasons
consistent with its interests.

**Constraints already evidenced:** core actor decisions must remain
deterministic; LLMs may assist with extraction, narration, or proposals but
must not authoritatively change actor state or choose the final action.

## Evidence and assumptions

**Evidence**

- The README names a self-directed D&D/RPG trader as the first demonstration
  and hands-on play/observation as the initial engagement evaluation.
- A sample program can stream a conversation with a configured local LLM.
- The proposed determinism decision sets the boundary for authoritative actor
  decisions.
- The reported trader playtest contains a valid, traced purchase that leaves
  the trader with 26 gold, followed by narration that it has 30 gold.
- In that playtest, a question about buying caused a herb sale without the
  player offering the herb or a price; later narration claimed trades succeeded
  although the traces recorded `player_has_no_healing_herb`.
- An unsupported demand to surrender gold was narrated as fulfilled without a
  corresponding authoritative state change.
- The repaired playtest renders ordinary social messages through four fixed
  atmospheric clauses; a greeting and a name question each produced the same
  reply.
- The current transaction contract, validation, state model, and rendering are
  all specific to buying one healing herb for gold from a trader.

**Assumptions to test**

- The smallest meaningful demonstration is one trader and one player rather
  than a general multi-actor simulation.
- Visible consequences of state and past interaction will make the trader feel
  more autonomous than a prompt-only chat character.
- A small, deterministic economic decision model can create useful learning
  only if the conversational boundary cannot invent or misrepresent its state
  transitions.
- A small reusable authority boundary can support more than one actor
  capability without requiring its core behavior to be rewritten for each one.

The ordering below is a recommendation based on these assumptions. It is not a
commitment to dates, scope beyond the listed slices, or product priorities not
yet supplied by the user.

## Ordered future outcomes

### 6. Test a reusable authoritative-action boundary

**Outcome:** obtain evidence that the actor interaction model can support two
materially different, bounded capabilities without changing its common
authority flow. One capability may be the existing trader purchase; the other
must be a non-economic, state-grounded interaction such as identifying the
actor or answering a question about an authoritative fact.

**Hypothesis:** the reusable part of an NPC system is the authority flow—not a
universal trade grammar or a set of trader templates. A generic flow can accept
an untrusted interpretation, validate evidence against a capability contract,
produce an authoritative result, and render an outcome for both capabilities.

**Smallest test:** define the two capability contracts and run a fixed corpus
of supported and unsupported messages for each. Confirm that each contract
owns its own facts, evidence rules, and possible outcomes, while both use the
same authority flow and traces.

**Support signal / pass criterion:** both capabilities preserve their stated
authority and state rules; an unsupported message changes no state; and adding
the second capability does not require changing the common authority flow or
the first capability's contract. If it does, identify the coupling rather than
generalizing further.

**Scope guard:** this is not a commitment to a universal NPC DSL, a multi-actor
world, or open-ended dialogue. Do not add more capabilities until the result
shows which concepts are genuinely shared.

### 7. Re-run the bounded trader playtest

**Outcome:** the developer can conduct a small, repeatable chat playtest where
the trader responds distinctly and correctly to basic social questions, while
its trade behaviour and visible state remain consistent across an accepted
offer, a follow-up refusal, and an unsupported demand.

**Hypothesis:** the reusable boundary and a bounded set of state-grounded
social capabilities will make the trader's autonomy observable without relying
on hidden traces to correct the player-facing dialogue.

**Smallest test:** run and repeat a scripted session containing a greeting, a
name or fact question, an accepted offer, a follow-up refusal, and an
unsupported demand. Retain decision traces as diagnostic evidence, but assess
the player-visible dialogue independently.

**Support signal / pass criterion:** the basic social questions receive
meaningfully distinct, authoritative responses; no player-visible claim
conflicts with state or the trace; no unsolicited trade occurs; and the two
runs produce the same authoritative state transitions. A trace is not a
substitute for a correct player-facing response.

### 8. Decide whether to deepen the actor loop or broaden the model

**Outcome:** use the playtest evidence to make an explicit next product choice:
improve the trader's perception, sensemaking, intent, action, outcome, and
feedback loop; repeat the trader experiment with a changed hypothesis; or
explore a second actor scale.

**Hypothesis:** play evidence will reveal the smallest missing capability that
limits perceived autonomy or reproducibility.

**Smallest test:** review recorded play sessions and decision traces against the
outcomes above; list each observed limitation, the evidence for it, and one
minimal experiment that could address it.

**Support signal / pass criterion:** a next experiment can be selected from
observed evidence with a falsifiable success signal. If no limitation is
observable, repeat or strengthen the playtest rather than expanding scope.

### 9. Evaluate LangExtract for grounded trade extraction

**Outcome:** obtain reproducible evidence on whether
[LangExtract](https://github.com/google/langextract) can improve varied
natural-language trade extraction while preserving the authoritative
conversation contract. This is an evaluation milestone, not a commitment to
add LangExtract to the runtime.

**Hypothesis:** LangExtract's schema-guided extraction and source character
intervals can increase recognition of explicitly supported offers without
increasing inferred transactions, compared with the current untrusted
extraction plus deterministic validator.

**Smallest test:** build a fixed, checked-in corpus containing the supported
offer shape with varied filler, the existing non-offer cases, and the reported
playtest sequence. Run both extractors against it using the configured local
model path where possible. For every LangExtract result, verify its spans map
to the original message, then pass only its normalized candidate through the
same deterministic validator; record recognition, rejection reason, and
latency.

**Support signal / pass criterion:** LangExtract recognizes at least the
baseline's valid supported offers, produces no validator-accepted transaction
for a non-offer, and every field used by an accepted candidate has a valid
source span. If it cannot operate through the configured local model boundary,
or increases false positives, retain the existing extractor and record the
evidence.

**Scope guard:** do not replace the deterministic validator, change the
economic evaluator, or add LangExtract to the live playtest during this
milestone. Do not use cloud credentials merely to complete the comparison.

## Recommended next outcome

Start with **Outcome 6: test a reusable authoritative-action boundary**. The
current safety mechanisms have proven valuable, but their trader-specific form
is not evidence for a generic NPC engine. The critical assumption is that two
bounded capabilities can share one authority flow while retaining separate
contracts; the success signal is that adding the second capability does not
change the flow or weaken either capability's safety guarantees.
