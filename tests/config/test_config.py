"""Tests for main Config class."""

from logging import Logger
from unittest.mock import Mock, patch

import pytest

from gitlab_tui.config.config import Config
from gitlab_tui.config.config_reader import ConfigReader
from gitlab_tui.config.credentials_reader import CredentialsManager
from gitlab_tui.config.defaults import AppConfig, IconsConfig, ThemeConfig
from gitlab_tui.config.git_context_resolver import GitContextResolver


@pytest.fixture
def mock_logger():
    """Create a mock logger"""
    return Mock(spec=Logger)


@pytest.fixture
def config(mock_logger):
    """Create a Config instance"""
    return Config(mock_logger)


class TestConfigInit:
    """Test Config.__init__"""

    def test_init_sets_logger(self, mock_logger):
        config = Config(mock_logger)
        assert config.logger == mock_logger

    def test_init_sets_all_attributes_to_none(self, mock_logger):
        config = Config(mock_logger)
        assert config._git is None
        assert config._config_reader is None
        assert config._app is None
        assert config._icons is None
        assert config._theme is None
        assert config._credentials is None


class TestGitProperty:
    """Test Config.git property"""

    @patch("gitlab_tui.config.config.GitContextResolver")
    def test_returns_git_context_resolver(self, mock_git_class, config):
        """Test git property returns GitContextResolver instance"""
        mock_git_instance = Mock(spec=GitContextResolver)
        mock_git_class.return_value = mock_git_instance

        result = config.git

        assert result == mock_git_instance
        mock_git_class.assert_called_once_with(config.logger)

    @patch("gitlab_tui.config.config.GitContextResolver")
    def test_caches_git_context_resolver(self, mock_git_class, config):
        """Test git property caches the GitContextResolver instance"""
        mock_git_instance = Mock(spec=GitContextResolver)
        mock_git_class.return_value = mock_git_instance

        first_call = config.git
        second_call = config.git

        assert first_call is second_call
        mock_git_class.assert_called_once()  # Should only be called once due to caching


class TestAppProperty:
    """Test Config.app property"""

    @patch.object(Config, "_get_config_reader")
    def test_returns_app_config(self, mock_get_config_reader, config):
        """Test app property returns AppConfig instance"""
        mock_config_reader = Mock(spec=ConfigReader)
        mock_app_config = Mock(spec=AppConfig)
        mock_config_reader.get_app_config.return_value = mock_app_config
        mock_get_config_reader.return_value = mock_config_reader

        result = config.app

        assert result == mock_app_config
        mock_get_config_reader.assert_called_once()
        mock_config_reader.get_app_config.assert_called_once()

    @patch.object(Config, "_get_config_reader")
    def test_caches_app_config(self, mock_get_config_reader, config):
        """Test app property caches the AppConfig instance"""
        mock_config_reader = Mock(spec=ConfigReader)
        mock_app_config = Mock(spec=AppConfig)
        mock_config_reader.get_app_config.return_value = mock_app_config
        mock_get_config_reader.return_value = mock_config_reader

        first_call = config.app
        second_call = config.app

        assert first_call is second_call
        mock_get_config_reader.assert_called_once()  # Should only be called once due to caching
        mock_config_reader.get_app_config.assert_called_once()


class TestIconsProperty:
    """Test Config.icons property"""

    @patch.object(Config, "_get_config_reader")
    def test_returns_icons_config(self, mock_get_config_reader, config):
        """Test icons property returns IconsConfig instance"""
        mock_config_reader = Mock(spec=ConfigReader)
        mock_icons_config = Mock(spec=IconsConfig)
        mock_config_reader.get_icons_config.return_value = mock_icons_config
        mock_get_config_reader.return_value = mock_config_reader

        result = config.icons

        assert result == mock_icons_config
        mock_get_config_reader.assert_called_once()
        mock_config_reader.get_icons_config.assert_called_once()

    @patch.object(Config, "_get_config_reader")
    def test_caches_icons_config(self, mock_get_config_reader, config):
        """Test icons property caches the IconsConfig instance"""
        mock_config_reader = Mock(spec=ConfigReader)
        mock_icons_config = Mock(spec=IconsConfig)
        mock_config_reader.get_icons_config.return_value = mock_icons_config
        mock_get_config_reader.return_value = mock_config_reader

        first_call = config.icons
        second_call = config.icons

        assert first_call is second_call
        mock_get_config_reader.assert_called_once()  # Should only be called once due to caching
        mock_config_reader.get_icons_config.assert_called_once()


class TestThemeProperty:
    """Test Config.theme property"""

    @patch.object(Config, "_get_config_reader")
    def test_returns_theme_config(self, mock_get_config_reader, config):
        """Test theme property returns ThemeConfig instance"""
        mock_config_reader = Mock(spec=ConfigReader)
        mock_theme_config = Mock(spec=ThemeConfig)
        mock_config_reader.get_theme_config.return_value = mock_theme_config
        mock_get_config_reader.return_value = mock_config_reader

        result = config.theme

        assert result == mock_theme_config
        mock_get_config_reader.assert_called_once()
        mock_config_reader.get_theme_config.assert_called_once()

    @patch.object(Config, "_get_config_reader")
    def test_caches_theme_config(self, mock_get_config_reader, config):
        """Test theme property caches the ThemeConfig instance"""
        mock_config_reader = Mock(spec=ConfigReader)
        mock_theme_config = Mock(spec=ThemeConfig)
        mock_config_reader.get_theme_config.return_value = mock_theme_config
        mock_get_config_reader.return_value = mock_config_reader

        first_call = config.theme
        second_call = config.theme

        assert first_call is second_call
        mock_get_config_reader.assert_called_once()  # Should only be called once due to caching
        mock_config_reader.get_theme_config.assert_called_once()


class TestCredentialsProperty:
    """Test Config.credentials property"""

    @patch("gitlab_tui.config.config.CredentialsManager")
    @patch.object(Config, "git", new_callable=lambda: Mock(spec=GitContextResolver))
    def test_returns_credentials_manager(
        self, mock_git_property, mock_credentials_class, config
    ):
        """Test credentials property returns CredentialsManager instance"""
        mock_git_property.get_domain.return_value = "gitlab.com"
        mock_credentials_instance = Mock(spec=CredentialsManager)
        mock_credentials_class.return_value = mock_credentials_instance

        result = config.credentials

        assert result == mock_credentials_instance
        mock_git_property.get_domain.assert_called_once()
        mock_credentials_class.assert_called_once_with(config.logger, "gitlab.com")

    @patch("gitlab_tui.config.config.CredentialsManager")
    @patch.object(Config, "git", new_callable=lambda: Mock(spec=GitContextResolver))
    def test_caches_credentials_manager(
        self, mock_git_property, mock_credentials_class, config
    ):
        """Test credentials property caches the CredentialsManager instance"""
        mock_git_property.get_domain.return_value = "gitlab.com"
        mock_credentials_instance = Mock(spec=CredentialsManager)
        mock_credentials_class.return_value = mock_credentials_instance

        first_call = config.credentials
        second_call = config.credentials

        assert first_call is second_call
        mock_git_property.get_domain.assert_called_once()  # Should only be called once due to caching
        mock_credentials_class.assert_called_once()


class TestGetConfigReader:
    """Test Config._get_config_reader"""

    @patch("gitlab_tui.config.config.ConfigReader")
    def test_returns_config_reader(self, mock_config_reader_class, config):
        """Test _get_config_reader returns ConfigReader instance"""
        mock_config_reader_instance = Mock(spec=ConfigReader)
        mock_config_reader_class.return_value = mock_config_reader_instance

        result = config._get_config_reader()

        assert result == mock_config_reader_instance
        mock_config_reader_class.assert_called_once_with(config.logger)

    @patch("gitlab_tui.config.config.ConfigReader")
    def test_caches_config_reader(self, mock_config_reader_class, config):
        """Test _get_config_reader caches the ConfigReader instance"""
        mock_config_reader_instance = Mock(spec=ConfigReader)
        mock_config_reader_class.return_value = mock_config_reader_instance

        first_call = config._get_config_reader()
        second_call = config._get_config_reader()

        assert first_call is second_call
        mock_config_reader_class.assert_called_once()  # Should only be called once due to caching


class TestConfigIntegration:
    """Test Config class integration scenarios"""

    @patch("gitlab_tui.config.config.GitContextResolver")
    @patch("gitlab_tui.config.config.ConfigReader")
    @patch("gitlab_tui.config.config.CredentialsManager")
    def test_multiple_properties_share_config_reader(
        self, mock_credentials_class, mock_config_reader_class, mock_git_class, config
    ):
        """Test that app, icons, and theme properties share the same ConfigReader instance"""
        # Setup mocks
        mock_git_instance = Mock(spec=GitContextResolver)
        mock_git_instance.get_domain.return_value = "gitlab.com"
        mock_git_class.return_value = mock_git_instance

        mock_config_reader_instance = Mock(spec=ConfigReader)
        mock_config_reader_instance.get_app_config.return_value = Mock(spec=AppConfig)
        mock_config_reader_instance.get_icons_config.return_value = Mock(
            spec=IconsConfig
        )
        mock_config_reader_instance.get_theme_config.return_value = Mock(
            spec=ThemeConfig
        )
        mock_config_reader_class.return_value = mock_config_reader_instance

        mock_credentials_instance = Mock(spec=CredentialsManager)
        mock_credentials_class.return_value = mock_credentials_instance

        # Access multiple properties
        _ = config.app
        _ = config.icons
        _ = config.theme

        # ConfigReader should only be instantiated once
        mock_config_reader_class.assert_called_once_with(config.logger)

    @patch("gitlab_tui.config.config.GitContextResolver")
    @patch("gitlab_tui.config.config.ConfigReader")
    @patch("gitlab_tui.config.config.CredentialsManager")
    def test_credentials_depends_on_git_domain(
        self, mock_credentials_class, mock_config_reader_class, mock_git_class, config
    ):
        """Test that credentials property correctly depends on git domain"""
        # Setup mocks
        mock_git_instance = Mock(spec=GitContextResolver)
        mock_git_instance.get_domain.return_value = "gitlab.example.com"
        mock_git_class.return_value = mock_git_instance

        mock_credentials_instance = Mock(spec=CredentialsManager)
        mock_credentials_class.return_value = mock_credentials_instance

        # Access credentials property
        result = config.credentials

        # Verify the domain was passed correctly
        mock_git_instance.get_domain.assert_called_once()
        mock_credentials_class.assert_called_once_with(
            config.logger, "gitlab.example.com"
        )
        assert result == mock_credentials_instance
