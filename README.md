# GitLab TUI (WIP)

A TUI application for interacting with GitLab pipelines and jobs.

<img width="1400" height="750" alt="Image" src="https://github.com/user-attachments/assets/774963f3-d074-4f2c-b5e7-811f1a70e958" />

## Setup

### Credentials

Create a credentials file at `~/.config/gitlab-tui/credentials` with your GitLab personal access token:

```toml
["gitlab.com"]
token = "your_personal_access_token_here"

# For self-hosted GitLab
["gitlab.example.com"]
token = "your_token_here"
```

> **Note**: Use quotes around domain names containing dots.
