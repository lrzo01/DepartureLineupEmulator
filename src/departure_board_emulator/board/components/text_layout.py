from __future__ import annotations

from departure_board_emulator.board.base import BoardBase
from departure_board_emulator.font import Font


class TextLayout(BoardBase):
    def measure_text(self, text: str, font: Font) -> int:
        width = 0
        drawn = 0

        for character in text:
            glyph = font.find_glyph_from_letter(character)

            if glyph is None:
                if character == " ":
                    width += 3 + font.default_spacing
                    drawn += 1

                continue

            width += glyph.width + font.default_spacing
            drawn += 1

        if drawn == 0:
            return 0

        return width - font.default_spacing

    def wrap_text(
        self,
        text: str,
        font: Font,
        max_width: int,
    ) -> list[str]:
        lines: list[str] = []
        current = ""

        for word in text.split():
            candidate = f"{current} {word}" if current else word

            if current and self.measure_text(candidate, font) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate

        if current:
            lines.append(current)

        return lines
