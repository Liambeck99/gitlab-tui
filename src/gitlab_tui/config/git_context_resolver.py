import subprocess  # nosec B404
from logging import Logger
from pathlib import Path
from typing import Optional

from gitlab_tui.utils.exceptions import ConfigError


class GitContextResolver:
    """Manages reading the projects .git configuration"""

    def __init__(self, logger: Logger):
        self.logger = logger
        self._remote_url: Optional[str] = None
        self._project_path: Optional[str] = None
        self._domain: Optional[str] = None
        self._current_branch: Optional[str] = None

    def _init_remote_url(self) -> str:
        """Get the Git remote URL for the current repository.

        Returns:
            Remote URL string

        Raises:
            ConfigError: If any of the following occur:
                - Not in a git repository
                - No remote origin configured
                - Git command not found
        """
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],  # nosec B603 B607
                capture_output=True,
                text=True,
                check=True,
                cwd=Path.cwd(),
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.debug("Not in a git repository or no remote configured")
            raise ConfigError("Not in a git repo or no remote configured") from e
        except FileNotFoundError as e:
            self.logger.warning("Git command not found")
            raise ConfigError("Git command not found") from e

    def _get_project_path_from_url(self, url: str) -> str:
        """Extract GitLab project path from a remote URL.

        Supports:
        - https://gitlab.com/group/project.git
        - git@gitlab.com:group/project.git
        - https://gitlab.example.com/group/subgroup/project.git

        Returns:
            Project path string

        Raises:
            ConfigError: On unexpected URL format

        """
        # Remove .git suffix
        url = url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]

        # Handle SSH format: git@gitlab.com:group/project
        if url.startswith("git@"):
            parts = url.split(":")
            if len(parts) >= 2:
                return parts[1]

        # Handle HTTPS format: https://gitlab.com/group/project
        if "://" in url:
            parts = url.split("://", 1)[1].split("/", 1)
            if len(parts) >= 2:
                return parts[1]

        raise ConfigError("Unexpected url format")

    def _get_domain_from_url(self, url: str) -> str:
        """Extract GitLab domain from a remote URL.

        Supports:
        - https://gitlab.com/group/project.git
        - git@gitlab.com:group/project.git
        - https://gitlab.example.com/group/subgroup/project.git

        Returns:
            Domain string

        Raises:
            ConfigError: On unexpected URL format
        """
        # Handle SSH format: git@gitlab.com:group/project
        if url.startswith("git@"):
            url = url[4:]
            parts = url.split(":")
            if len(parts) >= 2:
                return parts[0]

        # Handle HTTPS format: https://gitlab.com/group/project
        if "://" in url:
            # Split by protocol and take the part after the domain
            parts = url.split("://", 1)[1].split("/", 1)
            if len(parts) >= 2:
                return parts[0]

        raise ConfigError("Unexpected url format")

    def _init_current_branch(self) -> str:
        """Get the current Git branch name

        Returns:
            Branch name string
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],  # nosec B603 B607
                capture_output=True,
                text=True,
                check=True,
                cwd=Path.cwd(),
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.info("Could not determine current branch")
            raise ConfigError("Could not determine current branch") from e

    def get_remote_url(self) -> str:
        """Get the remote url for the selected project."""
        if self._remote_url is None:
            self._remote_url = self._init_remote_url()
        return self._remote_url

    def get_domain(self) -> str:
        """Get the domain for the selected project"""
        if self._domain is None:
            remote_url = self.get_remote_url()
            self._domain = self._get_domain_from_url(remote_url)
        return self._domain

    def get_project_path(self) -> str:
        """Get the project path for the selected project"""
        if self._project_path is None:
            remote_url = self.get_remote_url()
            self._project_path = self._get_project_path_from_url(remote_url)
        return self._project_path

    def get_current_branch(self) -> str:
        """Get the current branch for the selected project"""
        if self._current_branch is None:
            self._current_branch = self._init_current_branch()
        return self._current_branch
