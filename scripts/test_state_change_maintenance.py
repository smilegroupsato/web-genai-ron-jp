"""Negative tests for the narrowly scoped legacy maintenance gate."""
import subprocess
import unittest
from pathlib import Path
from maintain_state_change_metadata import ROOT, TARGETS, transform_html, transform_markdown, validate_changes


class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = {p: subprocess.check_output(['git', 'show', '054e6135e20df02019a3483f0f9d56db6707543b:' + p], cwd=ROOT).decode('utf-8') for p in TARGETS}
        cls.after = {p: (transform_html if p.startswith('site/') else transform_markdown)(v, Path(p).stem) for p,v in cls.before.items()}

    def test_permitted_change_and_idempotence(self):
        validate_changes(list(TARGETS), self.before.__getitem__, self.after.__getitem__)
        for p,value in self.after.items():
            self.assertEqual(value, (transform_html if p.startswith('site/') else transform_markdown)(value, Path(p).stem))

    def test_body_rewrite_rejected(self):
        changed = dict(self.after)
        p = 'site/article/state-change/chapter-02.html'
        changed[p] = changed[p].replace('完成された実証研究ではない', '完成された実証研究である')
        self.assertNotEqual(changed[p], self.after[p])
        with self.assertRaisesRegex(ValueError, 'Not the permitted'):
            validate_changes(list(TARGETS), self.before.__getitem__, changed.__getitem__)

    def test_extra_site_file_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unrelated'):
            validate_changes([*TARGETS, 'site/index.html'], self.before.__getitem__, self.after.__getitem__)

    def test_wrong_canonical_rejected(self):
        changed = dict(self.after)
        p = 'site/article/state-change/chapter-05.html'
        changed[p] = changed[p].replace('https://genai-ron.jp/article/state-change/chapter-05.html', 'https://example.org/')
        with self.assertRaisesRegex(ValueError, 'Not the permitted'):
            validate_changes(list(TARGETS), self.before.__getitem__, changed.__getitem__)


if __name__ == '__main__':
    unittest.main()
