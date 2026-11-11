"""Verify shared artifact policy, current-session capture and memory loading."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from artifact_policy import redact_text, redact_obj


class ArtifactPolicyTests(unittest.TestCase):
    def test_comment_publishes_sanitized_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            token = 'github_pat_' + 'q' * 50
            review = root / 'review-7.md'
            review.write_text('Review: ' + token)
            gh = root / 'gh'
            gh.write_text('#!/usr/bin/env python3\nimport os,sys,shutil\n'
                          'shutil.copyfile(sys.argv[sys.argv.index("--body-file")+1], os.environ["POSTED_FIXTURE"])\n')
            gh.chmod(0o755)
            posted = root / 'posted.md'
            env = dict(os.environ, PATH=f'{root}:{os.environ["PATH"]}',
                       REPO='acme/widgets', LUFFY_REPLACE_PREVIOUS='0',
                       POSTED_FIXTURE=str(posted))
            subprocess.run(['bash', str(ROOT / 'scripts/post-review-comment.sh'), str(review), '7'],
                           env=env, check=True, capture_output=True)
            self.assertNotIn(token, posted.read_text())
            self.assertIn(token, review.read_text())

    def test_known_credential_formats_and_nested_fields(self):
        values = ['sk-or-v1-' + 'a' * 32, 'ghp_' + 'b' * 36,
                  'github_pat_' + 'c' * 50, 'Bearer private-session-token']
        result = redact_obj({'messages': values, 'api_key': 'custom-short-value'})
        output = json.dumps(result)
        for value in values + ['custom-short-value']:
            self.assertNotIn(value, output)
        self.assertIn('[REDACTED]', output)
        self.assertEqual(redact_text('a normal review of code'), 'a normal review of code')

    def test_trace_and_hub_share_policy_including_trigger_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            token = 'ghp_' + 'x' * 36
            (out / 'review-7.md').write_text('**Verdict:** COMMENT\n' + token)
            env = dict(os.environ, LUFFY_ROOT=str(ROOT), OUT_DIR=td,
                       HERMES_HOME=str(out / 'home'), PR_NUMBER='7',
                       REPO='acme/widgets', LUFFY_STATUS='success',
                       TRIGGER_COMMENT='Bearer private-session-token')
            subprocess.run(['bash', str(ROOT / 'scripts/save-trace.sh')],
                           env=env, check=True, capture_output=True)
            trace = Path((out / 'latest-trace-dir.txt').read_text().strip())
            self.assertNotIn(token, (trace / 'review.md').read_text())
            self.assertNotIn('private-session-token', (trace / 'meta.json').read_text())
            subprocess.run([sys.executable, str(ROOT / 'scripts/build-hub-payload.py')],
                           env=env, check=True, capture_output=True)
            payload = (out / 'hub-payload.json').read_text()
            self.assertNotIn(token, payload)
            self.assertNotIn('private-session-token', payload)


class SessionCaptureTests(unittest.TestCase):
    def capture(self, session_id):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        home = Path(tmp.name)
        out = home / 'out'
        out.mkdir()
        db = sqlite3.connect(home / 'state.db')
        db.execute('CREATE TABLE messages (id INTEGER, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)')
        db.executemany('INSERT INTO messages VALUES (?, ?, ?, ?, ?)', [
            (1, 'old', 'user', 'UNRELATED_PRIVATE_SESSION', ''),
            (2, 'old', 'assistant', 'old answer', ''),
            (3, 'current', 'assistant', 'CURRENT_REVIEW', '')])
        db.commit()
        db.close()
        (home / 'sessions').mkdir()
        (home / 'sessions/old.json').write_text('UNRELATED_PRIVATE_SESSION')
        (home / 'logs').mkdir()
        (home / 'logs/agent.log').write_text('UNRELATED_PRIVATE_SESSION')
        (home / 'logs/errors.log').write_text('UNRELATED_PRIVATE_SESSION')
        (out / 'hermes-run.log').write_text('CURRENT_LOG')
        old_export = out / 'agent-loop/sessions-export'
        old_export.mkdir(parents=True)
        (old_export / 'legacy.json').write_text('UNRELATED_PRIVATE_SESSION')
        (out / 'agent-loop/errors.log').write_text('UNRELATED_PRIVATE_SESSION')
        if session_id:
            (out / 'hermes-usage.json').write_text(json.dumps({'session_id': session_id}))
        env = dict(os.environ, HERMES_HOME=str(home), OUT_DIR=str(out),
                   AGENT_LOOP_DIR=str(out / 'agent-loop'), HERMES_USAGE_FILE=str(out / 'hermes-usage.json'))
        subprocess.run([sys.executable, str(ROOT / 'scripts/capture-hermes-loop.py')],
                       env=env, check=True, capture_output=True)
        text = '\n'.join(p.read_text() for p in (out / 'agent-loop').rglob('*') if p.is_file())
        self.assertNotIn('UNRELATED_PRIVATE_SESSION', text)
        return json.loads((out / 'agent-loop/agent-loop.json').read_text())

    def test_current_session_only_even_when_old_session_is_larger(self):
        captured = self.capture('current')
        self.assertEqual(captured['message_count'], 1)
        self.assertEqual(captured['messages'][0]['content'], 'CURRENT_REVIEW')

    def test_missing_session_id_does_not_guess(self):
        captured = self.capture(None)
        self.assertEqual(captured['message_count'], 0)
        self.assertIn('skipped', captured['capture_warning'])


if __name__ == '__main__':
    unittest.main()
