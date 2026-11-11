"""Memory composition stays bounded and stable across reloads."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_snapshot import compose


class MemorySnapshotTests(unittest.TestCase):
    def test_repeated_preload_is_idempotent_and_keeps_local_notes(self):
        hub = '# Hub\n\nRepository notes.\n\n## Review one\n- First finding\n'
        local = '# Local\n\nUnpublished note.\n\n## Review two\n- Local finding\n'
        first = compose(hub, local, 1000)
        for _ in range(20):
            self.assertEqual(compose(hub, first, 1000), first)
        self.assertEqual(first.count('## Review one'), 1)
        self.assertIn('Unpublished note.', first)
        self.assertIn('## Review two', first)

    def test_snapshot_is_bounded_and_valid_utf8(self):
        text = compose('## Old\n' + 'x' * 3000, '## Recent\n' + '猫' * 100, 200)
        self.assertLessEqual(len(text.encode()), 200)
        text.encode().decode('utf-8')

    def test_truncated_snapshot_remains_idempotent(self):
        hub = '# Hub\n\n## First\n' + 'x' * 500 + '\n\n## Recent\n' + 'y' * 60
        first = compose(hub, '', 120)
        self.assertEqual(compose(hub, first, 120), first)

    def test_changed_hub_does_not_duplicate_existing_record(self):
        old = compose('## A\none', '## B\ntwo', 1000)
        updated = compose('## A\none\n\n## C\nthree', old, 1000)
        self.assertEqual(updated.count('## A'), 1)
        self.assertIn('## B', updated)
        self.assertIn('## C', updated)
        self.assertEqual(compose('## A\none\n\n## C\nthree', updated, 1000), updated)


if __name__ == "__main__":
    unittest.main()
