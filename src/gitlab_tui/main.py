#!/usr/bin/env python3
"""GitLab TUI - A terminal interface for GitLab pipelines and more."""
import os
import sys

from gitlab_tui.api.client import GitlabAPI
from gitlab_tui.api.mock.mock_client import MockGitlabAPI
from gitlab_tui.app import GitLabTUI
from gitlab_tui.config.config import Config
from gitlab_tui.utils.exceptions import ConfigError
from gitlab_tui.utils.logger import get_logger
from gitlab_tui.utils.parse_args import parse_args


def main() -> None:
    """Main entry point for the GitLab TUI application."""

    try:
        args = parse_args()
        logger = get_logger()

        config = Config(logger=logger)

        # Get GitLab configuration
        gitlab_domain = config.git.get_domain()
        gitlab_project = args.project or config.git.get_project_path()
        gitlab_branch = args.branch or config.git.get_current_branch()
        gitlab_token = config.credentials.get_token()

        # Build GitLab URL from domain
        gitlab_url = f"https://{gitlab_domain}"

        gitlab_api: GitlabAPI
        mock_mode = os.getenv("MOCK_MODE", "").lower() in ("true", "1", "yes")
        if mock_mode:
            gitlab_api = MockGitlabAPI()
        else:
            gitlab_api = GitlabAPI(
                logger=logger, base_url=gitlab_url, auth_token=gitlab_token
            )

        app = GitLabTUI(
            logger=logger,
            gitlab_api=gitlab_api,
            config=config,
            project=gitlab_project,
            branch=gitlab_branch,
        )
        app.run()

    except ConfigError as e:
        # Log the full error for debugging
        logger.error(f"Configuration error: {e}", exc_info=True)
        # Show clean error message to user
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        # Log unexpected errors with full stack trace
        logger.error(f"Unexpected error: {e}", exc_info=True)
        # Show generic error message to user
        print(
            f"Unexpected error occurred. Check logs for details: {e}", file=sys.stderr
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
