"""Pipeline sidebar component for displaying pipeline history."""

from logging import Logger
from typing import Any, Dict, List, Optional

from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListView, Static

from gitlab_tui.config.manager import AppConfig
from gitlab_tui.ui.components.base_widget import BaseComponent
from gitlab_tui.ui.components.pipeline_list_item import PipelineListItem


class PipelineSidebar(BaseComponent, Widget):
    """Sidebar widget for displaying pipeline history."""

    pipelines: reactive[List[Dict[str, Any]]] = reactive([])
    selected_pipeline_id: reactive[Optional[int]] = reactive(None)

    def __init__(self, logger: Logger, config: AppConfig, **kwargs) -> None:
        BaseComponent.__init__(self, logger, config, **kwargs)
        Widget.__init__(self, **kwargs)

    def compose(self):
        """Compose the sidebar widget."""
        with Vertical():
            yield Label("Pipeline History", classes="title")
            yield Static("Loading pipelines...", id="loading", classes="loading")
            yield ListView(id="pipeline-list")
            yield Static("No pipelines found", id="empty-message", classes="hidden")

    async def update_pipelines(self, pipelines: List[Dict[str, Any]]) -> None:
        """Update the pipeline list with new data."""
        self.logger.info(f"Updating sidebar with {len(pipelines)} pipelines")
        self.pipelines = pipelines

        # Hide loading message
        self.logger.debug("Hiding loading message")
        loading = self.query_one("#loading", Static)
        loading.add_class("hidden")

        # Get the ListView and update it
        self.logger.debug("Clearing pipeline list view")
        list_view = self.query_one("#pipeline-list", ListView)
        list_view.clear()

        if not pipelines:
            # Show empty message
            self.logger.warning("No pipelines to display, showing empty message")
            empty_msg = self.query_one("#empty-message", Static)
            empty_msg.remove_class("hidden")
            return

        # Hide empty message and add pipeline items
        self.logger.debug("Hiding empty message and adding pipeline items")
        empty_msg = self.query_one("#empty-message", Static)
        empty_msg.add_class("hidden")

        for i, pipeline in enumerate(pipelines):
            self.logger.debug(
                f"Adding pipeline item {i+1}: ID={pipeline.get('id')}, status={pipeline.get('status')}"
            )
            item = PipelineListItem(self.logger, self.config, pipeline)
            await list_view.append(item)

        self.logger.debug(
            f"Successfully added {len(pipelines)} pipeline items to sidebar"
        )

    def on_list_view_selected(self, message: ListView.Selected) -> None:
        """Handle pipeline selection from the list."""
        self.logger.debug(f"List view selection event triggered: {message}")
        if message.item and hasattr(message.item, "pipeline_data"):
            pipeline_id = message.item.pipeline_data.get("id")
            pipeline_status = message.item.pipeline_data.get("status")
            self.logger.info(
                f"Pipeline selected: ID={pipeline_id}, status={pipeline_status}"
            )
            if pipeline_id:
                self.selected_pipeline_id = pipeline_id
                # Post a message to the parent app
                self.logger.debug(
                    f"Posting PipelineSelected message for pipeline {pipeline_id}"
                )
                self.post_message(PipelineSelected(pipeline_id))
        else:
            self.logger.warning("Invalid list view selection - no pipeline data found")


class PipelineSelected(Message):
    """Message sent when a pipeline is selected."""

    def __init__(self, pipeline_id: int) -> None:
        self.pipeline_id = pipeline_id
        super().__init__()
