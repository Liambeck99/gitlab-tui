"""Main configuration class for GitLab TUI application."""

from logging import Logger
from typing import Optional

from gitlab_tui.config.config_reader import ConfigReader
from gitlab_tui.config.credentials_reader import CredentialsManager
from gitlab_tui.config.defaults import AppConfig, IconsConfig, ThemeConfig
from gitlab_tui.config.git_context_resolver import GitContextResolver


class Config:
    """Main configuration class providing namespaced access to all config components.

    Usage:
        config = Config(logger)

        # Git context
        url = config.git.get_remote_url()
        domain = config.git.get_domain()

        # App configuration
        theme = config.app.theme
        refresh = config.app.auto_refresh

        # Icons
        success = config.icons.success
        failed = config.icons.failed

        # Theme
        primary = config.theme.primary
        background = config.theme.background

        # Credentials
        token = config.credentials.get_token()
    """

    def __init__(self, logger: Logger):
        self.logger = logger
        self._git: Optional[GitContextResolver] = None
        self._config_reader: Optional[ConfigReader] = None
        self._app: Optional[AppConfig] = None
        self._icons: Optional[IconsConfig] = None
        self._theme: Optional[ThemeConfig] = None
        self._credentials: Optional[CredentialsManager] = None

    @property
    def git(self) -> GitContextResolver:
        """Get the Git context resolver."""
        if self._git is None:
            self._git = GitContextResolver(self.logger)
        return self._git

    @property
    def app(self) -> AppConfig:
        """Get the App configuration."""
        if self._app is None:
            config_reader = self._get_config_reader()
            self._app = config_reader.get_app_config()
        return self._app

    @property
    def icons(self) -> IconsConfig:
        """Get the Icons configuration."""
        if self._icons is None:
            config_reader = self._get_config_reader()
            self._icons = config_reader.get_icons_config()
        return self._icons

    @property
    def theme(self) -> ThemeConfig:
        """Get the Theme configuration."""
        if self._theme is None:
            config_reader = self._get_config_reader()
            self._theme = config_reader.get_theme_config()
        return self._theme

    @property
    def credentials(self) -> CredentialsManager:
        """Get the Credentials manager."""
        if self._credentials is None:
            domain = self.git.get_domain()
            self._credentials = CredentialsManager(self.logger, domain)
        return self._credentials

    def _get_config_reader(self) -> ConfigReader:
        """Get the config reader (shared between app, icons, and theme)."""
        if self._config_reader is None:
            self._config_reader = ConfigReader(self.logger)
        return self._config_reader
