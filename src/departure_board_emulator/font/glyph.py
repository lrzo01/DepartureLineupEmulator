from .font import Font


class Glyph:
    def __init__(self, name: str, width: int, font: Font):
        self.name = name
        self._width = width
        self.font = font
        self.grid = [[0] * width for _ in range(font.height)]
        font.glyphs.append(self)

    @property
    def blank(self) -> bool:
        if self.grid == [[0] * self.width for _ in range(self.font.height)]:
            return True
        return False

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_width: int):
        if new_width == self._width or new_width < 1:
            return

        for y in range(len(self.grid)):
            if new_width > self._width:
                self.grid[y].extend([0] * (new_width - self._width))
            else:
                self.grid[y] = self.grid[y][:new_width]

        self._width = new_width

    def clear(self) -> None:
        self.grid = [[0] * self.width for _ in range(self.font.height)]

    def write(self, x: int, y: int, state: int) -> None:
        if not (0 <= x < self.width):
            raise ValueError(f"X out of bounds: {x}")
        if not (0 <= y < self.font.height):
            raise ValueError(f"Y out of bounds: {y}")

        self.grid[y][x] = state

    def read(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width):
            raise ValueError(f"X out of bounds: {x}")
        if not (0 <= y < self.font.height):
            raise ValueError(f"Y out of bounds: {y}")

        return bool(self.grid[y][x])

    def invert(self) -> None:
        self.grid = [[1 - pixel for pixel in row] for row in self.grid]

    def shift_up(self) -> None:
        self.grid.pop(0)
        self.grid.append([0] * self.width)

    def shift_down(self) -> None:
        self.grid.insert(0, [0] * self.width)
        self.grid.pop()

    def shift_left(self) -> None:
        for index, _ in enumerate(self.grid):
            self.grid[index].pop(0)
            self.grid[index].append(0)

    def shift_right(self) -> None:
        for index, _ in enumerate(self.grid):
            self.grid[index].insert(0, 0)
            self.grid[index].pop()
