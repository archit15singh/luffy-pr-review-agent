# Luffy central memory

This directory is the **hub** for review memory across every target repository that runs Luffy.

## Layout

```text
memory/
  repos/
    {owner}--{repo}/
      MEMORY.md                 # cumulative learned notes for that repo
      runs/
        {trace_id}/
          meta.json             # run identity + hashes
          review.md             # Luffy review body (may be truncated)
          summary.md            # short distill block
```

## How it gets updated

1. A **target repo** finishes a Luffy review and builds a redacted payload from the run trace.
2. It fires `repository_dispatch` (`luffy-run`) on **this** repo using `LUFFY_HUB_TOKEN` (or `GITHUB_TOKEN` when Luffy is reviewing itself).
3. Workflow **Ingest Luffy Run** (`.github/workflows/ingest-luffy-run.yml`) commits updates under `memory/repos/…`.

## Secrets (target repos)

| Secret | Purpose |
|--------|---------|
| `LUFFY_HUB_TOKEN` | PAT or fine-grained token with `contents: write` + ability to create `repository_dispatch` on `archit15singh/luffy-pr-review-agent` |

Optional vars:

| Variable | Default | Purpose |
|----------|---------|---------|
| `LUFFY_HUB_REPO` | `archit15singh/luffy-pr-review-agent` | Hub repository |
