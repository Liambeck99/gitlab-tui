from logging import Logger
from pathlib import Path
from textwrap import dedent
from unittest.mock import Mock, patch

import pytest

from gitlab_tui.config.credentials_reader import CredentialsManager
from gitlab_tui.utils.exceptions import ConfigError


@pytest.fixture
def mock_logger():
    """Create a mock logger"""
    return Mock(spec=Logger)


@pytest.fixture
def credentials_manager(mock_logger, tmp_path, monkeypatch):
    """Create a CredentialsManager instance"""
    monkeypatch.setattr(CredentialsManager, "CONFIG_DIR", tmp_path)
    manager = CredentialsManager(mock_logger, "gitlab.com")

    return manager


class TestCredentialsManagerInit:
    """Test CredentialsManager.__init__"""

    def test_init_sets_logger(self, mock_logger):
        manager = CredentialsManager(mock_logger, "gitlab.com")
        assert manager.logger == mock_logger

    def test_init_sets_domain(self, mock_logger):
        manager = CredentialsManager(mock_logger, "gitlab.example.com")
        assert manager.domain == "gitlab.example.com"

    def test_init_sets_credentials_file_path(self, mock_logger):
        manager = CredentialsManager(mock_logger, "gitlab.com")
        expected_path = Path.home() / ".config" / "gitlab-tui" / "credentials"
        assert manager.credentials_file == expected_path

    def test_init_sets_token_to_none(self, mock_logger):
        manager = CredentialsManager(mock_logger, "gitlab.com")
        assert manager._token is None


class TestLoadToken:
    """Test CredentialsManager._load_token"""

    def test_errors_if_file_not_found(self, credentials_manager):
        expected_message = (
            f"Credentials file not found at {credentials_manager.credentials_file}"
        )
        with pytest.raises(ConfigError, match=expected_message):
            credentials_manager._load_token()

    def test_errors_if_domain_config_missing(self, credentials_manager):
        with open(credentials_manager.credentials_file, "w") as f:
            content = """
            ["gitlab.company_a.com"]
            token = "mock_token_a"

            ["gitlab.company_b.com"]
            token = "mock_token_b"
            """
            f.write(dedent(content).strip())

        expected_message = f"No configuration found for '{credentials_manager.domain}'"
        with pytest.raises(ConfigError, match=expected_message):
            credentials_manager._load_token()

    def test_errors_if_config_missing_token(self, credentials_manager):
        with open(credentials_manager.credentials_file, "w") as f:
            content = """
            ["gitlab.company_a.com"]
            token = "mock_token_a"

            ["gitlab.company_b.com"]
            token = "mock_token_b"

            ["gitlab.com"]
            foo = "bar"
            """
            f.write(dedent(content).strip())

        expected_message = f"No token found for '{credentials_manager.domain}'"
        with pytest.raises(ConfigError, match=expected_message):
            credentials_manager._load_token()

    def test_returns_the_correct_token(self, credentials_manager):
        with open(credentials_manager.credentials_file, "w") as f:
            content = """
            ["gitlab.company_a.com"]
            token = "mock_token_a"

            ["gitlab.company_b.com"]
            token = "mock_token_b"

            ["gitlab.com"]
            foo = "bar"
            token = "mock_token"
            """
            f.write(dedent(content).strip())

        expected = "mock_token"
        actual = credentials_manager._load_token()
        assert actual == expected


class TestGetToken:
    """Test CredentialsManager.get_token"""

    @patch.object(CredentialsManager, "_load_token")
    def test_returns_token_successfully(self, mock_load_token, mock_logger):
        """Test successful retrieval of token with lazy initialization"""
        expected = "mock_token"
        mock_load_token.return_value = expected

        manager = CredentialsManager(mock_logger, "gitlab.com")
        actual = manager.get_token()

        assert actual == expected
        mock_load_token.assert_called_once()

    @patch.object(CredentialsManager, "_load_token")
    def test_caches_token_on_subsequent_calls(self, mock_load_token, mock_logger):
        """Test that token is cached after first call"""
        expected = "mock_token"
        mock_load_token.return_value = expected

        manager = CredentialsManager(mock_logger, "gitlab.com")
        first_call = manager.get_token()
        second_call = manager.get_token()

        assert first_call == expected
        assert second_call == expected
        mock_load_token.assert_called_once()  # Should only be called once due to caching
