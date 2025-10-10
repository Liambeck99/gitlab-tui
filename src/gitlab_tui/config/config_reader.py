import tomllib
from logging import Logger
from pathlib import Path
from typing import Optional

from gitlab_tui.config.defaults import (
    AppConfig,
    IconsConfig,
    ThemeConfig,
)


class ConfigReader:
    """Manages reading the configuration"""

    CONFIG_DIR = Path.home() / ".config" / "gitlab-tui"
    CONFIG_FILE_NAME = "config.toml"

    def __init__(self, logger: Logger):
        self.logger = logger
        self.config_file = self.CONFIG_DIR / self.CONFIG_FILE_NAME
        self._app_config: Optional[AppConfig] = None
        self._icons_config: Optional[IconsConfig] = None
        self._theme_config: Optional[ThemeConfig] = None

    def _load_config(self) -> dict:
        """Load configuration from file

        Returns:
            Configuration data dictionary
        """
        if self.config_file.exists():
            with open(self.config_file, "rb") as f:
                return tomllib.load(f)
        else:
            return {}

    def get_app_config(self) -> AppConfig:
        """Get the App configuration"""
        if self._app_config is None:
            data = self._load_config()
            app_config_data = data.get("app", {})
            self._app_config = AppConfig(**app_config_data)
        return self._app_config

    def get_icons_config(self) -> IconsConfig:
        """Get the Icons configuration"""
        if self._icons_config is None:
            data = self._load_config()
            icons_config_data = data.get("icons", {})
            self._icons_config = IconsConfig(**icons_config_data)
        return self._icons_config

    def get_theme_config(self) -> ThemeConfig:
        """Get the Theme configuration"""
        if self._theme_config is None:
            data = self._load_config()
            theme_config_data = data.get("theme", {})
            self._theme_config = ThemeConfig(**theme_config_data)
        return self._theme_config
