"""Pipeline main view component for displaying pipeline jobs and stages."""

from itertools import groupby
from logging import Logger
from operator import itemgetter
from typing import Any, Dict, List

from rich.text import Text
from textual.containers import Center, Grid, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Label, Static

from gitlab_tui.config.manager import AppConfig
from gitlab_tui.ui.components.base_widget import BaseComponent


class PipelineMainView(BaseComponent, Widget):
    """Main view for displaying pipeline details and jobs."""

    jobs: reactive[List[Dict[str, Any]]] = reactive([])

    def __init__(
        self,
        logger: Logger,
        config: AppConfig,
        **kwargs,
    ):
        super().__init__(logger, config, **kwargs)

    def compose(self):
        """Compose the main view widget."""
        with Vertical():
            # Compact pipeline info section
            with Vertical(id="info-section", classes="info-section"):
                yield Label("Pipeline Details", classes="title")
                with Grid(id="info-grid", classes="info-grid"):
                    # Empty initially, will be filled when jobs are loaded
                    pass

            # Job table takes up remaining space
            with Vertical(id="jobs-section", classes="jobs-section"):
                yield Label("Pipeline Stages and Jobs", classes="title")
                yield DataTable(id="job-table", zebra_stripes=True, classes="job-table")

            with Center():
                yield Static(
                    "Select a pipeline to view details",
                    id="placeholder",
                    classes="placeholder",
                )

    async def update_pipeline_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        """Update the view with job data."""
        self.jobs = jobs

        if not jobs:
            self._show_placeholder(True)
            return

        self._show_placeholder(False)

        # Update info grid
        await self._update_info_grid(jobs)

        # Update job table
        await self._update_job_table(jobs)

    async def _update_info_grid(self, jobs: List[Dict[str, Any]]) -> None:
        """Update the pipeline info grid."""
        info_grid = self.query_one("#info-grid", Grid)
        info_grid.remove_children()

        # Get the first job to extract pipeline info
        if not jobs:
            return

        job = jobs[0]
        pipeline = job.get("pipeline", {})

        # Calculate stats
        total_jobs = len(jobs)

        pipeline_id = pipeline.get("id", "Unknown")
        pipeline_status = pipeline.get("status", "Unknown").title()

        # Add info rows
        await info_grid.mount(Label("ID:", classes="info-label"))
        await info_grid.mount(Label(f"#{pipeline_id}", classes="info-value"))

        await info_grid.mount(Label("Status:", classes="info-label"))
        await info_grid.mount(Label(pipeline_status, classes="info-value"))

        await info_grid.mount(Label("Jobs:", classes="info-label"))
        await info_grid.mount(
            Label(
                f"{total_jobs} total jobs",
                classes="info-value",
            )
        )

    async def _update_job_table(self, jobs: List[Dict[str, Any]]) -> None:
        """Update the job table with stage columns and job rows."""
        table = self.query_one("#job-table", DataTable)
        table.clear(columns=True)

        # Group jobs by stage
        jobs_by_stage = self._group_jobs_by_stage(jobs)
        if not jobs_by_stage:
            return

        # Add columns for each stage
        stages = list(jobs_by_stage.keys())
        table.add_columns(*stages)

        # Find the max number of jobs in any stage
        max_jobs = max(len(jobs_by_stage[stage]) for stage in stages)

        # Prepare row data
        rows: List[List[Text]] = []
        for i in range(max_jobs):
            row: List[Text] = []
            for stage in stages:
                stage_jobs = jobs_by_stage[stage]
                if i < len(stage_jobs):
                    job = stage_jobs[i]
                    job_info = self._format_job_cell(job)
                    row.append(job_info)
            rows.append(row)

        # Add rows
        if rows:
            table.add_rows(rows)

    def _group_jobs_by_stage(
        self, jobs: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group jobs by stage and sort by stage and job name."""
        # First sort by stage_idx to preserve stage order
        sorted_jobs = sorted(
            jobs, key=lambda j: (j.get("stage_idx", 999), j.get("stage", ""))
        )

        # Group by stage
        result = {}
        for stage, jobs_in_stage in groupby(sorted_jobs, key=itemgetter("stage")):
            result[stage] = list(jobs_in_stage)

        return result

    def _format_job_cell(self, job: Dict[str, Any]) -> Text:
        """Format a job cell with name and status."""
        job_name = job.get("name", "Unknown")
        job_status = job.get("status", "unknown")

        status_icon, status_colour = self._get_status_icon_and_colour(job_status)

        formatted_text = self._format_text(
            text=f"{status_icon} {job_name}", colour=status_colour
        )

        return formatted_text

    def _show_placeholder(self, show: bool) -> None:
        """Show or hide the placeholder message."""
        placeholder = self.query_one("#placeholder", Static)
        if show:
            placeholder.add_class("placeholder")
            placeholder.remove_class("hidden")
        else:
            placeholder.add_class("hidden")
            placeholder.remove_class("placeholder")
