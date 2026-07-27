# Agent Workflow

This document governs bounded implementation work. It does not apply to ordinary
discussion, review, or read-only exploration. For the information map, see
[Information Flow](information-flow.md).

## Control plane

The [Vision-to-Roadmap role](agent_roles/product_strategist.md),
[Product Manager](agent_roles/product_manager.md), and
[Technical Lead](agent_roles/technical_lead.md) operate outside the
implementation loop. The Vision-to-Roadmap role turns the vision into a
dependency-ordered recommendation for concrete product outcomes. The Product
Manager evaluates that recommendation against evidence and maintains the
ordered roadmap. The Technical Lead turns an agreed outcome into the smallest
verifiable technical path, integrates accepted work, and records only changed
durable facts.

Use a task packet only for delegated, risky, experimental, or multi-step work.
The Technical Lead may implement a localized, verifiable change directly when a
packet would add no value.

## Enter the implementation loop

For a packet, select one delivery role and read only its guide and the packet's
named context.

| Work | Delivery role |
| --- | --- |
| Bounded read-only discovery | [Explorer](agent_roles/explorer.md) |
| Code, tests, configuration, or documentation implementation | [Implementer](agent_roles/implementer.md) |
| Review of a qualifying packet or diff | [Simplifier](agent_roles/simplifier.md) |

Use the Simplifier only when the work adds a file, dependency, abstraction,
helper, public boundary, cross-module change, or unresolved design choice.

## Make work Ready

Before a packet enters delivery, the Technical Lead confirms:

- one observable outcome, write scope, verification, and stop condition;
- a concept-provenance audit when the work adds or changes domain information,
  with every new semantic element traced to an accepted source or a named
  blocking decision;
- a terminology plan when the work introduces, changes, or reuses an ambiguous
  project-specific term across a boundary, with its glossary entry or an
  explicit packet-local/disposable classification;
- the relevant canonical context and any durable-information impact;
- an experiment record and decision unlocked, if this is an experiment;
- a second scenario or a scaffolding label, if the work claims reuse; and
- a discovery outcome rather than implementation, if a material product or
  technical choice remains unresolved.

The [task template](tasks/TEMPLATE.md) holds the details. A roadmap outcome is a
priority signal, not a Ready task.

## Lifecycle

1. **Planned:** dependencies or decisions remain unresolved.
2. **Ready:** outcome, context, write scope, verification, and stop conditions are complete.
3. **In progress:** one owner is executing the task.
4. **Review:** execution and task-local verification are complete. The
   experiment record contains its observed result and is marked `Review`; the
   Technical Lead obtains any required Simplifier review and resolves its
   findings.
5. **Blocked:** a named design or external condition prevents progress.
6. **Done:** findings are resolved, the Technical Lead has reconciled the
   durable records, and accepted the result.

Only the Technical Lead marks Ready or Done. A delivery role may move Ready work
to In progress, then Review or Blocked. The [task registry](tasks/STATUS.md) contains
only open packets; remove Done packets after integration because Git owns history.

## Delegation

- Create a packet from the [task template](tasks/TEMPLATE.md) before delegated
  execution.
- Give each worker one role, one packet, exact context references, write scope,
  verification, and stop conditions.
- Use at most one write-enabled worker in a shared worktree.
- Independent read-only work may run concurrently when evidence scopes do not
  overlap a writer's uncommitted output.
- Workers do not commit, push, expose secrets, perform unapproved external
  mutations, or decide unresolved product or authority questions.
- Do not delegate localized work merely to create another workflow stage.

## Handoff

Return:

- status and concise outcome;
- files changed and ownership impact;
- test-first evidence and exact verification results;
- assumptions, deviations, security or interface risks;
- unresolved questions and recommended next action.

Raw logs remain outside durable documents. The Technical Lead inspects the actual
diff, resolves findings, runs final checks, and integrates only accepted work.

### Review and roadmap closure

The Technical Lead owns the sequence from Review to Done. For an experiment
that requires Simplifier review, the Technical Lead obtains that review and
resolves its findings. It then marks the exact completed roadmap outcome
`Completed`, finalizes the evidence record, and marks the task Done. It does not add,
replace, or reorder roadmap outcomes.

The Product Manager consumes finalized evidence during normal planning and may
add or reorder future outcomes then. Product planning is not a completion gate:
the Product Manager does not accept implementation, review a diff, arrange
Simplifier review, or change task or evidence lifecycle status.

### Completion reconciliation

Before marking an experiment or delivery Done, the Technical Lead confirms:

- any required Simplifier review is complete and its findings are resolved;
- any required evidence record has its final status and result;
- accepted behavior and verified mechanism are routed to Requirements and
  Architecture, while unresolved problems are routed to an issue record;
- the exact completed outcome is marked `Completed` in the roadmap, and any
  evidence record reflects that completed status;
- modified Markdown links are checked, with any pre-existing repository-wide
  link failures recorded as issues rather than ignored; and
- the final diff passes the repository's required verification.
