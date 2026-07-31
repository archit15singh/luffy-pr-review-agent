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

    def _full_contract(self, summary: str = "ok") -> str:
        return (
            "## 🏴‍☠️ Luffy Review — PR #42\n\n"
            "**Verdict:** APPROVE\n"
            "**Confidence:** high\n"
            "**Score:** 92/100\n"
            "**Review effort:** 2/5\n\n"
            f"### Summary\n{summary}\n\n"
            "### Walkthrough\n- change\n\n"
            "### Blocking\n- None\n\n"
            "### Key findings\nNone — no high-confidence defects in new code.\n\n"
            "### Security audit\nNo\n\n"
            "### Suggestions\n- None\n\n"
            "### Code suggestions\nNone\n\n"
            "### Nits\n- None\n\n"
            "### Tests & risk\n"
            "- Relevant tests added/updated: yes\n"
            "- Coverage: unit\n"
            "- Risk: low — small\n"
            "- Rollback: easy\n\n"
            "### What I checked\n- files\n"
        )

    def test_strips_outer_fence(self):
        raw = "```markdown\n" + self._full_contract() + "\n```"
        out = self.run_norm(raw)
        self.assertNotIn("```", out.splitlines()[0])
        self.assertIn("**Verdict:** APPROVE", out)
        self.assertIn("**Score:** 92/100", out)
        self.assertIn("### Security audit", out)
        self.assertIn("<!-- luffy-review pr=42 run=test -->", out)

    def test_repairs_missing_contract(self):
        raw = "looks fine ship it"
        out = self.run_norm(raw)
        self.assertIn("**Verdict:** COMMENT", out)
        self.assertIn("**Score:**", out)
        self.assertIn("### Summary", out)
        self.assertIn("### Security audit", out)
        self.assertIn("looks fine ship it", out)

    def test_truncates_huge(self):
        raw = self._full_contract(summary="x" * 70_000)
        out = self.run_norm(raw)
        self.assertLessEqual(len(out), 60_500)
        self.assertIn("truncated", out.lower())

    def test_accepts_full_structured_contract(self):
        out = self.run_norm(self._full_contract("solid fix with tests"))
        self.assertIn("**Score:** 92/100", out)
        self.assertNotIn("contract repair", out.lower())


if __name__ == "__main__":
    unittest.main()
