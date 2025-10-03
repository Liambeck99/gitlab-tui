"""Configuration manager for GitLab TUI."""

import os
import subprocess  # nosec B404
import tomllib
from argparse import Namespace
from dataclasses import dataclass, field
from logging import Logger
from pathlib import Path
from typing import Dict, Optional

from gitlab_tui.utils.exceptions import ConfigError


@dataclass
class GitLabConfig:
    """GitLab configuration."""

    url: str = "https://gitlab.com"
    branch: str = "master"
    project: str = ""


@dataclass
class UIConfig:
    """UI configuration."""

    theme: str = "dark"
    auto_refresh: int = 300  # seconds


@dataclass
class DisplayConfig:
    """Display configuration."""

    timestamp_format: str = "%m/%d/%y %H:%M"


@dataclass
class IconsConfig:
    """Icons configuration."""

    default_icon: str = "?"
    success: str = "\uf058"  # Circle with tick ()
    failed: str = "\uf530"  # Circle with cross ()
    running: str = "\uf042"  # Circle part full ()
    pending: str = "\uebb5"  # Circle with pause ()
    canceled: str = "\ueabd"  # Circle with line through ()
    created: str = "\uf1ce"  # Circle with notch ()
    manual: str = "\uf013"  # Cog ()
    skipped: str = "\uf192"  # Circle with dot ()

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get icon by key with optional default."""
        if not default:
            default = self.default_icon
        return getattr(self, key, default)


@dataclass
class ThemeConfig:
    name: str = "catppuccin-mocha"
    primary: str = "#cba6f7"  # Mauve - primary accent color
    secondary: str = "#89b4fa"  # Blue - secondary accent
    accent: str = "#f5c2e7"  # Pink - tertiary accent
    foreground: str = "#cdd6f4"  # Text - main text color
    background: str = "#1e1e2e"  # Base - main background
    success: str = "#a6e3a1"  # Green - success states
    warning: str = "#f9e2af"  # Yellow - warnings
    error: str = "#f38ba8"  # Red - errors and dangers
    surface: str = "#313244"  # Surface0 - elevated surfaces
    panel: str = "#45475a"  # Surface2 - panels and sidebars
    dark: bool = True
    variables: Dict[str, str] = field(
        default_factory=lambda: {
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#cba6f7",  # Mauve for footer keys
            "input-selection-background": "#89b4fa 35%",  # Blue with transparency
            # Additional Catppuccin-specific variables
            "border-color": "#6c7086",  # Overlay1 for borders
            "scrollbar-color": "#585b70",  # Overlay0 for scrollbars
            "scrollbar-hover-color": "#6c7086",  # Overlay1 for scrollbar hover
            "tab-active-foreground": "#cba6f7",  # Mauve for active tabs
            "tab-inactive-foreground": "#9399b2",  # Subtext0 for inactive tabs
            "button-hover-background": "#585b70",  # Overlay0 for button hover
            "text_primary": "#cdd6f4",  # Text - your existing foreground (best contrast)
            "text_secondary": "#bac2de",  # Subtext1 - slightly dimmed
            "text_tertiary": "#a6adc8",  # Subtext0 - more subtle
            "text_muted": "#9399b2",  # Overlay2 - disabled states
            "text_subtle": "#7f849c",  # Overlay1 - very subtle text
            "text_faint": "#6c7086",  # Overlay0 - placeholders, hints
        }
    )


@dataclass
class AppConfig:
    """Main application configuration."""

    gitlab: GitLabConfig
    ui: UIConfig
    display: DisplayConfig
    icons: IconsConfig
    theme: ThemeConfig


class ConfigManager:
    """Manages configuration and credentials for GitLab TUI."""

    def __init__(self, logger: Logger, args: Namespace):
        self.logger = logger
        self.config_dir = Path.home() / ".config" / "gitlab-tui"
        self.config_file = self.config_dir / "config.toml"
        self.credentials_file = self.config_dir / "credentials"
        self.args = args

        self._config: Optional[AppConfig] = self._load_config_file()
        self._token: Optional[str] = (
            os.getenv("GITLAB_TUI_TOKEN") or self._load_credentials()
        )

    def _load_config_file(self) -> AppConfig:
        """Load configuration from file."""
        try:
            user_gitlab_data = {
                "project": self._get_project(),
                "branch": self._get_branch(),
            }

            if not self.config_file.exists():
                # Create default config file
                default_config = AppConfig(
                    gitlab=GitLabConfig(**user_gitlab_data),
                    ui=UIConfig(),
                    display=DisplayConfig(),
                    icons=IconsConfig(),
                    theme=ThemeConfig(),
                )
                return default_config

            with open(self.config_file, "rb") as f:
                data = tomllib.load(f)

            # Parse sections
            gitlab_data = data.get("gitlab", {})
            ui_data = data.get("ui", {})
            display_data = data.get("display", {})
            icons_data = data.get("icons", {})
            theme_data = data.get("theme", {})

            merged_gitlab_data = {**gitlab_data, **user_gitlab_data}

            return AppConfig(
                gitlab=GitLabConfig(**merged_gitlab_data),
                ui=UIConfig(**ui_data),
                display=DisplayConfig(**display_data),
                icons=IconsConfig(**icons_data),
                theme=ThemeConfig(**theme_data),
            )

        except Exception as e:
            self.logger.error(f"Error loading config file: {e}")
            raise ConfigError("Error loading config file")

    def _load_credentials(self) -> str:
        """Load GitLab token from credentials file."""
        try:
            with open(self.credentials_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("token="):
                        return line.split("=", 1)[1]

                raise ValueError(
                    f"No line starting with 'token=' was found in {self.credentials_file}"
                )
        except Exception as e:
            self.logger.error(f"Error loading credentials: {e}")
            raise ConfigError("Error loading credentials")

    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        if self._config is None:
            self._config = self._load_config_file()
        return self._config

    def get_token(self) -> str:
        """Get the GitLab token from various sources."""
        if self._token is None:
            self._token = os.getenv("GITLAB_TUI_TOKEN") or self._load_credentials()
        return self._token

    def _get_project(self) -> str:
        """Get the project to use"""
        project = self.args.project or self._get_project_path()
        if not project:
            raise ConfigError("Project not provided and/or not in a git repo")

        return project

    def _get_branch(self) -> str:
        """Get the branch name to use"""
        branch = self.args.branch or self._get_current_branch()
        if not branch:
            raise ConfigError("Branch not provided and/or not in git repo")

        return branch

    def _get_project_path(self) -> str:
        remote_url = self._get_git_remote_url()
        return self._parse_gitlab_project_from_url(remote_url)

    def _get_git_remote_url(self) -> str:
        """Get the Git remote URL for the current repository.

        Returns:
            Remote URL or None if not in a git repo
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
        except subprocess.CalledProcessError:
            self.logger.debug("Not in a git repository or no remote configured")
            raise ConfigError("Not in a git repo or no remote configured")
        except FileNotFoundError:
            self.logger.warning("Git command not found")
            raise ConfigError("Git command not found")

    def _parse_gitlab_project_from_url(self, url: str) -> str:
        """Extract GitLab project path from a remote URL.

        Supports:
        - https://gitlab.com/group/project.git
        - git@gitlab.com:group/project.git
        - https://gitlab.example.com/group/subgroup/project.git

        Returns:
            Project path (e.g., 'group/project') or None
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
            # Split by protocol and take the part after the domain
            parts = url.split("://", 1)[1].split("/", 1)
            if len(parts) >= 2:
                return parts[1]

        raise ConfigError("Unexpected url format")

    def _get_current_branch(self) -> Optional[str]:
        """Get the current Git branch name.

        Returns:
            Branch name or None
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
        except subprocess.CalledProcessError:
            self.logger.info("Could not determine current branch")
            return None
