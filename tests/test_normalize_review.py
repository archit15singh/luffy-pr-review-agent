#!/usr/bin/env python3
"""Unit tests for normalize-review.py (stdlib only)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "normalize-review.py"


class NormalizeReviewTests(unittest.TestCase):
    def run_norm(self, raw: str, pr: str = "42") -> str:
        with tempfile.TemporaryDirectory() as td:
            inp = Path(td) / "raw.md"
            out = Path(td) / "out.md"
            inp.write_text(raw)
            subprocess.check_call(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(inp),
                    "--output",
                    str(out),
                    "--pr",
                    pr,
                    "--run-id",
                    "test",
                ]
            )
            return out.read_text()

    def test_strips_outer_fence(self):
        raw = "```markdown\n## 🏴‍☠️ Luffy Review — PR #42\n\n**Verdict:** APPROVE\n\n### Summary\nok\n\n### Blocking\n- None\n```"
        out = self.run_norm(raw)
        self.assertNotIn("```", out.splitlines()[0])
        self.assertIn("**Verdict:** APPROVE", out)
        self.assertIn("<!-- luffy-review pr=42 run=test -->", out)

    def test_repairs_missing_contract(self):
        raw = "looks fine ship it"
        out = self.run_norm(raw)
        self.assertIn("**Verdict:** COMMENT", out)
        self.assertIn("### Summary", out)
        self.assertIn("looks fine ship it", out)

    def test_truncates_huge(self):
        raw = (
            "## 🏴‍☠️ Luffy Review — PR #42\n\n**Verdict:** COMMENT\n\n### Summary\n"
            + ("x" * 70_000)
            + "\n\n### Blocking\n- None\n"
        )
        out = self.run_norm(raw)
        self.assertLessEqual(len(out), 60_500)
        self.assertIn("truncated", out.lower())


if __name__ == "__main__":
    unittest.main()
