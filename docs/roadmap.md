# Roadmap

This document owns incomplete future outcomes.

## Product frame

**Target user:** the project's developer, initially playing with a D&D/RPG-style
trader through a simple chat interface.

**Problem:** there is not yet evidence that a simulated actor can make
autonomous, repeatable economic and social choices that stay engaging in a
conversation. The first trader slices now exist, but the observed playtest
shows that the chat can invent a trade, describe a refused trade as successful,
and contradict authoritative state.

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

**Assumptions to test**

- The smallest meaningful demonstration is one trader and one player rather
  than a general multi-actor simulation.
- Visible consequences of state and past interaction will make the trader feel
  more autonomous than a prompt-only chat character.
- A small, deterministic economic decision model can create useful learning
  only if the conversational boundary cannot invent or misrepresent its state
  transitions.

The ordering below is a recommendation based on these assumptions. It is not a
commitment to dates, scope beyond the listed slices, or product priorities not
yet supplied by the user.

## Ordered future outcomes

### 6. Evaluate LangExtract for grounded trade extraction

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

### 7. Re-run the bounded trader playtest

**Outcome:** the developer can conduct a small, repeatable chat playtest where
the trader's trade behaviour and visible state remain consistent across
non-trade conversation, an accepted offer, a follow-up refusal, and an
unsupported demand.

**Hypothesis:** the repaired conversation contract and grounded outcome layer
will make the trader's autonomy observable without relying on hidden traces to
correct the player-facing dialogue.

**Smallest test:** run a scripted four-part session covering the cases above,
then repeat the same session. Retain decision traces as diagnostic evidence,
but assess the player-visible dialogue independently.

**Support signal / pass criterion:** no player-visible claim conflicts with
authoritative state or the trace, no unsolicited trade occurs, and the two runs
produce the same authoritative state transitions. A trace is not a substitute
for a correct player-facing response.

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

## Recommended next outcome

Start with **Outcome 4: establish an authoritative conversation contract**.
The playtest already shows unauthorized state changes, so state-grounded
narration alone would make incorrect transactions more believable rather than
preventing them. The critical assumption is that explicit intent recognition
can contain the transaction boundary; its success signal is that only the
single supported offer shape changes authoritative state.
