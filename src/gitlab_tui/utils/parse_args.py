from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter


def parse_args() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(
        description="GitLab TUI - Terminal interface for GitLab pipelines",
        formatter_class=RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitlab-tui --project foo/bar
  gitlab-tui --project 12345 --branch main
  gitlab-tui --gitlab-url https://gitlab.example.com --project mygroup/myproject
        """,
    )

    parser.add_argument(
        "--project",
        dest="project",
        help="GitLab project ID or path (e.g., 'group/project' or '12345')",
    )

    parser.add_argument(
        "--branch",
        dest="branch",
        help="Default branch to display (default: main)",
    )

    return parser.parse_args()
