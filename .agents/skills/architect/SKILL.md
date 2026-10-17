---
name: architect
description: "Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. Use for $architect, 'architect this', 'design this', or non-trivial work where jumping to code would lock in the wrong shape."
---

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Synthesize across multiple model perspectives, then fill in code against the chosen sketch.

## Start

Track one entry per phase with a plan tool when available, otherwise a short Markdown checklist.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase A: Ground the problem

Build a real mental model of every system the new code touches. Run the **how** skill over the relevant subsystems. Naming a file isn't grounding. Produce the architectural explanation `how` prescribes. If the design redefines ownership or layering, also run the **why** skill when available, otherwise inspect git history, design docs, and available PR or issue tools for the existing rationale. Treat established rationale as a constraint, and mark gaps rather than guessing.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

## Phase B: Sketch

Run independent design candidates with Codex subagent tools, using the design-sketch task, Phase A grounding artifacts, and `references/runner-prompt.md` as each runner's prompt. Give each candidate its own output directory under `/tmp` and read-only access to the repository. Candidates write sketches only in their assigned output directories.

Use `gpt-6.1-sol` and `gpt-6-astra`, both with `high` reasoning, for the two design perspectives. With `collaboration.spawn_agent`, set `fork_turns: "none"` when selecting these models and provide the workspace, applicable repo instructions, task, and filled-in prompt. Respect the available agent limit. If a model is unavailable, inherit the current model and preserve independence by assigning distinct design approaches. If subagent tools are unavailable, develop the two candidates sequentially.

Design it twice. Require at least two structurally distinct candidates before synthesis, even when the first looks sufficient. This makes the principle of exhausting the design space concrete. Whole-shape alternatives, not point fixes inside one shape.

Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md) before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

After all candidates finish, compare them against the task constraints and the red flags. Use an independent read-only judge on `gpt-6.1-sol` with `high` reasoning when subagent tools are available. Give it the candidates and comparison criteria. Pick a base, adapt worthwhile ideas from the others into one coherent design, and verify the package against the requirements. Record the base, judge's verdict when available, adopted ideas, rejected ideas, and any unavailable models in the rationale's "Synthesis decision" section.

## Phase C: Agree (opt-in)

Default: proceed directly to implementation with the synthesized design. No human checkpoint.

Opt in to a checkpoint when the invoker explicitly asks: "$architect with checkpoint," "stop and show me before implementing," or similar. Then surface the synthesized design and pause for sign-off.

The synthesis can ship as its own commit either way, as a scaffold-first approach. Planned and scoped breakage during fill-in is fine. For adversarial pressure on the design before implementing, run the **interrogate** skill when available, otherwise review the synthesized sketch for unsupported assumptions, failure modes, and requirements it misses.

If the human pushes back on the shape (in a checkpoint or after the fact), treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code, pseudocode with logic. The synthesized sketch is the contract. Deviations from it are signal to surface, not friction to absorb silently. If a function needs a parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out. Don't bolt fixes onto a wrong design, per the **principle-redesign-from-first-principles** and **principle-fix-root-causes** skills.

The signal is a *pattern*, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the implementation.

Use judgment. A few edge cases don't condemn an architecture. Some problems are legitimately complex. Complexity in the data is not complexity in the design.

When you scrap:

1. Re-run the **how** skill over what's been built.
2. Redesign as if the new constraints had been day-one assumptions, per **principle-redesign-from-first-principles**.
3. Subtract before adding. The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and repeat the independent candidate comparison.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the synthesis decision.
