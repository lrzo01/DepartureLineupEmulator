from __future__ import annotations

import numpy as np

from departure_board_emulator.board.line import line_util as LU
from departure_board_emulator.font import Font


class Line:
    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height

        self.grid: np.ndarray = np.zeros((height, width), dtype=np.uint8)

    def set_pixel(self, x: int, y: int, state: int) -> None:
        self.grid[y, x] = state

    def get_pixel(self, x: int, y: int) -> int:
        return int(self.grid[y, x])

    def clear(self) -> None:
        self.grid = np.zeros((self.height, self.width), dtype=np.uint8)

    # used for coach letters etc
    def write_glyph_in_box(
        self,
        identifier: str,
        font: Font,
        box_x: int,
        box_width: int,
        invert: bool = False,
    ) -> None:
        glyph = font.find_glyph_from_letter(identifier)

        if not glyph:
            return

        min_x = glyph.width
        max_x = -1
        min_y = font.height
        max_y = -1

        for x in range(glyph.width):
            for y in range(font.height):
                if glyph.read(x, y):
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)

        if max_x == -1 or max_y == -1:
            return

        visible_width = max_x - min_x + 1
        visible_height = max_y - min_y + 1

        start_x = box_x + (box_width - visible_width) // 2 - min_x

        start_y = (self.height - visible_height) // 2 - min_y

        if invert:
            for x in range(box_x, box_x + box_width):
                if 0 <= x < self.width:
                    for y in range(self.height):
                        self.set_pixel(x, y, 1)

        for x in range(glyph.width):
            out_x = start_x + x

            if not 0 <= out_x < self.width:
                continue

            for y in range(font.height):
                out_y = start_y + y

                if not 0 <= out_y < self.height:
                    continue

                if glyph.read(x, y):
                    if invert:
                        self.set_pixel(out_x, out_y, 0)
                    else:
                        self.set_pixel(out_x, out_y, 1)

    def write_glyph(
        self,
        identifier: str,
        font: Font,
        x: int,
        vertical_alignment: LU.VerticalAlignment = LU.VerticalAlignment.Centre,
    ) -> None:
        glyph = font.find_glyph_from_letter(identifier)

        if not glyph:
            return

        if vertical_alignment == LU.VerticalAlignment.Up:
            start_y = 0
        elif vertical_alignment == LU.VerticalAlignment.Down:
            start_y = self.height - font.height
        else:
            start_y = (self.height - font.height) // 2

        for col in range(glyph.width):
            out_x = x + col

            if not (0 <= out_x < self.width):
                continue

            for row in range(font.height):
                out_y = start_y + row

                if 0 <= out_y < self.height and glyph.read(col, row):
                    self.set_pixel(out_x, out_y, 1)

    def write_text(
        self,
        raw_text: str,
        fonts: list[Font],
        constraint: LU.TextConstraint,
        vertical_alignment: LU.VerticalAlignment,
        horizontal_alignment: LU.HorizontalAlignment,
    ) -> None:
        text = LU.parse_string_to_identifiers(raw_text)
        chosen_font = LU.determine_best_font(fonts, text, self.width, constraint)

        width = LU.find_text_width(chosen_font, text)
        height = chosen_font.height

        if horizontal_alignment == LU.HorizontalAlignment.Left:
            start_x = 0
        elif horizontal_alignment == LU.HorizontalAlignment.Right:
            start_x = self.width - width
        else:
            start_x = (self.width - width) // 2

        if vertical_alignment == LU.VerticalAlignment.Up:
            start_y = 0
        elif vertical_alignment == LU.VerticalAlignment.Down:
            start_y = self.height - height
        else:
            start_y = (self.height - height) // 2

        current_x = start_x

        for i, letter in enumerate(text):
            glyph = chosen_font.find_glyph_from_letter(letter)
            if not glyph:
                continue

            for col in range(glyph.width):
                out_x = current_x + col

                if not (0 <= out_x < self.width):
                    continue

                if constraint in (
                    LU.TextConstraint.Truncate,
                    LU.TextConstraint.ReduceFontSize,
                ):
                    if np.any(self.grid[:, out_x] == 1):
                        return
                elif constraint == LU.TextConstraint.Free:
                    self.grid[:, out_x] = 0

                for row in range(chosen_font.height):
                    if glyph.read(col, row):
                        out_y = start_y + row
                        if 0 <= out_y < self.height:
                            self.set_pixel(out_x, out_y, 1)

            current_x += glyph.width

            if i < len(text) - 1:
                for space_col in range(chosen_font.default_spacing):
                    out_x = current_x + space_col

                    if not (0 <= out_x < self.width):
                        continue

                    if constraint in (
                        LU.TextConstraint.Truncate,
                        LU.TextConstraint.ReduceFontSize,
                    ):
                        if np.any(self.grid[:, out_x] == 1):
                            return
                    elif constraint == LU.TextConstraint.Free:
                        self.grid[:, out_x] = 0

                current_x += chosen_font.default_spacing
