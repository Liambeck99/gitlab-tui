#!/usr/bin/env python3
"""GitLab TUI - A terminal interface for GitLab pipelines and more."""
import os

from gitlab_tui.api.client import GitlabAPI
from gitlab_tui.api.mock.mock_client import MockGitlabAPI
from gitlab_tui.app import GitLabTUI
from gitlab_tui.config.manager import ConfigManager


def main() -> None:
    """Main entry point for the GitLab TUI application."""

    config_manager = ConfigManager()
    gitlab_token = config_manager.get_token()
    config = config_manager.get_config()

    gitlab_api: GitlabAPI
    mock_mode = os.getenv("MOCK_MODE", "").lower() in ("true", "1", "yes")
    if mock_mode:
        gitlab_api = MockGitlabAPI()
    else:
        gitlab_api = GitlabAPI(base_url=config.gitlab.url, auth_token=gitlab_token)

    app = GitLabTUI(
        gitlab_api=gitlab_api,
        config=config_manager.get_config(),
    )
    app.run()


if __name__ == "__main__":
    main()
