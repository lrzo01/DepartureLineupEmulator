from __future__ import annotations

from typing import Any

import numpy as np

from departure_board_emulator.board.line.line import Line
from departure_board_emulator.fetch import Fetcher
from departure_board_emulator.font import Font


class BoardBase:
    def __init__(
        self,
        fetcher: Fetcher,
        fonts: dict[str, Font] | None = None,
    ) -> None:
        self.fetcher: Fetcher = fetcher

        target_fps = fetcher.fetch_config_item("target_fps", int, 30)
        hold_secs = fetcher.fetch_config_item("extra_message_hold_secs", float, 5.0)
        pause_secs = fetcher.fetch_config_item("scroll_end_pause_secs", float, 0.5)

        self.extra_message_hold_ticks = int(hold_secs * target_fps)
        self.scroll_end_pause_ticks = int(pause_secs * target_fps)
        self.scroll_step_px: float = fetcher.fetch_config_item(
            "scroll_speed_px", float, 0.75
        )
        self.associated_page_h_padding = fetcher.fetch_config_item(
            "associated_page_h_padding", int, 6
        )

        self.current_amenity_page: int = 0
        self.lines: list[Line] = []
        self.data: dict[str, Any] = {}

        self.current_destination: str = "Front"
        self.showing_via: bool = False
        self.showing_plat: bool = False
        self.is_showing_platform: bool = False
        self.platform_flash_state: bool = True
        self.current_secondary_text: str = ""
        self.showing_calling_at: bool = True

        self.current_page: int = 1
        self.total_pages: int = 1

        self.showing_associated_page: bool = False
        self.associated_page_shown: bool = False
        self.associated_page_index: int = 0

        self.extra_messages: list[str] = []
        self.current_extra_message: int = 0

        self.scrolling: bool = False
        self.scroll_offset: int = 0
        self.scroll_span: int = 0
        self.scroll_complete: bool = False

        self._scroll_text: str | None = None
        self._scroll_buffer: np.ndarray | None = None

        self._extra_message_timer: int = 0

        self.fonts: dict[str, Font] = fonts or {
            "long": fetcher.fetch_font("Long.json"),
            "tall": fetcher.fetch_font("Tall.json"),
            "wide": fetcher.fetch_font("Wide.json"),
            "std": fetcher.fetch_font("Standard.json"),
        }

        for _ in range(2):
            self.lines.append(Line(160, 13))

        for _ in range(14):
            self.lines.append(Line(150, 9))

    # the below is all unnecessary, just for typing
    # -----------

    def wrap_text(self, text: str, font: Font, max_width: int) -> list[str]:
        return []

    def get_available_calling_rows(self) -> list[int]:
        return []

    def get_full_grid(self) -> np.ndarray:
        return np.zeros((0, 0), dtype=np.uint8)

    def render_associated_page(self) -> bool:
        return False

    def has_associated_page(self) -> bool:
        return False

    def refresh_extra_messages(self) -> None:
        pass

    def render_extra_message(self) -> None:
        pass

    def coach_formation(self) -> None:
        pass

    def page_logic(self) -> None:
        pass

    def get_amenity_page_count(self) -> int:
        return 0

    def has_coach_letters(self) -> bool:
        return False

    def reset_scroll(self) -> None:
        pass

    def tick_scroll(self, pixels: int | None = None) -> bool:
        return False

    def tick_flash(self) -> bool:
        return False

    def scroll_pending(self) -> bool:
        return False
