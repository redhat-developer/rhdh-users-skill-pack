"""Shared pytest fixtures for rhdh-users-skill-pack tests."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def skill_root():
    """Return the project root path."""
    return PROJECT_ROOT
