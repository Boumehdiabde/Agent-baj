"""Skill system for domain-specific agent capabilities."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseSkill(ABC):
    """Base class for reusable domain skills."""

    name: str = "base"

    @abstractmethod
    async def run(self, task: str, **context: Any) -> str:
        """Execute the skill for a task."""


class DjangoSkill(BaseSkill):
    """Opinionated Django scaffolding and validation skill."""

    name = "django"

    async def run(self, task: str, **context: Any) -> str:
        return (
            "Django skill is ready. Suggested next steps: inspect settings.py, create the app, "
            "define models, run migrations, and validate with pytest or manage.py test. "
            f"Task: {task}"
        )


class DockerSkill(BaseSkill):
    """Basic Docker-oriented skill."""

    name = "docker"

    async def run(self, task: str, **context: Any) -> str:
        return (
            "Docker skill is ready. Validate the image, docker-compose config, and runtime healthchecks. "
            f"Task: {task}"
        )


class GitHubSkill(BaseSkill):
    """GitHub automation skill."""

    name = "github"

    async def run(self, task: str, **context: Any) -> str:
        return (
            "GitHub skill is ready. Check branch status, create a focused PR, and ensure CI is green. "
            f"Task: {task}"
        )


SKILL_REGISTRY: Dict[str, BaseSkill] = {
    "django": DjangoSkill(),
    "docker": DockerSkill(),
    "github": GitHubSkill(),
}


def list_skills() -> List[str]:
    return sorted(SKILL_REGISTRY.keys())
