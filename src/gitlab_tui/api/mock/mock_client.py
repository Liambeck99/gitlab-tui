import logging
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Union

from gitlab_tui.api.client import GitlabAPI
from gitlab_tui.api.mock.consts import (
    BRANCH_NAMES,
    COMMIT_MESSAGES,
    JOB_NAMES,
    STAGES,
    STATUSES,
    USERS,
)


class MockGitlabAPI(GitlabAPI):
    """GitLab API client for fetching pipeline and project data."""

    def __init__(self):
        # Remove trailing slash from base_url
        self._base_url = "https://mock-gitlab.com"

        # Setup logger
        self.logger = logging.getLogger("gitlab_tui.api")
        self.logger.info(
            "GitLab API client initialized in MOCK MODE - no real API calls will be made"
        )

    def _random_datetime(self, days_ago: int = 7) -> str:
        """Generate a random datetime within the last N days."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(days=days_ago)
        random_time = start_time + timedelta(
            seconds=random.randint(0, int((now - start_time).total_seconds()))
        )
        return random_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _random_sha(self, length: int = 40) -> str:
        return "".join(random.choices(string.hexdigits.lower(), k=length))  # nosec B311

    def get_project(self, project: Union[int, str]) -> dict:
        return {
            "id": 3,
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "description_html": '<p data-sourcepos="1:1-1:56" dir="auto">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>',
            "default_branch": "main",
            "visibility": "private",
            "ssh_url_to_repo": "git@example.com:diaspora/diaspora-project-site.git",
            "http_url_to_repo": "http://example.com/diaspora/diaspora-project-site.git",
            "web_url": "http://example.com/diaspora/diaspora-project-site",
            "readme_url": "http://example.com/diaspora/diaspora-project-site/blob/main/README.md",
            "tag_list": ["example", "disapora project"],
            "topics": ["example", "disapora project"],
            "owner": {
                "id": 3,
                "name": "Diaspora",
                "created_at": "2013-09-30T13:46:02Z",
            },
            "name": "Diaspora Project Site",
            "name_with_namespace": "Diaspora / Diaspora Project Site",
            "path": "diaspora-project-site",
            "path_with_namespace": "diaspora/diaspora-project-site",
            "issues_enabled": True,
            "open_issues_count": 1,
            "merge_requests_enabled": True,
            "jobs_enabled": True,
            "wiki_enabled": True,
            "snippets_enabled": False,
            "can_create_merge_request_in": True,
            "resolve_outdated_diff_discussions": False,
            "container_registry_enabled": False,
            "container_registry_access_level": "disabled",
            "security_and_compliance_access_level": "disabled",
            "container_expiration_policy": {
                "cadence": "7d",
                "enabled": False,
                "keep_n": None,
                "older_than": None,
                "name_regex": None,
                "name_regex_delete": None,
                "name_regex_keep": None,
                "next_run_at": "2020-01-07T21:42:58.658Z",
            },
            "created_at": "2013-09-30T13:46:02Z",
            "updated_at": "2013-09-30T13:46:02Z",
            "last_activity_at": "2013-09-30T13:46:02Z",
            "creator_id": 3,
            "namespace": {
                "id": 3,
                "name": "Diaspora",
                "path": "diaspora",
                "kind": "group",
                "full_path": "diaspora",
                "avatar_url": "http://localhost:3000/uploads/group/avatar/3/foo.jpg",
                "web_url": "http://localhost:3000/groups/diaspora",
            },
            "import_url": None,
            "import_type": None,
            "import_status": "none",
            "import_error": None,
            "permissions": {
                "project_access": {"access_level": 10, "notification_level": 3},
                "group_access": {"access_level": 50, "notification_level": 3},
            },
            "archived": False,
            "avatar_url": "http://example.com/uploads/project/avatar/3/uploads/avatar.png",
            "license_url": "http://example.com/diaspora/diaspora-client/blob/main/LICENSE",
            "license": {
                "key": "lgpl-3.0",
                "name": "GNU Lesser General Public License v3.0",
                "nickname": "GNU LGPLv3",
                "html_url": "http://choosealicense.com/licenses/lgpl-3.0/",
                "source_url": "http://www.gnu.org/licenses/lgpl-3.0.txt",
            },
            "shared_runners_enabled": True,
            "group_runners_enabled": True,
            "forks_count": 0,
            "star_count": 0,
            "runners_token": self._random_sha(20),
            "ci_default_git_depth": 50,
            "ci_forward_deployment_enabled": True,
            "ci_forward_deployment_rollback_allowed": True,
            "ci_allow_fork_pipelines_to_run_in_parent_project": True,
            "ci_id_token_sub_claim_components": ["project_path", "ref_type", "ref"],
            "ci_separated_caches": True,
            "ci_restrict_pipeline_cancellation_role": "developer",
            "ci_pipeline_variables_minimum_override_role": "maintainer",
            "ci_push_repository_for_job_token_allowed": False,
            "public_jobs": True,
            "shared_with_groups": [
                {
                    "group_id": 4,
                    "group_name": "Twitter",
                    "group_full_path": "twitter",
                    "group_access_level": 30,
                },
                {
                    "group_id": 3,
                    "group_name": "Gitlab Org",
                    "group_full_path": "gitlab-org",
                    "group_access_level": 10,
                },
            ],
            "repository_storage": "default",
            "only_allow_merge_if_pipeline_succeeds": False,
            "allow_merge_on_skipped_pipeline": False,
            "allow_pipeline_trigger_approve_deployment": False,
            "restrict_user_defined_variables": False,
            "only_allow_merge_if_all_discussions_are_resolved": False,
            "remove_source_branch_after_merge": False,
            "printing_merge_requests_link_enabled": True,
            "request_access_enabled": False,
            "merge_method": "merge",
            "squash_option": "default_on",
            "auto_devops_enabled": True,
            "auto_devops_deploy_strategy": "continuous",
            "approvals_before_merge": 0,
            "mirror": False,
            "mirror_user_id": 45,
            "mirror_trigger_builds": False,
            "only_mirror_protected_branches": False,
            "mirror_overwrites_diverged_branches": False,
            "external_authorization_classification_label": None,
            "packages_enabled": True,
            "service_desk_enabled": False,
            "service_desk_address": None,
            "autoclose_referenced_issues": True,
            "suggestion_commit_message": None,
            "enforce_auth_checks_on_uploads": True,
            "merge_commit_template": None,
            "squash_commit_template": None,
            "issue_branch_template": "gitlab/%{id}-%{title}",
            "marked_for_deletion_at": "2020-04-03",
            "marked_for_deletion_on": "2020-04-03",
            "compliance_frameworks": ["sox"],
            "warn_about_potentially_unwanted_characters": True,
            "secret_push_protection_enabled": False,
            "statistics": {
                "commit_count": 37,
                "storage_size": 1038090,
                "repository_size": 1038090,
                "wiki_size": 0,
                "lfs_objects_size": 0,
                "job_artifacts_size": 0,
                "pipeline_artifacts_size": 0,
                "packages_size": 0,
                "snippets_size": 0,
                "uploads_size": 0,
                "container_registry_size": 0,
            },
            "container_registry_image_prefix": "registry.example.com/diaspora/diaspora-client",
            "_links": {
                "self": "http://example.com/api/v4/projects",
                "issues": "http://example.com/api/v4/projects/1/issues",
                "merge_requests": "http://example.com/api/v4/projects/1/merge_requests",
                "repo_branches": "http://example.com/api/v4/projects/1/repository_branches",
                "labels": "http://example.com/api/v4/projects/1/labels",
                "events": "http://example.com/api/v4/projects/1/events",
                "members": "http://example.com/api/v4/projects/1/members",
                "cluster_agents": "http://example.com/api/v4/projects/1/cluster_agents",
            },
            "spp_repository_pipeline_access": False,
        }

    def get_pipelines(
        self, project: Union[int, str], ref: str = "master", per_page: int = 10
    ) -> list[dict]:
        pipelines = []
        for i in range(per_page):
            pipeline_id = 50000 + i
            pipeline = {
                "id": pipeline_id,
                "iid": i + 1,
                "project_id": 12345,
                "status": random.choice(STATUSES),
                "source": "push",
                "ref": random.choice(BRANCH_NAMES) if i > 0 else ref,
                "sha": f"a{random.randint(100000, 999999)}b{random.randint(100000, 999999)}",
                "web_url": f"https://gitlab.example.com/company/awesome-web-app/-/pipelines/{pipeline_id}",
                "created_at": self._random_datetime(),
                "updated_at": self._random_datetime(),
            }
            pipelines.append(pipeline)
        return pipelines

    def get_pipeline_jobs(self, project: Union[int, str], pipeline_id: int) -> list:
        jobs = []
        for _ in range(10):
            user_name, user_email = random.choice(USERS)
            commit_message = random.choice(COMMIT_MESSAGES)
            stage = random.choice(STAGES)
            job_name = random.choice(JOB_NAMES[stage])
            job = {
                "commit": {
                    "author_email": user_email,
                    "author_name": user_name,
                    "created_at": self._random_datetime(),
                    "id": self._random_sha(),
                    "message": commit_message,
                    "short_id": "0ff3ae19",
                    "title": commit_message,
                },
                "coverage": None,
                "archived": False,
                "source": "push",
                "allow_failure": False,
                "created_at": "2015-12-24T15:51:21.802Z",
                "started_at": "2015-12-24T17:54:27.722Z",
                "finished_at": "2015-12-24T17:54:27.895Z",
                "erased_at": None,
                "duration": 0.173,
                "queued_duration": 0.010,
                "artifacts_file": {"filename": "artifacts.zip", "size": 1000},
                "artifacts": [
                    {
                        "file_type": "archive",
                        "size": 1000,
                        "filename": "artifacts.zip",
                        "file_format": "zip",
                    },
                    {
                        "file_type": "metadata",
                        "size": 186,
                        "filename": "metadata.gz",
                        "file_format": "gzip",
                    },
                    {
                        "file_type": "trace",
                        "size": 1500,
                        "filename": "job.log",
                        "file_format": "raw",
                    },
                    {
                        "file_type": "junit",
                        "size": 750,
                        "filename": "junit.xml.gz",
                        "file_format": "gzip",
                    },
                ],
                "artifacts_expire_at": "2016-01-23T17:54:27.895Z",
                "tag_list": ["docker runner", "ubuntu18"],
                "id": 7,
                "name": job_name,
                "pipeline": {
                    "id": pipeline_id,
                    "project_id": project,
                    "ref": "main",
                    "sha": self._random_sha(),
                    "status": "pending",
                },
                "ref": random.choice(BRANCH_NAMES),
                "runner": {
                    "id": 32,
                    "description": "",
                    "ip_address": None,
                    "active": True,
                    "paused": False,
                    "is_shared": True,
                    "runner_type": "instance_type",
                    "name": None,
                    "online": False,
                    "status": "offline",
                },
                "runner_manager": {
                    "id": 1,
                    "system_id": "s_89e5e9956577",
                    "version": "16.11.1",
                    "revision": "535ced5f",
                    "platform": "linux",
                    "architecture": "amd64",
                    "created_at": "2024-05-01T10:12:02.507Z",
                    "contacted_at": "2024-05-07T06:30:09.355Z",
                    "ip_address": "127.0.0.1",
                    "status": "offline",
                },
                "stage": stage,
                "status": random.choice(STATUSES),
                "failure_reason": "script_failure",
                "tag": False,
                "web_url": "https://example.com/foo/bar/-/jobs/7",
                "project": {"ci_job_token_scope_enabled": False},
                "user": {
                    "id": 1,
                    "name": "Administrator",
                    "username": "root",
                    "state": "active",
                    "avatar_url": "http://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon",
                    "web_url": "http://gitlab.dev/root",
                    "created_at": "2015-12-21T13:14:24.077Z",
                    "bio": None,
                    "location": None,
                    "public_email": "",
                    "linkedin": "",
                    "twitter": "",
                    "website_url": "",
                    "organization": "",
                },
            }
            jobs.append(job)
        return jobs

    def get_pipeline_details(self, project: Union[int, str], pipeline_id: int) -> dict:
        return {
            "id": 287,
            "iid": 144,
            "project_id": 21,
            "name": "Build pipeline",
            "sha": self._random_sha(),
            "ref": "main",
            "status": "success",
            "source": "push",
            "created_at": "2022-09-21T01:05:07.200Z",
            "updated_at": "2022-09-21T01:05:50.185Z",
            "web_url": "http://127.0.0.1:3000/test-group/test-project/-/pipelines/287",
            "before_sha": self._random_sha(),
            "tag": False,
            "yaml_errors": None,
            "user": {
                "id": 1,
                "username": "root",
                "name": "Administrator",
                "state": "active",
                "avatar_url": "https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon",
                "web_url": "http://127.0.0.1:3000/root",
            },
            "started_at": "2022-09-21T01:05:14.197Z",
            "finished_at": "2022-09-21T01:05:50.175Z",
            "committed_at": None,
            "duration": 34,
            "queued_duration": 6,
            "coverage": None,
            "detailed_status": {
                "icon": "status_success",
                "text": "passed",
                "label": "passed",
                "group": "success",
                "tooltip": "passed",
                "has_details": False,
                "details_path": "/test-group/test-project/-/pipelines/287",
                "illustration": None,
                "favicon": "/assets/ci_favicons/favicon_status_success-8451333011eee8ce9f2ab25dc487fe24a8758c694827a582f17f42b0a90446a2.png",
            },
        }
