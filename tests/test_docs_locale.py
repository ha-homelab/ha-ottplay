"""Non-ASCII documentation remains checkable under an ASCII Python locale."""

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationLocaleTests(unittest.TestCase):
    def test_documentation_checker_in_ascii_locale(self):
        env = os.environ.copy()
        env.update(LC_ALL="C", PYTHONUTF8="0", PYTHONCOERCECLOCALE="0")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/check_readme_translations.py")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
