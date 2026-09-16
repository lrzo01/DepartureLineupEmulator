from __future__ import annotations

import numpy as np

from departure_board_emulator.board.base import BoardBase


class GridCompositing(BoardBase):
    def get_row_pixel_bounds(self, index: int) -> tuple[int, int, int]:
        y = 0

        for i, line in enumerate(self.lines):
            height = line.grid.shape[0]

            if i == index:
                return y, height, line.width

            y += height

            if i == len(self.lines) - 1:
                break

            padding_height = 6 if i in (0, 1) else 4

            y += padding_height

        raise IndexError(index)

    def get_extra_message_grid(self) -> np.ndarray:
        return self.lines[14].grid

    def get_static_grid(self) -> np.ndarray:
        row = self.lines[14]
        saved = row.grid.copy()

        row.clear()

        try:
            return self.get_full_grid()
        finally:
            row.grid = saved

    def get_full_grid(self) -> np.ndarray:
        target_width = 160

        matrices: list[np.ndarray] = []

        for i, line in enumerate(self.lines):
            grid_to_append = line.grid

            if line.width < target_width:
                pad_amount = target_width - line.width

                grid_to_append = np.pad(
                    line.grid,
                    ((0, 0), (0, pad_amount)),
                    mode="constant",
                    constant_values=2,
                )

            matrices.append(grid_to_append)

            if i == len(self.lines) - 1:
                break

            padding_height = 6 if i in (0, 1) else 4

            spacer = np.full(
                (padding_height, target_width),
                2,
                dtype=np.uint8,
            )

            matrices.append(spacer)

        return np.vstack(matrices)
