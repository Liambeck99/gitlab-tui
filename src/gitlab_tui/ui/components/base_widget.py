"""Base Widget component for common dependecies and methods"""

from logging import Logger

from rich.style import Style
from rich.text import Text

from gitlab_tui.config.manager import AppConfig


class BaseComponent:
    """Base widget for common dependencies and methods"""

    DEFAULT_COLOUR: str = "#cdd6f4"

    def __init__(
        self,
        logger: Logger,
        config: AppConfig,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.logger = logger
        self.config = config
        self.DEFAULT_COLOUR = self.config.theme.variables["text_secondary"]

    def _get_status_icon_and_colour(self, status: str) -> tuple[str, str]:
        status_colours = {
            "success": self.config.theme.success,
            "failed": self.config.theme.error,
            "running": self.config.theme.secondary,
            "pending": self.config.theme.secondary,
            "canceled": self.config.theme.variables["text_secondary"],
            "created": self.config.theme.accent,
            "manual": self.config.theme.primary,
            "skipped": self.config.theme.variables["text_secondary"],
        }

        status_icon = self.config.icons.get(status)
        status_colour = status_colours.get(status, self.DEFAULT_COLOUR)

        return status_icon, status_colour

    def _format_text(self, text: str, colour: str) -> Text:
        formatted_text = Text(text)
        formatted_text.stylize(Style(color=colour))
        return formatted_text
