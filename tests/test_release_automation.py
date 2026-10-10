#!/usr/bin/env python3
"""Release Please wiring for mint-action. Expected skips return assertions."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "opsdevcode-release.json"
RP_CONFIG = ROOT / "release-please-config.json"
MANIFEST = ROOT / ".release-please-manifest.json"
VERSION = ROOT / "VERSION"
WORKFLOW = ROOT / ".github" / "workflows" / "release-train.yml"
CI = ROOT / ".github" / "workflows" / "ci.yml"
README = ROOT / "README.md"
STARTER_PIN = "29918519e95b10eec7cbc3ffd253d7c5286599f6"
VERSION_PATTERN = r"^0\.[0-9]+\.[0-9]+-alpha\.[0-9]+$"
RELEASE_PLEASE_VERSION_MARKER = "x-release-please-version"


def _semver_on_line(line: str) -> str:
    token = line.split("#", 1)[0].strip()
    if not token:
        raise AssertionError(f"missing version before comment: {line!r}")
    return token


class ReleaseAutomationTests(unittest.TestCase):
    def test_contract_uses_release_please_not_none(self) -> None:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(data["engine"], "release-please")
        self.assertEqual(data["canonical"], "github-release")
        self.assertFalse(data["tagPolicy"]["manualTags"])
        self.assertFalse(data["tagPolicy"]["retag"])
        self.assertEqual(
            data["tagPolicy"]["pattern"],
            r"^v0\.[0-9]+\.[0-9]+-alpha\.[0-9]+$",
        )
        self.assertFalse(data["prerelease"]["githubMakeLatest"])
        self.assertFalse(data["provenance"]["synthesize"])
        self.assertEqual(data["downstream"]["marketplace"]["role"], "none")
        self.assertEqual(data["artifacts"], ["notes"])

    def test_release_please_is_alpha_simple_and_seeded(self) -> None:
        config = json.loads(RP_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(
            config["bootstrap-sha"],
            "b210974d2b0edb079b912f61d0ac028576af679e",
        )
        pkg = config["packages"]["."]
        self.assertEqual(pkg["release-type"], "simple")
        self.assertTrue(pkg["prerelease"])
        self.assertEqual(pkg["prerelease-type"], "alpha")
        self.assertEqual(pkg["versioning-strategy"], "prerelease")
        self.assertTrue(pkg["include-v-in-tag"])
        self.assertFalse(pkg["include-component-in-tag"])
        self.assertEqual(pkg["extra-files"], ["VERSION"])
        version_text = VERSION.read_text(encoding="utf-8")
        self.assertIn(RELEASE_PLEASE_VERSION_MARKER, version_text)
        version_lines = [line for line in version_text.splitlines() if line.strip()]
        self.assertEqual(len(version_lines), 1)
        published = _semver_on_line(version_lines[0])
        self.assertRegex(published, VERSION_PATTERN)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["."], published)

    def test_release_train_is_push_main_only_and_pinned(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("gh release create", text)
        self.assertNotIn("git tag", text)
        self.assertIn("permissions: {}", text)
        self.assertIn("googleapis/release-please-action@5c625bfb5d1ff62eadeeb3772007f7f66fdcf071", text)
        self.assertIn(
            "actions/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1",
            text,
        )
        self.assertIn("repositories: mint-action", text)
        self.assertIn("permission-contents: write", text)
        self.assertNotIn("permission-contents: admin", text)
        ci = CI.read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", ci)
        self.assertNotIn("pull_request_target", ci)

    def test_readme_still_pins_consumer_sha(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn(STARTER_PIN, text)
        self.assertNotIn("mint-action@main", text)
        self.assertNotIn("mint-action@latest", text)


if __name__ == "__main__":
    unittest.main()
