"""Pipeline sidebar component for displaying pipeline history."""

from datetime import datetime
from logging import Logger
from typing import Any, Dict

from textual.containers import Horizontal, Vertical
from textual.widgets import Label, ListItem

from gitlab_tui.config.manager import AppConfig
from gitlab_tui.ui.components.base_widget import BaseComponent


class PipelineListItem(BaseComponent, ListItem):
    """A custom list item for displaying pipeline information."""

    def __init__(
        self, logger: Logger, config: AppConfig, pipeline_data: Dict[str, Any], **kwargs
    ) -> None:
        BaseComponent.__init__(self, logger, config, **kwargs)
        self.pipeline_data = pipeline_data
        self.can_focus = True

    def compose(self):
        """Compose the pipeline list item."""
        pipeline = self.pipeline_data

        # Extract pipeline info
        status = pipeline.get("status", "unknown")
        ref = pipeline.get("ref", "unknown")
        created_at = pipeline.get("created_at", "")

        # Format created time
        try:
            created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            time_str = created_time.strftime(self.config.display.timestamp_format)
        except (ValueError, AttributeError):
            time_str = "Unknown"

        # Get author info
        user = pipeline.get("user", {})
        author = user.get("name", user.get("username", "Unknown"))

        status_icon, status_colour = self._get_status_icon_and_colour(status)
        status_text = self._format_text(
            text=f"{status_icon} {ref}", colour=status_colour
        )

        with Vertical():
            # Single line with status and ref
            with Horizontal():
                yield Label(status_text, classes="pipeline-id")
            # Single line with author and time
            with Horizontal():
                yield Label(
                    f"{author[:12]}.." if len(author) > 12 else author,
                    classes="pipeline-author",
                )
                yield Label(time_str, classes="pipeline-time")
