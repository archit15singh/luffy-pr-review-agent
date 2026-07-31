#!/usr/bin/env python3
"""Tests for hub-ingest-run.py and build-hub-payload.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "scripts" / "hub-ingest-run.py"
BUILD = ROOT / "scripts" / "build-hub-payload.py"


class HubIngestTests(unittest.TestCase):
    def test_ingest_writes_memory_tree(self):
        with tempfile.TemporaryDirectory() as td:
            hub = Path(td)
            (hub / "memory" / "repos").mkdir(parents=True)
            payload = {
                "run": {
                    "schema_version": 1,
                    "source_repo": "acme/widgets",
                    "pr_number": "7",
                    "run_id": "123",
                    "run_attempt": "1",
                    "trace_id": "pr7-run123-a1",
                    "model": "openai/gpt-5-mini",
                    "status": "success",
                    "verdict": "REQUEST CHANGES",
                    "review_md": "## Review\n\n**Verdict:** REQUEST CHANGES\n\n### Summary\nok\n",
                    "memory_block": "## Review run pr7-run123-a1\n- Verdict: REQUEST CHANGES\n",
                    "timings": {"total_seconds": 12},
                    "meta": {},
                }
            }
            env = os.environ.copy()
            env["CLIENT_PAYLOAD"] = json.dumps(payload)
            env["HUB_ROOT"] = str(hub)
            subprocess.check_call([sys.executable, str(INGEST)], env=env, cwd=str(hub))
            mem = hub / "memory" / "repos" / "acme--widgets" / "MEMORY.md"
            self.assertTrue(mem.exists())
            self.assertIn("REQUEST CHANGES", mem.read_text())
            run_meta = (
                hub
                / "memory"
                / "repos"
                / "acme--widgets"
                / "runs"
                / "pr7-run123-a1"
                / "meta.json"
            )
            self.assertTrue(run_meta.exists())
            index = hub / "memory" / "index.json"
            self.assertTrue(index.exists())
            self.assertIn("acme--widgets", index.read_text())

    def test_build_payload_redacts_keys(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            (out / "review-1.md").write_text(
                "## R\n\n**Verdict:** COMMENT\n\n### Summary\n"
                "key sk-or-v1-abcdefghijklmnopqrstuvwxyz012345\n\n### Blocking\n- None\n"
            )
            env = os.environ.copy()
            env.update(
                {
                    "OUT_DIR": str(out),
                    "PR_NUMBER": "1",
                    "REPO": "acme/widgets",
                    "GITHUB_RUN_ID": "9",
                    "LUFFY_STATUS": "success",
                    "LUFFY_MODEL": "test-model",
                }
            )
            subprocess.check_call([sys.executable, str(BUILD)], env=env)
            payload = json.loads((out / "hub-payload.json").read_text())
            self.assertEqual(payload["source_repo"], "acme/widgets")
            self.assertNotIn("sk-or-v1-abcdefghij", payload["review_md"])
            self.assertIn("[OPENROUTER_KEY_REDACTED]", payload["review_md"])


if __name__ == "__main__":
    unittest.main()
