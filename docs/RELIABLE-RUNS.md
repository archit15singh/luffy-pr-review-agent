# Reliable review runs

## Local workspace

Luffy reads the workspace as well as the diff. Set `WORKSPACE_ROOT` to a clean checkout at the reviewed PR's head commit. The local helper now rejects mismatched or dirty checkouts before invoking the pipeline.

For example, clone the target repository into a separate temporary directory, run `gh pr checkout <number> --repo <owner/repo>` inside it, and invoke:

```sh
WORKSPACE_ROOT=/absolute/path/to/pr-checkout \
LUFFY_HUB_PUBLISH=0 POST_COMMENT=0 \
  ./scripts/review-local.sh owner/repo 123
```

Run the command from the Luffy checkout. Configure `OPENROUTER_API_KEY` in its ignored `.env` file; never commit it. With the flags above, the helper does not post a review or publish hub memory. Terminal tools still execute locally: use an isolated environment appropriate to the repository's trust level. The commit check is a correctness check, not a sandbox.

## Failure semantics

- Diff-download errors stop context assembly before a model is called.
- Hermes errors and empty responses return a nonzero status. A failure report remains available, while partial model output stays in the raw trace.
- Failed reviews are not distilled into successful-review memory.
- Reused output directories discard previous run artifacts before execution. Local trace IDs are unique, preserving prior trace directories rather than mixing runs.

Do not run concurrent reviews with the same `OUT_DIR` or `HERMES_HOME`.

## Verification recorded 12 November 2026

The existing checkout is `/Users/singh/projects/luffy-pr-review-agent`. A live provider run was skipped at the owner's request after the missing local OpenRouter key was identified. A Hermes installation was started and interrupted; no live model review, review comment or hub-memory publish was performed. Model quality, current CLI compatibility and paid provider behavior remain unverified.

The ten process-boundary regression scenarios use a fixture Hermes executable and fixture GitHub responses. Eight fail against the preceding implementation; all ten pass after the corrections. The positive review cases pass before and after. These tests exercise the real shell entry points, normalization, orchestration, memory distillation, trace creation and local workspace gates without claiming a live model result. Together with the existing tests, the suite has 24 passing tests. CI runs these tests and syntax-checks every shell script on PRs and main.

Selected by impact versus change size: truthful failure status first, complete diff context second, correct local workspace third. UI redesign, model migration and broader review-quality evaluation are deferred until a credential-backed run supplies evidence.
