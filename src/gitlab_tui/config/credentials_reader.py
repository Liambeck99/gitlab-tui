"""Credentials manager for GitLab TUI."""

import tomllib
from logging import Logger
from pathlib import Path
from typing import Optional

from gitlab_tui.utils.exceptions import ConfigError


class CredentialsManager:
    """Manages reading the defined credentials"""

    CONFIG_DIR = Path.home() / ".config" / "gitlab-tui"
    CREDENTIALS_FILE_NAME = "credentials"

    def __init__(self, logger: Logger, domain: str):
        self.logger = logger
        self.credentials_file = self.CONFIG_DIR / self.CREDENTIALS_FILE_NAME
        self.domain = domain
        self._token: Optional[str] = None

    def _load_token(self) -> str:
        """Load token from credentials file.

        Returns:
            Token string

        Raises:
            ConfigError: If file doesn't exist or token not found
        """
        if not self.credentials_file.exists():
            self.logger.error(f"Credentials file not found: {self.credentials_file}")
            raise ConfigError(
                f"Credentials file not found at {self.credentials_file}\n\n"
                f"Expected format (use quotes around domains with dots):\n"
                f'["gitlab.com"]\n'
                f'token = "your_token_here"'
            )

        try:
            with open(self.credentials_file, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            raise ConfigError(
                f"Failed to parse credentials file: {self.credentials_file}\n\n"
                f"Expected TOML format:\n"
                f'["gitlab.com"]\n'
                f'token = "your_token_here"'
            ) from e

        domain_config = data.get(self.domain)

        if not domain_config:
            raise ConfigError(
                f"No configuration found for '{self.domain}'\n\n"
                f"Expected format:\n"
                f'["{self.domain}"]\n'
                f'token = "your_token_here"'
            )

        token = domain_config.get("token")

        if not token:
            raise ConfigError(
                f"No token found for '{self.domain}'\n\n"
                f"Expected format:\n"
                f'["{self.domain}"]\n'
                f'token = "your_token_here"'
            )

        return token

    def get_token(self) -> str:
        """Get GitLab token for the configured domain.

        Returns:
            GitLab personal access token
        """
        if self._token is None:
            self._token = self._load_token()
        return self._token
