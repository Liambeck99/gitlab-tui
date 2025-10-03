"""Main GitLab TUI application."""

import asyncio
import os
from logging import Formatter, Handler, Logger
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.message import Message
from textual.reactive import reactive
from textual.theme import Theme
from textual.widgets import Footer, Header, RichLog, TabbedContent, TabPane

from gitlab_tui.api.client import GitlabAPI, GitLabAPIError
from gitlab_tui.config.manager import AppConfig
from gitlab_tui.ui.components.pipeline_main_view import PipelineMainView
from gitlab_tui.ui.components.pipeline_sidebar import PipelineSidebar


class GitLabTUI(App):
    """A TUI application for interacting with GitLab."""

    CSS_PATH = "styles.tcss"
    TITLE = "GitLab TUI"

    BINDINGS: list[Binding] = [  # type: ignore
        # Vim-style navigation (map to directional actions)
        Binding("h", "focus_left", "Focus left"),
        Binding("l", "focus_right", "Focus right"),
        Binding("j", "down", "Move down"),
        Binding("k", "up", "Move up"),
        Binding("g,g", "scroll_home", "Go to top"),
        Binding("G", "scroll_end", "Go to bottom"),
        # Application controls
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh data"),
        Binding("d", "toggle_dark", "Toggle dark mode"),
        # Debug mode
        Binding("ctrl+shift+d", "toggle_debug", "Toggle debug panel"),
        # Quick help
        Binding("?", "show_help", "Show help"),
    ]

    # Reactive attributes
    selected_pipeline_id: reactive[Optional[int]] = reactive(None)
    loading: reactive[bool] = reactive(False)
    error_message: reactive[Optional[str]] = reactive(None)
    debug_panel_visible: reactive[bool] = reactive(False)

    def __init__(self, logger: Logger, gitlab_api: GitlabAPI, config: AppConfig):
        super().__init__()
        self.config = config

        # Setup debug mode
        self.debug_mode = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        self.debug_keys = os.getenv("DEBUG_KEYS", "").lower() in ("true", "1", "yes")
        self.debug_panel_visible = self.debug_mode

        self.gitlab_api = gitlab_api
        self.project = config.gitlab.project  # Can be ID (int) or path (str)
        self.branch = config.gitlab.branch
        self.pipelines_data: list = []
        self.current_pipeline_jobs: list = []

        # Setup logger for this instance
        self.logger = logger
        self.logger.info(
            f"GitLab TUI starting - Debug mode: {self.debug_mode}, Debug keys: {self.debug_keys}"
        )

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Vertical():
            # Main content area
            with TabbedContent(initial="pipelines", id="main-content"):
                with TabPane("Pipelines", id="pipelines"):
                    with Horizontal():
                        yield PipelineSidebar(
                            logger=self.logger,
                            config=self.config,
                            id="pipeline-sidebar",
                        )
                        yield PipelineMainView(
                            logger=self.logger, config=self.config, id="pipeline-main"
                        )

            # Debug panel (initially hidden unless debug mode)
            yield RichLog(
                id="debug-log",
                classes="debug-panel" + ("" if self.debug_panel_visible else " hidden"),
            )

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the app when it's mounted."""
        self._setup_rich_log_handler()
        self._setup_debug_logging()

        theme = Theme(**self.config.theme.__dict__)
        self.register_theme(theme)
        self.theme = self.config.theme.name

        await self.load_initial_data()

    def _setup_rich_log_handler(self) -> None:
        """Setup RichLog handler for live debug output."""
        debug_log = self.query_one("#debug-log", RichLog)

        # Create custom handler that writes to RichLog
        class RichLogHandler(Handler):
            def __init__(self, rich_log_widget):
                super().__init__()
                self.rich_log = rich_log_widget

            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.rich_log.write(msg)
                except Exception:
                    pass  # nosec B110 Ignore errors in logging

        # Add RichLog handler to logger
        rich_handler = RichLogHandler(debug_log)
        rich_formatter = Formatter("%(levelname)s - %(message)s")
        rich_handler.setFormatter(rich_formatter)
        self.logger.addHandler(rich_handler)

    def _setup_debug_logging(self) -> None:
        """Setup debug logging for navigation actions."""
        if self.debug_mode:
            self.logger.debug("Debug mode enabled - logging all actions")

    def on_key(self, event: Key) -> None:
        """Log all key presses for debugging (only if DEBUG_KEYS=true)."""
        if not self.debug_keys:
            return  # Skip all key logging unless DEBUG_KEYS is enabled

        focused_widget = self.focused
        focused_name = focused_widget.__class__.__name__ if focused_widget else "None"
        focused_id = (
            getattr(focused_widget, "id", "no-id") if focused_widget else "no-id"
        )

        self.logger.debug(
            f"Key pressed: '{event.key}' (focused: {focused_name}#{focused_id})"
        )

        # Log if key has a binding
        for binding in self.BINDINGS:
            if binding.key == event.key:
                self.logger.debug(
                    f"Key '{event.key}' has binding: {binding.action} ({binding.description})"
                )
                break
        else:
            self.logger.debug(f"Key '{event.key}' has no binding")

    async def load_initial_data(self) -> None:
        """Load initial pipeline data."""
        self.logger.info(f"Loading initial data for project: {self.project}")
        self.loading = True
        self.error_message = None

        try:
            # Test connection and get project info
            self.logger.debug(f"Fetching project info for: {self.project}")
            project_info = await asyncio.get_event_loop().run_in_executor(
                None, self.gitlab_api.get_project, self.project
            )
            project_name = project_info.get("name", "Unknown Project")
            self.logger.info(
                f"Connected to project: {project_name} (ID: {project_info.get('id')})"
            )
            self.sub_title = f"Pipeline Viewer - {project_name}"

            # Get pipeline data
            self.logger.debug("Fetching pipeline data")
            await self.refresh_pipelines()

        except GitLabAPIError as e:
            self.logger.error(f"GitLab API error during initialization: {e}")
            self.error_message = str(e)
            self.notify(f"Error: {e}", severity="error")
        except Exception as e:
            self.logger.error(f"Unexpected error during initialization: {e}")
            self.error_message = str(e)
            self.notify(f"Unexpected error: {e}", severity="error")
        finally:
            self.loading = False
            self.logger.debug("Initial data loading complete")

    async def refresh_pipelines(self) -> None:
        """Refresh pipeline data from GitLab API."""
        self.logger.debug(
            f"Refreshing pipelines for project {self.project}, branch: {self.branch}"
        )
        try:
            pipelines = await asyncio.get_event_loop().run_in_executor(
                None,
                self.gitlab_api.get_pipelines,
                self.project,
                self.branch,
                10,
            )
            self.logger.info(f"Retrieved {len(pipelines)} pipelines")
            self.pipelines_data = pipelines

            # Log pipeline details
            for i, pipeline in enumerate(pipelines[:3]):  # Log first 3 for brevity
                self.logger.debug(
                    f"Pipeline {i+1}: ID={pipeline.get('id')}, status={pipeline.get('status')}, ref={pipeline.get('ref')}"
                )

            # Update sidebar with new data
            self.logger.debug("Updating sidebar with pipeline data")
            sidebar = self.query_one("#pipeline-sidebar", PipelineSidebar)
            await sidebar.update_pipelines(pipelines)

            # Auto-select first pipeline if none selected
            if pipelines and not self.selected_pipeline_id:
                first_pipeline_id = pipelines[0]["id"]
                self.logger.info(f"Auto-selecting first pipeline: {first_pipeline_id}")
                await self.select_pipeline(first_pipeline_id)
            elif not pipelines:
                self.logger.warning("No pipelines found")

        except GitLabAPIError as e:
            self.logger.error(f"GitLab API error refreshing pipelines: {e}")
            self.error_message = str(e)
            self.notify(f"Error refreshing pipelines: {e}", severity="error")
        except Exception as e:
            self.logger.error(f"Unexpected error refreshing pipelines: {e}")
            self.error_message = str(e)
            self.notify(f"Unexpected error refreshing pipelines: {e}", severity="error")

    async def select_pipeline(self, pipeline_id: int) -> None:
        """Select a pipeline and load its job data."""
        self.logger.info(f"Selecting pipeline: {pipeline_id}")
        self.selected_pipeline_id = pipeline_id

        try:
            # Get pipeline jobs
            self.logger.debug(f"Fetching jobs for pipeline {pipeline_id}")
            jobs = await asyncio.get_event_loop().run_in_executor(
                None, self.gitlab_api.get_pipeline_jobs, self.project, pipeline_id
            )
            self.logger.info(f"Retrieved {len(jobs)} jobs for pipeline {pipeline_id}")
            self.current_pipeline_jobs = jobs

            # Log job details
            job_summary: dict = {}
            for job in jobs:
                stage = job.get("stage", "unknown")
                status = job.get("status", "unknown")
                if stage not in job_summary:
                    job_summary[stage] = {}
                if status not in job_summary[stage]:
                    job_summary[stage][status] = 0
                job_summary[stage][status] += 1

            self.logger.debug(f"Job summary: {job_summary}")

            # Update main view with job data
            self.logger.debug("Updating main view with job data")
            main_view = self.query_one("#pipeline-main", PipelineMainView)
            await main_view.update_pipeline_jobs(jobs)
            self.logger.debug("Main view updated successfully")

        except GitLabAPIError as e:
            self.logger.error(f"GitLab API error loading pipeline jobs: {e}")
            self.error_message = str(e)
            self.notify(f"Error loading pipeline jobs: {e}", severity="error")
        except Exception as e:
            self.logger.error(f"Unexpected error loading pipeline jobs: {e}")
            self.error_message = str(e)
            self.notify(
                f"Unexpected error loading pipeline jobs: {e}", severity="error"
            )

    def action_toggle_dark(self) -> None:
        """Toggle dark/light mode."""
        # TODO: implement light theme
        self.logger.debug(" NOT IMPLEMENTED YET Toggle dark mode action triggered")
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    async def action_refresh(self) -> None:
        """Refresh all data."""
        self.logger.info("Refresh action triggered")
        self.notify("Refreshing data...")
        await self.refresh_pipelines()

    async def action_quit(self) -> None:
        """Quit the application."""
        self.logger.info("Quit action triggered")
        self.exit()

    def action_focus_left(self) -> None:
        """Smart left action: widget navigation or panel focus."""
        if self.debug_keys:
            self.logger.debug("Focus left action triggered")
        focused = self.focused

        # If we're in a widget that handles left/right internally, let it handle it
        if focused and hasattr(focused, "action_cursor_left"):
            if self.debug_keys:
                self.logger.debug(
                    f"Widget {focused.__class__.__name__} can handle cursor_left, delegating"
                )
            focused.action_cursor_left()
            return
        elif focused and hasattr(focused, "cursor_left"):
            if self.debug_keys:
                self.logger.debug(
                    f"Widget {focused.__class__.__name__} can handle cursor_left, delegating"
                )
            focused.cursor_left()
            return

        # Otherwise, do panel navigation (focus sidebar)
        try:
            sidebar = self.query_one("#pipeline-sidebar")
            # Check if we're already in the sidebar
            if focused and (
                focused == sidebar or sidebar in focused.ancestors_with_self
            ):
                if self.debug_keys:
                    self.logger.debug("Already in sidebar, no action needed")
                return
            sidebar.focus()
            if self.debug_keys:
                self.logger.debug("Focused sidebar successfully")
        except Exception as e:
            self.logger.error(f"Failed to focus sidebar: {e}")

    def action_focus_right(self) -> None:
        """Smart right action: widget navigation or panel focus."""
        if self.debug_keys:
            self.logger.debug("Focus right action triggered")
        focused = self.focused

        # If we're in a widget that handles left/right internally, let it handle it
        if focused and hasattr(focused, "action_cursor_right"):
            if self.debug_keys:
                self.logger.debug(
                    f"Widget {focused.__class__.__name__} can handle cursor_right, delegating"
                )
            focused.action_cursor_right()
            return
        elif focused and hasattr(focused, "cursor_right"):
            if self.debug_keys:
                self.logger.debug(
                    f"Widget {focused.__class__.__name__} can handle cursor_right, delegating"
                )
            focused.cursor_right()
            return

        # Otherwise, do panel navigation (focus main view)
        try:
            main_view = self.query_one("#pipeline-main")
            # Check if we're already in the main view
            if focused and (
                focused == main_view or main_view in focused.ancestors_with_self
            ):
                if self.debug_keys:
                    self.logger.debug("Already in main view, no action needed")
                return
            main_view.focus()
            if self.debug_keys:
                self.logger.debug("Focused main view successfully")
        except Exception as e:
            self.logger.error(f"Failed to focus main view: {e}")

    def action_up(self) -> None:
        """Handle up action (mapped from 'k' key)."""
        if self.debug_keys:
            self.logger.info("UP action triggered (from 'k' key)")
        focused = self.focused
        if focused:
            if self.debug_keys:
                self.logger.debug(
                    f"Calling cursor_up on focused widget: {focused.__class__.__name__}"
                )
            # Call the widget's cursor_up method directly
            if hasattr(focused, "action_cursor_up"):
                focused.action_cursor_up()
                if self.debug_keys:
                    self.logger.debug("Successfully called action_cursor_up")
            elif hasattr(focused, "cursor_up"):
                focused.cursor_up()
                if self.debug_keys:
                    self.logger.debug("Successfully called cursor_up")
            else:
                if self.debug_keys:
                    self.logger.warning(
                        f"Widget {focused.__class__.__name__} has no cursor_up method"
                    )
        else:
            if self.debug_keys:
                self.logger.warning("No focused widget to handle up action")

    def action_down(self) -> None:
        """Handle down action (mapped from 'j' key)."""
        if self.debug_keys:
            self.logger.info("DOWN action triggered (from 'j' key)")
        focused = self.focused
        if focused:
            if self.debug_keys:
                self.logger.debug(
                    f"Calling cursor_down on focused widget: {focused.__class__.__name__}"
                )
            # Call the widget's cursor_down method directly
            if hasattr(focused, "action_cursor_down"):
                focused.action_cursor_down()
                if self.debug_keys:
                    self.logger.debug("Successfully called action_cursor_down")
            elif hasattr(focused, "cursor_down"):
                focused.cursor_down()
                if self.debug_keys:
                    self.logger.debug("Successfully called cursor_down")
            else:
                if self.debug_keys:
                    self.logger.warning(
                        f"Widget {focused.__class__.__name__} has no cursor_down method"
                    )
        else:
            if self.debug_keys:
                self.logger.warning("No focused widget to handle down action")

    def action_toggle_debug(self) -> None:
        """Toggle debug panel visibility."""
        self.debug_panel_visible = not self.debug_panel_visible
        debug_log = self.query_one("#debug-log", RichLog)

        if self.debug_panel_visible:
            debug_log.remove_class("hidden")
            self.logger.info("Debug panel shown")
        else:
            debug_log.add_class("hidden")
            self.logger.info("Debug panel hidden")

    def action_show_help(self) -> None:
        """Show help overlay with keyboard shortcuts."""
        help_text = """
GitLab TUI - Keyboard Shortcuts

Navigation:
  h/l     - Focus left/right panel
  j/k     - Move up/down
  gg/G    - Go to top/bottom
  tab     - Next focus

Actions:
  enter   - Select pipeline
  r       - Refresh data
  q       - Quit
  d       - Toggle dark mode
  ctrl+shift+d - Toggle debug panel
  ?       - This help
        """
        self.notify(help_text.strip())

    # Message handlers for custom events
    class PipelineSelected(Message):
        """Message sent when a pipeline is selected in the sidebar."""

        def __init__(self, pipeline_id: int) -> None:
            self.pipeline_id = pipeline_id
            super().__init__()

    async def on_pipeline_selected(self, message: PipelineSelected) -> None:
        """Handle pipeline selection from sidebar."""
        await self.select_pipeline(message.pipeline_id)
