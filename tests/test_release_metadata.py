import re
import tomllib
import unittest
from pathlib import Path

from gamerhq_skill_recurring_posts import RecurringPostsSkill


ROOT = Path(__file__).resolve().parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def setUp(self):
        self.pyproject = tomllib.loads(
            (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        self.version = self.pyproject["project"]["version"]

    def test_package_manifest_and_readme_versions_match(self):
        self.assertEqual(RecurringPostsSkill.manifest.version, self.version)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        match = re.search(r"^Version: `([^`]+)`", readme, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), self.version)

    def test_current_version_has_changelog_section(self):
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"\n## {self.version}\n", changelog)

    def test_unreleased_is_first_changelog_section(self):
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        sections = re.findall(r"^## (.+)$", changelog, flags=re.MULTILINE)
        self.assertGreater(len(sections), 1)
        self.assertEqual(sections[0], "Unreleased")
        self.assertEqual(sections[1], self.version)

    def test_package_identity_matches_release_metadata(self):
        self.assertEqual(
            self.pyproject["project"]["name"],
            "gamerhq-skill-recurring-posts",
        )
        self.assertEqual(
            self.pyproject["tool"]["gamerhq"]["skill-id"],
            RecurringPostsSkill.manifest.id,
        )
        self.assertEqual(
            self.pyproject["tool"]["gamerhq"]["runtime-api"],
            RecurringPostsSkill.manifest.runtime_api_version,
        )


if __name__ == "__main__":
    unittest.main()
