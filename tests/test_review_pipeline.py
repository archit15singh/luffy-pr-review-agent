"""Exercise real shell entry points with isolated process-boundary fixtures.

These tests do not call a model, GitHub, or publish comments/hub memory.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.bin = self.home / 'bin'
        self.bin.mkdir()
        self.out = self.home / 'out'
        self.out.mkdir()
        self.env = dict(os.environ, PATH=f'{self.bin}:{os.environ["PATH"]}',
                        LUFFY_ROOT=str(ROOT), OUT_DIR=str(self.out),
                        HERMES_HOME=str(self.home / 'hermes'),
                        WORKSPACE_ROOT=str(self.home), REPO='acme/widgets',
                        PR_NUMBER='7', OPENROUTER_API_KEY='fixture-only',
                        LUFFY_HUB_PUBLISH='0', GH_TOKEN='fixture-only')

    def binary(self, name, body):
        path = self.bin / name
        path.write_text('#!/usr/bin/env bash\n' + body + '\n')
        path.chmod(0o755)

    def run_script(self, name, *args):
        return subprocess.run(['bash', str(ROOT / 'scripts' / name), *args],
                              env=self.env, capture_output=True, text=True)

    def model(self, mode):
        self.binary('hermes', '''
if [[ "$1" == "--version" ]]; then echo fixture; exit 0; fi
case "${FIXTURE_MODE}" in
  failed) echo "provider unavailable" >&2; exit 23 ;;
  partial) echo "partial response"; exit 23 ;;
  empty) exit 0 ;;
  success) printf '## Review\n\n**Verdict:** COMMENT\n\n### Summary\nFixture review.\n'; exit 0 ;;
esac
''')
        self.env['FIXTURE_MODE'] = mode
        (self.out / 'prompt.md').write_text('Review the fixture.')

    def test_model_failure_survives_normalization(self):
        self.model('failed')
        result = self.run_script('run-hermes-review.sh')
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertIn('failed to produce a review', (self.out / 'review-7.md').read_text())

    def test_empty_model_response_is_failure(self):
        self.model('empty')
        result = self.run_script('run-hermes-review.sh')
        self.assertNotEqual(result.returncode, 0, result.stderr)

    def test_partial_response_with_error_is_failure(self):
        self.model('partial')
        result = self.run_script('run-hermes-review.sh')
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertIn('Partial output', (self.out / 'review-7.md').read_text())

    def test_model_success_retains_review_artifact(self):
        self.model('success')
        result = self.run_script('run-hermes-review.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Fixture review.', (self.out / 'review-7.md').read_text())

    def failing_diff(self):
        self.binary('gh', '''
if [[ "$2" == "view" ]]; then
  echo '{"number":7,"title":"fixture","files":[]}'
else
  echo 'partial diff'; exit 9
fi
''')

    def test_diff_failure_stops_context_assembly(self):
        self.failing_diff()
        result = self.run_script('assemble-context.sh')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.out / 'prompt.md').exists())
        self.assertFalse((self.out / 'pr.diff').exists())

    def test_failed_rerun_cannot_publish_old_review_or_usage(self):
        self.failing_diff()
        self.binary('curl', 'printf 404')
        for name in ['review-7.md', 'review-7.raw.md', 'meta.env',
                     'hermes-usage.json', 'latest-trace-dir.txt']:
            (self.out / name).write_text('STALE_SUCCESS')
        loop = self.out / 'agent-loop'
        loop.mkdir()
        (loop / 'agent-loop.json').write_text('STALE_SUCCESS')
        result = self.run_script('run-luffy-review.sh')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('LUFFY_STATUS=failed', result.stdout)
        review = (self.out / 'review-7.md').read_text()
        self.assertNotIn('STALE_SUCCESS', review)
        trace = Path((self.out / 'latest-trace-dir.txt').read_text().strip())
        self.assertEqual(json.loads((trace / 'meta.json').read_text())['status'], 'failed')
        self.assertFalse((trace / 'hermes-usage.json').exists())
        self.assertFalse((trace / 'agent-loop').exists())
        self.assertFalse((self.home / 'hermes/memories/MEMORY.md').exists())

    def test_local_helper_rejects_wrong_checkout(self):
        self.binary('gh', 'echo expected-pr-head')
        self.binary('git', 'echo another-head')
        result = self.run_script('review-local.sh', 'acme/widgets', '7')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('does not match', result.stderr)
        self.assertFalse((self.out / 'prompt.md').exists())

    def test_orchestrator_success_writes_memory_and_verifiable_trace(self):
        self.model('success')
        self.binary('curl', 'printf 404')
        self.binary('gh', '''
if [[ "$2" == "view" ]]; then
  echo '{"number":7,"title":"fixture","files":[{"path":"example.py","additions":1,"deletions":0}]}'
else
  printf 'diff --git a/example.py b/example.py\n+print(42)\n'
fi
''')
        result = self.run_script('run-luffy-review.sh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('LUFFY_STATUS=success', result.stdout)
        memory = (self.home / 'hermes/memories/MEMORY.md').read_text()
        self.assertIn('acme/widgets PR #7', memory)
        trace = Path((self.out / 'latest-trace-dir.txt').read_text().strip())
        self.assertEqual(json.loads((trace / 'meta.json').read_text())['status'], 'success')
        self.assertIn('Fixture review.', (trace / 'review.md').read_text())
        self.assertTrue((trace / 'trace.json').is_file())

    def test_local_helper_rejects_dirty_pr_head(self):
        self.binary('gh', 'echo expected-pr-head')
        self.binary('git', '''
if [[ "$3" == "rev-parse" ]]; then echo expected-pr-head
else echo ' M changed.py'; fi
''')
        result = self.run_script('review-local.sh', 'acme/widgets', '7')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('must be clean', result.stderr)

    def test_local_traces_have_distinct_run_ids(self):
        self.env.pop('GITHUB_RUN_ID', None)
        result = self.run_script('save-trace.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        first = (self.out / 'latest-trace-dir.txt').read_text()
        result = self.run_script('save-trace.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        second = (self.out / 'latest-trace-dir.txt').read_text()
        self.assertNotEqual(first, second)
        self.assertTrue(Path(first.strip()).is_dir())
        self.assertTrue(Path(second.strip()).is_dir())


if __name__ == '__main__':
    unittest.main()
