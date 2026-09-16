from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from departure_board_emulator.font.glyph import Glyph


class Font:
    def __init__(
        self,
        name: str,
        height: int,
        default_spacing: int = 1,
        default_width: int = 8,
        markers: list[int] | None = None,
    ) -> None:
        self.name: str = name
        self._height: int = height
        self.default_spacing: int = default_spacing
        self.default_width: int = default_width
        self.glyphs: list[Glyph] = []
        self.markers: list[int] = markers or []

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_height: int) -> None:
        if new_height == self._height or new_height < 1:
            return

        for glyph in self.glyphs:
            if new_height > self._height:
                for _ in range(new_height - self._height):
                    glyph.grid.append([0] * glyph.width)
            else:
                glyph.grid = glyph.grid[:new_height]

        self._height = new_height

    def find_glyph_from_letter(self, letter: str) -> Glyph | None:
        for glyph in self.glyphs:
            if glyph.name == letter:
                return glyph
        return None
