from __future__ import annotations

from departure_board_emulator.board.base import BoardBase
from departure_board_emulator.board.line import line_util as LU


class AssociatedPage(BoardBase):
    def has_associated_page(self) -> bool:
        return bool(str(self.data.get("AssociatedPage", "") or "").strip())

    def build_associated_page_chunks(
        self,
        rows: list[int],
    ) -> list[list[str]]:
        text = str(self.data.get("AssociatedPage", "") or "").strip()

        if not text or not rows:
            return []

        font = self.fonts["std"]

        raw_width = min(self.lines[row].width for row in rows)

        width = max(
            1,
            raw_width - 12,
        )

        wrapped: list[str] = self.wrap_text(text, font, width)

        if not wrapped:
            return []

        capacity = len(rows)

        return [
            wrapped[start : start + capacity]
            for start in range(0, len(wrapped), capacity)
        ]

    def render_associated_page(self) -> bool:
        self.lines[2].clear()

        rows: list[int] = self.get_available_calling_rows()

        chunks = self.build_associated_page_chunks(rows)

        if not chunks:
            self.associated_page_index = 0
            return False

        if self.associated_page_index >= len(chunks):
            self.associated_page_index = 0

        chunk = chunks[self.associated_page_index]

        for offset, text in enumerate(chunk):
            if offset >= len(rows):
                break

            self.lines[rows[offset]].write_text(
                text,
                [self.fonts["std"]],
                LU.TextConstraint.Truncate,
                LU.VerticalAlignment.Centre,
                LU.HorizontalAlignment.Centre,
            )

        self.associated_page_index += 1

        more_to_come = self.associated_page_index < len(chunks)

        if not more_to_come:
            self.associated_page_index = 0

        return more_to_come
