"""Tests for ConfigReader class."""

from logging import Logger
from pathlib import Path
from textwrap import dedent
from unittest.mock import Mock, patch

import pytest

from gitlab_tui.config.config_reader import ConfigReader
from gitlab_tui.config.defaults import AppConfig, IconsConfig, ThemeConfig


@pytest.fixture
def mock_logger():
    """Create a mock logger"""
    return Mock(spec=Logger)


@pytest.fixture
def config_reader(mock_logger, tmp_path, monkeypatch):
    """Create a ConfigReader instance"""
    monkeypatch.setattr(ConfigReader, "CONFIG_DIR", tmp_path)
    reader = ConfigReader(mock_logger)
    return reader


class TestConfigReaderInit:
    """Test ConfigReader.__init__"""

    def test_init_sets_logger(self, mock_logger):
        reader = ConfigReader(mock_logger)
        assert reader.logger == mock_logger

    def test_init_sets_config_file_path(self, mock_logger):
        reader = ConfigReader(mock_logger)
        expected_path = Path.home() / ".config" / "gitlab-tui" / "config.toml"
        assert reader.config_file == expected_path

    def test_init_sets_all_attributes_to_none(self, mock_logger):
        reader = ConfigReader(mock_logger)
        assert reader._app_config is None
        assert reader._icons_config is None
        assert reader._theme_config is None


class TestLoadConfig:
    """Test ConfigReader._load_config"""

    def test_returns_empty_dict_when_file_not_exists(self, config_reader):
        """Test returns empty dict when config file doesn't exist"""
        result = config_reader._load_config()
        assert result == {}

    def test_loads_and_returns_toml_data(self, config_reader):
        """Test loads and returns TOML data when file exists"""
        with open(config_reader.config_file, "w") as f:
            content = """
            [app]
            theme = "light"
            auto_refresh = 600

            [icons]
            success = "✓"
            failed = "✗"

            [theme]
            name = "custom-theme"
            primary = "#ff0000"
            """
            f.write(dedent(content).strip())

        result = config_reader._load_config()

        expected = {
            "app": {
                "theme": "light",
                "auto_refresh": 600,
            },
            "icons": {
                "success": "✓",
                "failed": "✗",
            },
            "theme": {
                "name": "custom-theme",
                "primary": "#ff0000",
            },
        }
        assert result == expected


class TestGetAppConfig:
    """Test ConfigReader.get_app_config"""

    @patch.object(ConfigReader, "_load_config")
    def test_returns_app_config_successfully(self, mock_load_config, mock_logger):
        """Test successful retrieval of app config with lazy initialization"""
        mock_load_config.return_value = {
            "app": {
                "theme": "light",
                "auto_refresh": 600,
                "timestamp_format": "%d/%m/%y %H:%M",
            }
        }

        reader = ConfigReader(mock_logger)
        result = reader.get_app_config()

        assert isinstance(result, AppConfig)
        assert result.theme == "light"
        assert result.auto_refresh == 600
        assert result.timestamp_format == "%d/%m/%y %H:%M"
        mock_load_config.assert_called_once()

    @patch.object(ConfigReader, "_load_config")
    def test_uses_defaults_when_app_section_missing(
        self, mock_load_config, mock_logger
    ):
        """Test uses default values when app section is missing"""
        mock_load_config.return_value = {}

        reader = ConfigReader(mock_logger)
        result = reader.get_app_config()

        assert isinstance(result, AppConfig)
        assert result.theme == "dark"  # default value
        assert result.auto_refresh == 300  # default value
        assert result.timestamp_format == "%m/%d/%y %H:%M"  # default value
        mock_load_config.assert_called_once()

    @patch.object(ConfigReader, "_load_config")
    def test_caches_app_config_on_subsequent_calls(self, mock_load_config, mock_logger):
        """Test that app config is cached after first call"""
        mock_load_config.return_value = {"app": {"theme": "light"}}

        reader = ConfigReader(mock_logger)
        first_call = reader.get_app_config()
        second_call = reader.get_app_config()

        assert first_call is second_call  # Same instance
        mock_load_config.assert_called_once()  # Should only be called once due to caching


class TestGetIconsConfig:
    """Test ConfigReader.get_icons_config"""

    @patch.object(ConfigReader, "_load_config")
    def test_returns_icons_config_successfully(self, mock_load_config, mock_logger):
        """Test successful retrieval of icons config with lazy initialization"""
        mock_load_config.return_value = {
            "icons": {"success": "✓", "failed": "✗", "running": "▶"}
        }

        reader = ConfigReader(mock_logger)
        result = reader.get_icons_config()

        assert isinstance(result, IconsConfig)
        assert result.success == "✓"
        assert result.failed == "✗"
        assert result.running == "▶"
        mock_load_config.assert_called_once()

    @patch.object(ConfigReader, "_load_config")
    def test_uses_defaults_when_icons_section_missing(
        self, mock_load_config, mock_logger
    ):
        """Test uses default values when icons section is missing"""
        mock_load_config.return_value = {}

        reader = ConfigReader(mock_logger)
        result = reader.get_icons_config()

        assert isinstance(result, IconsConfig)
        assert result.default_icon == "?"  # default value
        assert result.success == "\uf058"  # default value
        mock_load_config.assert_called_once()

    @patch.object(ConfigReader, "_load_config")
    def test_caches_icons_config_on_subsequent_calls(
        self, mock_load_config, mock_logger
    ):
        """Test that icons config is cached after first call"""
        mock_load_config.return_value = {"icons": {"success": "✓"}}

        reader = ConfigReader(mock_logger)
        first_call = reader.get_icons_config()
        second_call = reader.get_icons_config()

        assert first_call is second_call  # Same instance
        mock_load_config.assert_called_once()  # Should only be called once due to caching


class TestGetThemeConfig:
    """Test ConfigReader.get_theme_config"""

    @patch.object(ConfigReader, "_load_config")
    def test_returns_theme_config_successfully(self, mock_load_config, mock_logger):
        """Test successful retrieval of theme config with lazy initialization"""
        mock_load_config.return_value = {
            "theme": {
                "name": "custom-theme",
                "primary": "#ff0000",
                "background": "#000000",
            }
        }

        reader = ConfigReader(mock_logger)
        result = reader.get_theme_config()

        assert isinstance(result, ThemeConfig)
        assert result.name == "custom-theme"
        assert result.primary == "#ff0000"
        assert result.background == "#000000"
        mock_load_config.assert_called_once()

    @patch.object(ConfigReader, "_load_config")
    def test_uses_defaults_when_theme_section_missing(
        self, mock_load_config, mock_logger
    ):
        """Test uses default values when theme section is missing"""
        mock_load_config.return_value = {}

        reader = ConfigReader(mock_logger)
        result = reader.get_theme_config()

        assert isinstance(result, ThemeConfig)
        assert result.name == "catppuccin-mocha"  # default value
        assert result.primary == "#cba6f7"  # default value
        assert result.dark is True  # default value
        mock_load_config.assert_called_once()

    @patch.object(ConfigReader, "_load_config")
    def test_caches_theme_config_on_subsequent_calls(
        self, mock_load_config, mock_logger
    ):
        """Test that theme config is cached after first call"""
        mock_load_config.return_value = {"theme": {"name": "custom"}}

        reader = ConfigReader(mock_logger)
        first_call = reader.get_theme_config()
        second_call = reader.get_theme_config()

        assert first_call is second_call  # Same instance
        mock_load_config.assert_called_once()  # Should only be called once due to caching
