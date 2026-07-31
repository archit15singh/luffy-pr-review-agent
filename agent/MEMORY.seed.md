# Luffy review memory (seed)

## Review craft
- Focus findings on **new code** introduced by the PR; require a concrete trigger scenario.
- Bugs/security: thorough. Style/nits: high bar or omit.
- Prefer silence over low-confidence guesses unless impact is high (data loss, security, money).
- Always fill: Score, Review effort, Security audit, Relevant tests, Key findings.
- Cite `path` / `symbol`; never dump secrets from the workspace.

## Domain notes
- Monorepos: sparse checkout may hide unrelated modules — do not invent missing symbols.
- Diff may be size-truncated; state that under What I checked and lower confidence when needed.
