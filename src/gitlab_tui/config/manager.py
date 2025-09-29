"""Configuration manager for GitLab TUI."""

import os
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Optional

import tomli_w


@dataclass
class GitLabConfig:
    """GitLab configuration."""

    url: str = "https://gitlab.com"
    default_branch: str = "master"
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

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "gitlab-tui"
        self.config_file = self.config_dir / "config.toml"
        self.credentials_file = self.config_dir / "credentials"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._config: Optional[AppConfig] = self._load_config_file()
        self._token: Optional[str] = (
            os.getenv("GITLAB_TUI_TOKEN") or self._load_credentials()
        )

    def _create_default_config(self) -> AppConfig:
        """Create default configuration."""
        return AppConfig(
            gitlab=GitLabConfig(),
            ui=UIConfig(),
            display=DisplayConfig(),
            icons=IconsConfig(),
            theme=ThemeConfig(),
        )

    def _load_config_file(self) -> AppConfig:
        """Load configuration from file."""
        if not self.config_file.exists():
            # Create default config file
            default_config = self._create_default_config()
            self._save_config_file(default_config)
            return default_config

        try:
            with open(self.config_file, "rb") as f:
                data = tomllib.load(f)

            # Parse sections
            gitlab_data = data.get("gitlab", {})
            ui_data = data.get("ui", {})
            display_data = data.get("display", {})
            icons_data = data.get("icons", {})
            theme_data = data.get("theme", {})

            # TODO: If not hard coded get value from gitlab repo
            if not gitlab_data.get("project"):
                raise ValueError("Missing value for project")

            return AppConfig(
                gitlab=GitLabConfig(**gitlab_data),
                ui=UIConfig(**ui_data),
                display=DisplayConfig(**display_data),
                icons=IconsConfig(**icons_data),
                theme=ThemeConfig(**theme_data),
            )

        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            print("Using default configuration", file=sys.stderr)
            return self._create_default_config()

    def _save_config_file(self, config: AppConfig) -> None:
        """Save configuration to file."""
        try:
            # Convert to dict format expected by TOML
            data = {
                "gitlab": asdict(config.gitlab),
                "ui": asdict(config.ui),
                "display": asdict(config.display),
                "icons": asdict(config.icons),
                "theme": asdict(config.theme),
            }

            with open(self.config_file, "wb") as f:
                tomli_w.dump(data, f)

            # Set appropriate permissions
            self.config_file.chmod(0o644)

        except Exception as e:
            print(f"Error saving config file: {e}", file=sys.stderr)

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
            print(f"Error loading credentials: {e}", file=sys.stderr)
            raise e

    def _save_credentials(self, token: str) -> None:
        """Save GitLab token to credentials file."""
        try:
            with open(self.credentials_file, "w") as f:
                f.write("# GitLab Personal Access Token\n")
                f.write(f"token={token}\n")

            # Set secure permissions (owner only)
            self.credentials_file.chmod(0o600)

        except Exception as e:
            print(f"Error saving credentials: {e}", file=sys.stderr)

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

    def save_token(self, token: str) -> None:
        """Save GitLab token to credentials file."""
        self._token = token
        self._save_credentials(token)

    def create_example_config(self) -> None:
        """Create example configuration files for first-time users."""
        if not self.config_file.exists():
            print(f"Creating default config at: {self.config_file}")
            self._save_config_file(self._create_default_config())

        if not self.credentials_file.exists():
            print(f"Creating credentials template at: {self.credentials_file}")
            with open(self.credentials_file, "w") as f:
                f.write("# GitLab Personal Access Token\n")
                f.write(
                    "# Get your token from: https://gitlab.com/-/profile/personal_access_tokens\n"
                )
                f.write("# token=glpat-your-token-here\n")
            self.credentials_file.chmod(0o600)
