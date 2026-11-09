import tempfile
import json
import subprocess
import unittest
import urllib.error
from pathlib import Path

from daily_health import audit_requirement, audit_rows, collect, local_path, markdown_targets


class DailyHealthTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.config = {"project": "Fixture", "files": [], "scope": "Test fixture"}

    def test_missing_required_file_is_failure(self):
        self.config["files"] = ["missing.png"]
        report, failed = collect(self.root, self.config, "2026-11-08")
        self.assertTrue(failed)
        self.assertIn("Required file missing", report)

    def test_repository_escape_rejected(self):
        with self.assertRaises(ValueError):
            local_path(self.root, "../outside")

    def test_code_examples_are_not_links(self):
        text = "[real](README.md)\n```md\n[example](missing.md)\n```\n`[example](missing.md)`"
        self.assertEqual(markdown_targets(text), ["README.md"])

    def test_relative_links_and_missing_target(self):
        (self.root / "docs").mkdir()
        (self.root / "README.md").write_text("Readme")
        (self.root / "docs/notes.md").write_text("[ok](../README.md#section) [bad](missing.md)")
        self.config["markdown"] = ["docs/notes.md"]
        report, failed = collect(self.root, self.config, "2026-11-08")
        self.assertTrue(failed)
        self.assertIn("| PASS | Local target exists", report)
        self.assertIn("| FAIL | Local target missing", report)

    def test_network_failure_is_unverified_not_healthy(self):
        self.config["urls"] = ["https://example.com"]

        def unavailable(*args, **kwargs):
            raise urllib.error.URLError("offline")

        report, failed = collect(self.root, self.config, "2026-11-08", unavailable)
        self.assertFalse(failed)
        self.assertIn("| WARN | Unverified:", report)

    def test_syntax_and_checksum_failures(self):
        (self.root / "app.py").write_text("def broken(:")
        (self.root / "asset").write_bytes(b"modified")
        self.config.update(python=["app.py"], sha256={"asset": "0" * 64})
        report, failed = collect(self.root, self.config, "2026-11-08")
        self.assertTrue(failed)
        self.assertIn("2 failed checks", report)

    def test_release_watch_is_repeatable_and_day_changes(self):
        (self.root / "requirements.txt").write_text("numpy~=2.0.1\n")
        self.config["requirements"] = "requirements.txt"

        def metadata(*args, **kwargs):
            return {"info": {"version": "2.3.0", "requires_python": ">=3.11"}}

        first = collect(self.root, self.config, "2026-11-08", metadata)
        self.assertEqual(first, collect(self.root, self.config, "2026-11-08", metadata))
        self.assertNotEqual(first, collect(self.root, self.config, "2026-11-09", metadata))
        self.assertIn("| numpy | ~=2.0.1 | 2.3.0 | >=3.11 |", first[0])

    def test_unsupported_requirement_is_visible_failure(self):
        (self.root / "requirements.txt").write_text("-r other.txt\n")
        self.config["requirements"] = "requirements.txt"
        report, failed = collect(self.root, self.config, "2026-11-08")
        self.assertTrue(failed)
        self.assertIn("Unsupported requirement", report)

    def test_clean_audit_is_reported(self):
        result = subprocess.CompletedProcess([], 0, json.dumps({
            'dependencies': [{'name': 'pillow', 'version': '13.0.0', 'vulns': []}]
        }))
        self.config['vulnerability_audit'] = True
        report, failed = collect(self.root, self.config, '2026-11-09', auditor=lambda: result)
        self.assertFalse(failed)
        self.assertIn('1 installed packages audited', report)

    def test_vulnerability_fails_report_with_fix(self):
        result = subprocess.CompletedProcess([], 1, json.dumps({
            'dependencies': [{'name': 'pillow', 'version': '10.4.0', 'vulns': [
                {'id': 'TEST-ADVISORY', 'fix_versions': ['13.0.0']}
            ]}]
        }))
        self.config['vulnerability_audit'] = True
        report, failed = collect(self.root, self.config, '2026-11-09', auditor=lambda: result)
        self.assertTrue(failed)
        self.assertIn('TEST-ADVISORY; fixed versions: 13.0.0', report)

    def test_incomplete_or_broken_audit_never_passes(self):
        cases = [
            (1, ''), (0, 'not json'), (0, '{}'), (0, '{"dependencies": []}'),
            (0, '{"dependencies": [{"name": "private", "skip_reason": "Unavailable"}]}'),
            (1, '{"dependencies": [{"name": "pillow", "version": "13.0.0", "vulns": []}]}'),
            (0, '{"dependencies": [{"name": "pillow", "version": "13.0.0", "vulns": null}]}'),
        ]
        for code, output in cases:
            with self.subTest(code=code, output=output):
                result = subprocess.CompletedProcess([], code, output)
                rows = audit_rows(lambda: result)
                self.assertTrue(all(row[1] == 'FAIL' for row in rows))

    def test_audit_timeout_is_a_failure(self):
        def timeout():
            raise subprocess.TimeoutExpired('pip_audit', 300)
        self.assertEqual(audit_rows(timeout)[0][1], 'FAIL')

    def test_cpu_builds_are_audited_at_the_actual_upstream_version(self):
        self.assertEqual(audit_requirement('torch', '2.4.0+cpu'), 'torch==2.4.0')
        self.assertEqual(audit_requirement('torchvision', '0.29.2+cpu'), 'torchvision==0.29.2')
        self.assertEqual(audit_requirement('pillow', '13.0.0'), 'pillow==13.0.0')
        # Unknown private builds must remain unverified, not silently become public versions.
        self.assertEqual(audit_requirement('torch', '2.15.0+custom'), 'torch==2.15.0+custom')
        self.assertEqual(audit_requirement('other', '1.0+cpu'), 'other==1.0+cpu')


if __name__ == "__main__":
    unittest.main()
