"""Tests for SKILL.md structure and content validation."""

import re

import pytest
import yaml


class TestSkillMakerSkillMd:
    """Test that skill-maker SKILL.md has required structure."""

    @pytest.fixture
    def skill_md(self, skill_root):
        """Load skill-maker SKILL.md content."""
        skill_path = skill_root / "skills" / "skill-maker" / "SKILL.md"
        return skill_path.read_text(encoding="utf-8")

    @pytest.fixture
    def skill_frontmatter(self, skill_md):
        """Parse YAML frontmatter from SKILL.md."""
        match = re.match(r"^---\n(.*?)\n---", skill_md, re.DOTALL)
        if not match:
            pytest.fail("SKILL.md missing YAML frontmatter")
        return yaml.safe_load(match.group(1))

    def test_frontmatter_has_name(self, skill_frontmatter):
        """SKILL.md must have a name field matching the directory."""
        assert "name" in skill_frontmatter
        assert skill_frontmatter["name"] == "skill-maker"

    def test_frontmatter_has_description(self, skill_frontmatter):
        """SKILL.md must have a description field."""
        assert "description" in skill_frontmatter
        assert len(skill_frontmatter["description"]) > 20


class TestUserFacingSkillDirectories:
    """Ensure only expected user-facing skills are present."""

    EXPECTED_SKILLS = {"skill-maker", "rhdh-upgrade-helper"}

    def test_skill_directories(self, skill_root):
        """skills/ should contain exactly the user-facing skill set."""
        skills_dir = skill_root / "skills"
        actual = {path.name for path in skills_dir.iterdir() if path.is_dir()}
        assert actual == self.EXPECTED_SKILLS
