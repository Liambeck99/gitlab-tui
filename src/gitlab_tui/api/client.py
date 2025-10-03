import time
import urllib.parse
from logging import Logger
from typing import Literal, Union, overload

from requests import HTTPError, Session
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import RequestException, Timeout


class GitLabAPIError(Exception):
    """Custom exception for GitLab API errors."""


class GitlabAPI:
    """GitLab API client for fetching pipeline and project data."""

    SESSION_MAX_RETRIES = 3
    SESSION_BACKOFF_FACTOR = 0.3
    SESSION_ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE"}
    SESSION_POOL_CONNECTIONS = 10
    SESSION_POOL_MAXSIZE = 20
    REQUEST_TIMEOUT = 30  # seconds

    def __init__(self, logger: Logger, base_url: str, auth_token: str):
        # Remove trailing slash from base_url
        self._base_url = base_url.rstrip("/")

        self._session = self._create_session(auth_token)

        # Setup logger
        self.logger = logger
        self.logger.info(f"GitLab API client initialized for: {self._base_url}")

    def _create_auth_headers(self, auth_token: str) -> dict:
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

    def _create_session(self, auth_token: str) -> Session:
        session = Session()

        retry_strategy = Retry(
            total=self.SESSION_MAX_RETRIES,
            backoff_factor=self.SESSION_BACKOFF_FACTOR,
            allowed_methods=self.SESSION_ALLOWED_METHODS,
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.SESSION_POOL_CONNECTIONS,
            pool_maxsize=self.SESSION_POOL_MAXSIZE,
            pool_block=False,
        )

        session.mount("https://", adapter)

        auth_headers = self._create_auth_headers(auth_token)

        session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                **auth_headers,
            }
        )

        return session

    @overload
    def _make_request(
        self, method: str, endpoint: str, expect_list: Literal[True], **kwargs
    ) -> list: ...

    @overload
    def _make_request(
        self, method: str, endpoint: str, expect_list: Literal[False], **kwargs
    ) -> dict: ...

    @overload
    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict: ...

    def _make_request(
        self, method: str, endpoint: str, expect_list: bool = False, **kwargs
    ) -> Union[list, dict]:
        """Make a request to the GitLab API with proper error handling."""
        url = f"{self._base_url}/api/v4{endpoint}"
        self.logger.debug(f"Making {method} request to: {url}")

        # Log request parameters (excluding sensitive data)
        if "params" in kwargs:
            self.logger.debug(f"Request params: {kwargs['params']}")

        start_time = time.time()

        try:
            response = self._session.request(
                method=method, url=url, timeout=self.REQUEST_TIMEOUT, **kwargs
            )

            elapsed = time.time() - start_time
            self.logger.debug(
                f"Request completed in {elapsed:.3f}s - Status: {response.status_code}"
            )

            response.raise_for_status()
            result = response.json()

            # Log response size
            if isinstance(result, list):
                self.logger.debug(f"Response contains {len(result)} items")
            elif isinstance(result, dict):
                self.logger.debug(
                    f"Response contains dict with keys: {list(result.keys())[:5]}..."
                )  # First 5 keys

            return result

        except Timeout:
            self.logger.error(f"Request timeout after {self.REQUEST_TIMEOUT}s: {url}")
            raise GitLabAPIError(f"Request timed out: {url}")
        except HTTPError as e:
            elapsed = time.time() - start_time
            self.logger.error(
                f"HTTP error after {elapsed:.3f}s - Status {e.response.status_code}: {url}"
            )
            if e.response.status_code == 401:
                raise GitLabAPIError("Authentication failed. Check your GitLab token.")
            elif e.response.status_code == 403:
                raise GitLabAPIError("Access forbidden. Check your permissions.")
            elif e.response.status_code == 404:
                raise GitLabAPIError(f"Resource not found: {endpoint}")
            else:
                error_response_text = e.response.text
                if len(error_response_text) > 200:
                    error_text = error_response_text[:200]
                else:
                    error_text = error_response_text

                raise GitLabAPIError(f"HTTP {e.response.status_code}: {error_text}")
        except RequestException as e:
            elapsed = time.time() - start_time
            self.logger.error(f"Request exception after {elapsed:.3f}s: {str(e)}")
            raise GitLabAPIError(f"Request failed: {str(e)}")

    def _parse_project(self, project: str | int) -> str:
        """Returns the project id/path in correct format"""
        # URL-encode the project path if it's a string
        project_param: str
        if isinstance(project, str):
            project_param = urllib.parse.quote(project, safe="")
        else:
            project_param = str(project)

        return project_param

    def get_project(self, project: Union[int, str]) -> dict:
        """Get project information.

        Args:
            project: The project ID (integer) or URL-encoded project path (string)

        Returns:
            dict: Project information
        """
        project_param = self._parse_project(project)

        return self._make_request("GET", f"/projects/{project_param}")

    def get_pipelines(
        self, project: Union[int, str], ref: str = "master", per_page: int = 10
    ) -> list[dict]:
        """Get pipelines for a project.

        Args:
            project: The project ID (integer) or URL-encoded project path (string)
            ref: Git reference (branch/tag) to filter by
            per_page: Number of pipelines to return

        Returns:
            list: List of pipeline objects
        """
        project_param = self._parse_project(project)
        params = {"ref": ref, "per_page": per_page, "order_by": "id", "sort": "desc"}

        return self._make_request(
            "GET",
            f"/projects/{project_param}/pipelines",
            params=params,
            expect_list=True,
        )

    def get_pipeline_jobs(
        self, project: Union[int, str], pipeline_id: int
    ) -> list[dict]:
        """Get jobs for a specific pipeline.

        Args:
            project: The project ID (integer) or URL-encoded project path (string)
            pipeline_id: The pipeline ID

        Returns:
            list: List of job objects
        """
        project_param = self._parse_project(project)

        return self._make_request(
            "GET",
            f"/projects/{project_param}/pipelines/{pipeline_id}/jobs",
            expect_list=True,
        )

    def get_pipeline_details(self, project: Union[int, str], pipeline_id: int) -> dict:
        """Get detailed information about a specific pipeline.

        Args:
            project: The project ID (integer) or URL-encoded project path (string)
            pipeline_id: The pipeline ID

        Returns:
            dict: Pipeline details
        """
        project_param = self._parse_project(project)

        return self._make_request(
            "GET", f"/projects/{project_param}/pipelines/{pipeline_id}"
        )
