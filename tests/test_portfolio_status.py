"""Tests for the portfolio status generator."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.portfolio_status import (
    classify_completion_band,
    classify_target_track,
    collect_repo_status,
    parse_open_roadmap_items,
)


class PortfolioStatusTests(unittest.TestCase):
    def test_parse_open_roadmap_items(self) -> None:
        text = """
## Phase
- [x] done
- [ ] first gap
- [ ] second gap
"""
        self.assertEqual(parse_open_roadmap_items(text), ["first gap", "second gap"])

    def test_classify_completion_band(self) -> None:
        self.assertEqual(classify_completion_band(3, 0), "near-complete")
        self.assertEqual(classify_completion_band(9, 0), "advanced")
        self.assertEqual(classify_completion_band(16, 0), "active")
        self.assertEqual(classify_completion_band(25, 0), "expanding")
        self.assertEqual(classify_completion_band(1, 2), "foundation-gap")

    def test_classify_target_track(self) -> None:
        self.assertEqual(classify_target_track(0, 0), "beyond-ready")
        self.assertEqual(classify_target_track(4, 0), "complete-now")
        self.assertEqual(classify_target_track(14, 0), "complete-next")
        self.assertEqual(classify_target_track(24, 0), "expand-then-complete")
        self.assertEqual(classify_target_track(3, 1), "foundation-first")

    def test_collect_repo_status_from_temp_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "sample-repo"
            root.mkdir()
            (root / "README.md").write_text("# Sample\n", encoding="utf-8")
            (root / "ROADMAP.md").write_text("- [ ] first\n- [ ] second\n", encoding="utf-8")
            (root / "LICENSE").write_text("CC BY 4.0\n", encoding="utf-8")
            (root / "SECURITY.md").write_text("security\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text("contrib\n", encoding="utf-8")
            (root / "CODE_OF_CONDUCT.md").write_text("conduct\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_sample.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
            (root / "module.py").write_text("VALUE = 1\n", encoding="utf-8")

            subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True, text=True)
            env = os.environ | {
                "GIT_AUTHOR_NAME": "Test User",
                "GIT_AUTHOR_EMAIL": "test@example.com",
                "GIT_COMMITTER_NAME": "Test User",
                "GIT_COMMITTER_EMAIL": "test@example.com",
            }
            subprocess.run(
                ["git", "-C", str(root), "commit", "-m", "Cycle 99: sample status repo"],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            status = collect_repo_status({"name": "sample-repo", "url": "https://example.invalid/sample.git"}, root)

            self.assertEqual(status.name, "sample-repo")
            self.assertEqual(status.latest_cycle, 99)
            self.assertEqual(status.open_roadmap_items, 2)
            self.assertEqual(status.required_files_present, 6)
            self.assertEqual(status.test_file_count, 1)
            self.assertEqual(status.completion_band, "near-complete")
            self.assertEqual(status.target_track, "complete-now")


if __name__ == "__main__":
    unittest.main()
