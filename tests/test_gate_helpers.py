"""Regression tests for high-ROI gate / sparse helpers."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSOC = ROOT / "scripts" / "association-allowed.sh"
SPARSE = ROOT / "scripts" / "sparse-pr-paths.sh"


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


class AssociationAllowlistTests(unittest.TestCase):
    def test_owner_allowed(self):
        r = _run(["bash", str(ASSOC), "OWNER"])
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_none_denied(self):
        r = _run(["bash", str(ASSOC), "NONE"])
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_first_timer_denied_by_default(self):
        r = _run(["bash", str(ASSOC), "FIRST_TIME_CONTRIBUTOR"])
        self.assertEqual(r.returncode, 1)

    def test_empty_allowlist_allows_all(self):
        r = _run(["bash", str(ASSOC), "NONE", ""])
        self.assertEqual(r.returncode, 0)

    def test_custom_allowlist(self):
        r = _run(["bash", str(ASSOC), "COLLABORATOR", "OWNER,COLLABORATOR"])
        self.assertEqual(r.returncode, 0)
        r = _run(["bash", str(ASSOC), "CONTRIBUTOR", "OWNER,COLLABORATOR"])
        self.assertEqual(r.returncode, 1)

    def test_case_insensitive(self):
        r = _run(["bash", str(ASSOC), "member", "owner,member"])
        self.assertEqual(r.returncode, 0)


class SparseCountRegressionTests(unittest.TestCase):
    """F13: empty path list must count as 0, not '0\\n0'."""

    def test_empty_file_count_is_zero_not_double(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            path = f.name
        try:
            # Broken pattern (historical): COUNT=$(grep -c . f || echo 0)
            # On macOS/GNU grep empty file: prints 0, exit 1 → "0\n0"
            broken = subprocess.check_output(
                ["bash", "-c", f'COUNT=$(grep -c . "{path}" || echo 0); printf %s "$COUNT"'],
                text=True,
            )
            # Fixed pattern
            fixed = subprocess.check_output(
                [
                    "bash",
                    "-c",
                    f'COUNT=$(grep -c . "{path}" 2>/dev/null || true); COUNT=${{COUNT:-0}}; printf %s "$COUNT"',
                ],
                text=True,
            )
            self.assertEqual(fixed, "0")
            # integer compare must work with fixed; broken often is non-integer "0\n0"
            subprocess.check_call(
                ["bash", "-c", f'COUNT=$(printf %s "{fixed}"); [[ "$COUNT" -ge 1 ]] && exit 1 || exit 0']
            )
            if "\n" in broken:
                with self.assertRaises(subprocess.CalledProcessError):
                    subprocess.check_call(
                        [
                            "bash",
                            "-c",
                            f'COUNT=$(grep -c . "{path}" || echo 0); [[ "$COUNT" -ge 1 ]]',
                        ]
                    )
        finally:
            os.unlink(path)

    def test_nonzero_paths_count(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write("/a.py\n/b.py\n")
            path = f.name
        try:
            fixed = subprocess.check_output(
                [
                    "bash",
                    "-c",
                    f'COUNT=$(grep -c . "{path}" 2>/dev/null || true); COUNT=${{COUNT:-0}}; printf %s "$COUNT"',
                ],
                text=True,
            )
            self.assertEqual(fixed, "2")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
