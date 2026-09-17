from __future__ import annotations

from typing import Any

import numpy as np

from departure_board_emulator.board.base import BoardBase
from departure_board_emulator.board.line.line import Line
from departure_board_emulator.board.line import line_util as LU


class ExtraMessages(BoardBase):
    scroll_step_px: float
    extra_messages: list[str]
    current_extra_message: int
    scrolling: bool
    scroll_complete: bool
    scroll_offset_float: float
    scroll_offset: int
    scroll_span: int
    _extra_message_timer: int
    _scroll_text: str | None
    _scroll_buffer: np.ndarray | None

    @staticmethod
    def join_message_parts(*parts: Any) -> str:
        cleaned = [str(part).strip() for part in parts if part and str(part).strip()]
        return " ".join(cleaned)

    def is_delayed(self) -> bool:
        status = self.data.get("DepStatus")

        if status == "Delayed":
            return True

        if status == "Exp":
            return self.data.get("ExpectedDepTimestamp", "") > self.data.get(
                "DepTimestamp", ""
            )

        return False

    def get_status_reason(self) -> str:
        if self.data.get("DepStatus") == "Cancelled":
            reason = self.data.get("CancelReason") or self.data.get("DelayReason")
        elif self.is_delayed():
            reason = self.data.get("DelayReason")
        else:
            return ""

        reason = str(reason or "").strip()

        if not reason:
            return ""

        return f"Due to {reason}"

    def build_extra_messages(self) -> list[str]:
        comments: Any = self.data.get("Comments") or {}
        candidates = []

        if comments.get("ExtendedComment"):
            candidates: list[Any] = [
                comments.get("ExtendedComment"),
                self.get_status_reason(),
            ]
        else:
            candidates = [
                self.join_message_parts(
                    comments.get("PlatformLine1"),
                    comments.get("PlatformLine2"),
                ),
                self.join_message_parts(
                    comments.get("DepartureLine1"),
                    comments.get("DepartureLine2"),
                ),
                self.get_status_reason(),
            ]

        messages: list[str] = []

        for message in candidates:
            if message and message not in messages:
                messages.append(message)

        return messages

    def refresh_extra_messages(self) -> None:
        messages = self.build_extra_messages()

        if messages != self.extra_messages:
            self.extra_messages = messages
            self.current_extra_message = 0
            self.reset_scroll()

        if self.current_extra_message >= len(self.extra_messages):
            self.current_extra_message = 0

    def has_extra_messages(self) -> bool:
        return bool(self.extra_messages)

    def scroll_pending(self) -> bool:
        return self.scrolling and not self.scroll_complete

    def reset_scroll(self) -> None:
        self.scrolling = False
        self.scroll_offset_float: float = 0.0
        self.scroll_offset = 0
        self.scroll_span = 0
        self.scroll_complete = False
        self._scroll_text = None
        self._scroll_buffer = None
        self._extra_message_timer = 0

    def _build_scroll_buffer(self, text: str, line: Line) -> None:
        if self._scroll_text == text:
            return

        self._scroll_text = text

        font = self.fonts["std"]
        height = line.grid.shape[0]

        headroom = len(text) * 24 + line.width

        draft = Line(headroom, height)

        draft.write_text(
            text,
            [font],
            LU.TextConstraint.Free,
            LU.VerticalAlignment.Centre,
            LU.HorizontalAlignment.Left,
        )

        lit_columns = np.where(np.any(draft.grid == 1, axis=0))[0]

        text_width = int(lit_columns[-1]) + 1 if lit_columns.size else 0

        if text_width <= line.width:
            self.scrolling = False
            self.scroll_span = 0
            self.scroll_offset_float = 0.0
            self.scroll_offset = 0
            self.scroll_complete = True
            self._scroll_buffer = None
            self._extra_message_timer = 150
            return

        self.scroll_span = text_width + line.width
        self.scroll_offset_float = 0.0
        self.scroll_offset = 0
        self.scroll_complete = False
        self.scrolling = True

        buffer = np.zeros(
            (height, line.width + text_width + line.width),
            dtype=draft.grid.dtype,
        )

        buffer[:, line.width : line.width + text_width] = draft.grid[:, :text_width]

        self._scroll_buffer = buffer

    def render_extra_message(self) -> None:
        line = self.lines[14]
        line.clear()

        if not self.extra_messages:
            self.reset_scroll()
            return

        text = self.extra_messages[self.current_extra_message]

        self._build_scroll_buffer(text, line)

        if not self.scrolling:
            line.write_text(
                text,
                [self.fonts["std"]],
                LU.TextConstraint.Free,
                LU.VerticalAlignment.Centre,
                LU.HorizontalAlignment.Left,
            )
            return

        buffer = self._scroll_buffer
        if buffer is None:
            return

        offset = min(self.scroll_offset, self.scroll_span)
        line.grid[:, :] = buffer[:, offset : offset + line.width]

    def tick_scroll(self, pixels: int | None = None) -> bool:
        if not self.extra_messages:
            return False

        if self.scrolling:
            if not self.scroll_complete:
                step = self.scroll_step_px if pixels is None else float(pixels)

                self.scroll_offset_float += step
                new_offset = int(self.scroll_offset_float)

                if new_offset >= self.scroll_span:
                    self.scroll_offset_float = float(self.scroll_span)
                    self.scroll_offset = self.scroll_span
                    self.scroll_complete = True
                    self._extra_message_timer = 15
                    self.render_extra_message()
                    return True

                if new_offset != self.scroll_offset:
                    self.scroll_offset = new_offset
                    self.render_extra_message()
                    return True

                return False

            self._extra_message_timer -= 1

            if self._extra_message_timer > 0:
                return False

            self._advance_extra_message()

            return True

        self._extra_message_timer -= 1

        if self._extra_message_timer > 0:
            return False

        self._advance_extra_message()

        return True

    def _advance_extra_message(self) -> None:
        if len(self.extra_messages) > 1:
            self.current_extra_message = (self.current_extra_message + 1) % len(
                self.extra_messages
            )

        self.reset_scroll()
        self.render_extra_message()
