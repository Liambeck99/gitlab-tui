from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppConfig:
    """App configuration"""

    theme: str = "dark"
    auto_refresh: int = 300  # seconds
    timestamp_format: str = "%m/%d/%y %H:%M"


@dataclass
class IconsConfig:
    """Icons configuration"""

    default_icon: str = "?"
    success: str = "\uf058"  # Circle with tick ()
    failed: str = "\uf530"  # Circle with cross ()
    running: str = "\uf042"  # Circle part full ()
    pending: str = "\uebb5"  # Circle not filled ()
    canceled: str = "\ueabd"  # Circle with line through ()
    created: str = "\uf1ce"  # Circle with notch ()
    manual: str = "\uf013"  # Cog ()
    skipped: str = "\uf192"  # Circle with dot ()

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get icon by key with optional default."""
        if not default:
            default = self.default_icon
        return getattr(self, key, default)


@dataclass
class ThemeConfig:
    """Default theme configuration"""

    name: str = "catppuccin-mocha"
    primary: str = "#cba6f7"  # Mauve - primary accent color
    secondary: str = "#89b4fa"  # Blue - secondary accent
    accent: str = "#f5c2e7"  # Pink - tertiary accent
    foreground: str = "#cdd6f4"  # Text - main text color
    background: str = "#1e1e2e"  # Base - main background
    success: str = "#a6e3a1"  # Green - success states
    warning: str = "#f9e2af"  # Yellow - warnings
    error: str = "#f38ba8"  # Red - errors and dangers
    surface: str = "#313244"  # Surface0 - elevated surfaces
    panel: str = "#45475a"  # Surface2 - panels and sidebars
    dark: bool = True
    variables: dict[str, str] = field(
        default_factory=lambda: {
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#cba6f7",  # Mauve for footer keys
            "input-selection-background": "#89b4fa 35%",  # Blue with transparency
            # Additional Catppuccin-specific variables
            "border-color": "#6c7086",  # Overlay1 for borders
            "scrollbar-color": "#585b70",  # Overlay0 for scrollbars
            "scrollbar-hover-color": "#6c7086",  # Overlay1 for scrollbar hover
            "tab-active-foreground": "#cba6f7",  # Mauve for active tabs
            "tab-inactive-foreground": "#9399b2",  # Subtext0 for inactive tabs
            "button-hover-background": "#585b70",  # Overlay0 for button hover
            "text_primary": "#cdd6f4",  # Text - your existing foreground (best contrast)
            "text_secondary": "#bac2de",  # Subtext1 - slightly dimmed
            "text_tertiary": "#a6adc8",  # Subtext0 - more subtle
            "text_muted": "#9399b2",  # Overlay2 - disabled states
            "text_subtle": "#7f849c",  # Overlay1 - very subtle text
            "text_faint": "#6c7086",  # Overlay0 - placeholders, hints
        }
    )
