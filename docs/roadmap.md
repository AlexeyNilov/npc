# Roadmap

This document owns incomplete future outcomes.

## Product frame

**Target user:** the project's developer, initially playing with a D&D/RPG-style
trader through a simple chat interface.

**Problem:** there is not yet evidence that a simulated actor can make
autonomous, repeatable economic and social choices that stay engaging in a
conversation. The current repository provides local-LLM chat connectivity, but
no actor or simulation behaviour.

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

**Assumptions to test**

- The smallest meaningful demonstration is one trader and one player rather
  than a general multi-actor simulation.
- Visible consequences of state and past interaction will make the trader feel
  more autonomous than a prompt-only chat character.
- A small, deterministic economic decision model is enough to create useful
  learning before broader actor modelling is attempted.

The ordering below is a recommendation based on these assumptions. It is not a
commitment to dates, scope beyond the listed slices, or product priorities not
yet supplied by the user.

## Ordered future outcomes

### 3. Run a stateful conversational trader playtest

**Outcome:** a developer can meet the trader in a simple chat interface, discuss
or propose the supported trades in natural language, and observe responses that
reflect the authoritative state and relevant prior interaction.

**Hypothesis:** connecting deterministic decisions to natural-language
interaction produces a more engaging experience than a static chat character.

**Smallest test:** conduct and record several hands-on sessions using the same
scripted scenario; include a repeated proposal or follow-up that depends on an
earlier interaction.

**Support signal / pass criterion:** the developer can identify a material,
state- or history-dependent difference in the trader's behaviour during each
session, and can reproduce the underlying decision path. If the dialogue can
be substituted with a fixed prompt without changing observed behaviour, the
hypothesis is not supported.

**Constraint:** language-model output may express or interpret a proposal, but
the authoritative state transition and final trader choice must remain
deterministic.

### 4. Decide whether to deepen the actor loop or broaden the model

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
