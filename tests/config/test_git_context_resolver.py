from logging import Logger
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import MagicMock, Mock, patch

import pytest

from gitlab_tui.config.git_context_resolver import GitContextResolver
from gitlab_tui.utils.exceptions import ConfigError


@pytest.fixture
def mock_logger():
    """Create a mock logger"""
    return Mock(spec=Logger)


@pytest.fixture
def git_resolver(mock_logger):
    """Create a GitContextResolver instance"""
    return GitContextResolver(mock_logger)


class TestGitContextResolverInit:
    """Test GitContextResolver.__init__"""

    def test_init_sets_logger(self, mock_logger):
        resolver = GitContextResolver(mock_logger)
        assert resolver.logger == mock_logger

    def test_init_sets_all_attributes_to_none(self, mock_logger):
        resolver = GitContextResolver(mock_logger)
        assert resolver._remote_url is None
        assert resolver._project_path is None
        assert resolver._domain is None
        assert resolver._current_branch is None


@patch("subprocess.run")
class TestInitRemoteUrl:
    """Test GitContextResolver._init_git_remote_url"""

    def test_returns_remote_url_successfully(self, mock_run, git_resolver):
        """Test successful retrieval of URL and any whitespace is stripped"""
        mock_run.return_value = MagicMock(
            stdout=" https://gitlab.com/user/project.git  \n", returncode=0
        )

        result = git_resolver._init_remote_url()

        assert result == "https://gitlab.com/user/project.git"
        mock_run.assert_called_once_with(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path.cwd(),
        )

    def test_raises_config_error_when_not_in_git_repo(self, mock_run, git_resolver):
        """Test error when not in a git repository"""
        mock_run.side_effect = CalledProcessError(1, "git")

        with pytest.raises(
            ConfigError, match="Not in a git repo or no remote configured"
        ):
            git_resolver._init_remote_url()

    def test_raises_config_error_when_git_not_found(self, mock_run, git_resolver):
        """Test error when git command is not found."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(ConfigError, match="Git command not found"):
            git_resolver._init_remote_url()


class TestGetProjectPathFromUrl:
    """Test GitContextResolver._get_project_path_from_url"""

    @pytest.mark.parametrize(
        "input, expected",
        [
            # HTTPS
            ("https://gitlab.com/group/project.git", "group/project"),
            ("https://gitlab.com/group/project", "group/project"),
            # SSH
            ("git@gitlab.com:group/project.git", "group/project"),
            ("git@gitlab.com:group/project", "group/project"),
            # HTTP
            ("http://gitlab.com/group/project.git", "group/project"),
            ("http://gitlab.com/group/project", "group/project"),
            # Nested subgroups
            ("https://gitlab.com/group/subgroup/project.git", "group/subgroup/project"),
            # Self hosted
            (
                "https://gitlab.company.com/group/subgroup/project",
                "group/subgroup/project",
            ),
        ],
    )
    def test_correctly_parses_remote_url(self, git_resolver, input, expected):
        """Test that the parser correctly returns the project path for all variations of inputs"""
        actual = git_resolver._get_project_path_from_url(input)

        assert actual == expected

    def test_fails_on_unepected_url_format(self, git_resolver):
        """Test that the error is returned when recieving malformed remote url"""
        remote_url = "git@gitlab.com//"

        with pytest.raises(ConfigError, match="Unexpected url format"):
            git_resolver._get_project_path_from_url(remote_url)


class TestGetDomainFromUrl:
    """Test GitContextResolver._get_domain_from_url"""

    @pytest.mark.parametrize(
        "input, expected",
        [
            # HTTPS
            ("https://gitlab.com/group/project.git", "gitlab.com"),
            ("https://gitlab.com/group/project", "gitlab.com"),
            # SSH
            ("git@gitlab.com:group/project.git", "gitlab.com"),
            ("git@gitlab.com:group/project", "gitlab.com"),
            # HTTP
            ("http://gitlab.com/group/project.git", "gitlab.com"),
            ("http://gitlab.com/group/project", "gitlab.com"),
            # Nested subgroups
            ("https://gitlab.com/group/subgroup/project.git", "gitlab.com"),
            # Self hosted
            (
                "https://gitlab.company.com/group/subgroup/project",
                "gitlab.company.com",
            ),
        ],
    )
    def test_correctly_parses_remote_url(self, git_resolver, input, expected):
        """Test that the parser correctly returns the domain for all variations of inputs"""
        actual = git_resolver._get_domain_from_url(input)

        assert actual == expected

    def test_fails_on_unepected_url_format(self, git_resolver):
        """Test that the error is returned when recieving malformed remote url"""
        remote_url = "git@gitlab.com//"

        with pytest.raises(ConfigError, match="Unexpected url format"):
            git_resolver._get_domain_from_url(remote_url)


@patch("subprocess.run")
class TestInitCurrentBranch:
    """Test GitContextResolver._init_current_branch"""

    def test_returns_current_branch_successfully(self, mock_run, git_resolver):
        """Test successful retrieval of current branch and any whitespace is stripped"""
        mock_run.return_value = MagicMock(
            stdout=" feature/mock_branch_name \n", returncode=0
        )

        result = git_resolver._init_current_branch()

        assert result == "feature/mock_branch_name"
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path.cwd(),
        )

    def test_raises_config_error_when_not_in_git_repo(self, mock_run, git_resolver):
        """Test error when not in a git repository"""
        mock_run.side_effect = CalledProcessError(1, "git")

        with pytest.raises(ConfigError, match="Could not determine current branch"):
            git_resolver._init_current_branch()


class TestGetRemoteUrl:
    """Test GitContextResolver.get_remote_url"""

    @patch.object(GitContextResolver, "_init_remote_url")
    def test_returns_remote_url_successfully(self, mock_remote, mock_logger):
        """Test successful retrieval of remote url with lazy initialization"""
        expected = "https://gitlab.com/group/project.git"
        mock_remote.return_value = expected

        resolver = GitContextResolver(mock_logger)
        actual = resolver.get_remote_url()

        assert actual == expected
        mock_remote.assert_called_once()

    @patch.object(GitContextResolver, "_init_remote_url")
    def test_caches_remote_url_on_subsequent_calls(self, mock_remote, mock_logger):
        """Test that remote url is cached after first call"""
        expected = "https://gitlab.com/group/project.git"
        mock_remote.return_value = expected

        resolver = GitContextResolver(mock_logger)
        first_call = resolver.get_remote_url()
        second_call = resolver.get_remote_url()

        assert first_call == expected
        assert second_call == expected
        mock_remote.assert_called_once()  # Should only be called once due to caching


class TestGetDomain:
    """Test GitContextResolver.get_domain"""

    @patch.object(GitContextResolver, "get_remote_url")
    @patch.object(GitContextResolver, "_get_domain_from_url")
    def test_returns_domain_successfully(
        self, mock_get_domain, mock_remote_url, mock_logger
    ):
        """Test successful retrieval of domain with lazy initialization"""
        mock_remote_url.return_value = "https://gitlab.company.com/group/project.git"
        expected = "gitlab.company.com"
        mock_get_domain.return_value = expected

        resolver = GitContextResolver(mock_logger)
        actual = resolver.get_domain()

        assert actual == expected
        mock_remote_url.assert_called_once()
        mock_get_domain.assert_called_once_with(
            "https://gitlab.company.com/group/project.git"
        )

    @patch.object(GitContextResolver, "get_remote_url")
    @patch.object(GitContextResolver, "_get_domain_from_url")
    def test_caches_domain_on_subsequent_calls(
        self, mock_get_domain, mock_remote_url, mock_logger
    ):
        """Test that domain is cached after first call"""
        mock_remote_url.return_value = "https://gitlab.company.com/group/project.git"
        expected = "gitlab.company.com"
        mock_get_domain.return_value = expected

        resolver = GitContextResolver(mock_logger)
        first_call = resolver.get_domain()
        second_call = resolver.get_domain()

        assert first_call == expected
        assert second_call == expected
        mock_remote_url.assert_called_once()  # Should only be called once due to caching
        mock_get_domain.assert_called_once()  # Should only be called once due to caching


class TestGetProjectPath:
    """Test GitContextResolver.get_project_path"""

    @patch.object(GitContextResolver, "get_remote_url")
    @patch.object(GitContextResolver, "_get_project_path_from_url")
    def test_returns_project_path_successfully(
        self, mock_get_path, mock_remote_url, mock_logger
    ):
        """Test successful retrieval of project path with lazy initialization"""
        mock_remote_url.return_value = "https://gitlab.com/group/project.git"
        expected = "group/project"
        mock_get_path.return_value = expected

        resolver = GitContextResolver(mock_logger)
        actual = resolver.get_project_path()

        assert actual == expected
        mock_remote_url.assert_called_once()
        mock_get_path.assert_called_once_with("https://gitlab.com/group/project.git")

    @patch.object(GitContextResolver, "get_remote_url")
    @patch.object(GitContextResolver, "_get_project_path_from_url")
    def test_caches_project_path_on_subsequent_calls(
        self, mock_get_path, mock_remote_url, mock_logger
    ):
        """Test that project path is cached after first call"""
        mock_remote_url.return_value = "https://gitlab.com/group/project.git"
        expected = "group/project"
        mock_get_path.return_value = expected

        resolver = GitContextResolver(mock_logger)
        first_call = resolver.get_project_path()
        second_call = resolver.get_project_path()

        assert first_call == expected
        assert second_call == expected
        mock_remote_url.assert_called_once()  # Should only be called once due to caching
        mock_get_path.assert_called_once()  # Should only be called once due to caching


class TestCurrentBranch:
    """Test GitContextResolver.get_current_branch"""

    @patch.object(GitContextResolver, "_init_current_branch")
    def test_returns_current_branch_successfully(self, mock_branch, mock_logger):
        """Test successful retrieval of current branch with lazy initialization"""
        expected = "feature/mock_branch_name"
        mock_branch.return_value = expected

        resolver = GitContextResolver(mock_logger)
        actual = resolver.get_current_branch()

        assert actual == expected
        mock_branch.assert_called_once()

    @patch.object(GitContextResolver, "_init_current_branch")
    def test_caches_current_branch_on_subsequent_calls(self, mock_branch, mock_logger):
        """Test that current branch is cached after first call"""
        expected = "feature/mock_branch_name"
        mock_branch.return_value = expected

        resolver = GitContextResolver(mock_logger)
        first_call = resolver.get_current_branch()
        second_call = resolver.get_current_branch()

        assert first_call == expected
        assert second_call == expected
        mock_branch.assert_called_once()  # Should only be called once due to caching
