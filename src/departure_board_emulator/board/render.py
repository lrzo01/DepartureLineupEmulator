from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtGui import QImage, QPixmap

if TYPE_CHECKING:
    from departure_board_emulator.fetch import Fetcher

_tile_cache: dict[tuple[int, int, str, str, str], np.ndarray] = {}

# unironically alot of this is black magic
# wouldnt touch, but it makes sure it renders in an optimised way
# there is some weird bug with scrolling sometimes but the jittering is pretty minimal

def _rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")

    return (
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16),
    )


def _coverage(dot_size: int, stride: int) -> np.ndarray:
    samples = stride * 8

    axis = (np.arange(samples) + 0.5) / 8

    yy, xx = np.meshgrid(axis, axis, indexing="ij")

    if dot_size <= 2:
        inside = ((xx >= 0) & (xx <= dot_size) & (yy >= 0) & (yy <= dot_size)).astype(np.float32)
    else:
        centre = dot_size / 2.0
        radius = dot_size / 2.0
        inside = ((xx - centre) ** 2 + (yy - centre) ** 2 <= radius**2).astype(np.float32)

    return inside.reshape(
        stride,
        8,
        stride,
        8,
    ).mean(axis=(1, 3))


def _tiles(
    dot_size: int,
    dot_spacing: int,
    on_color: str,
    off_color: str,
    bg_color: str,
) -> np.ndarray:
    key = (dot_size, dot_spacing, on_color, off_color, bg_color)

    cached = _tile_cache.get(key)

    if cached is not None:
        return cached

    stride = dot_size + dot_spacing

    coverage = _coverage(dot_size, stride)
    background = _rgb(bg_color)

    def tile(color: str | None) -> np.ndarray:
        result = np.empty((stride, stride, 4), dtype=np.uint8)

        foreground = background if color is None else _rgb(color)

        for out_index, channel in enumerate((2, 1, 0)):
            blended = (
                background[channel]
                + (foreground[channel] - background[channel]) * coverage
            )

            result[..., out_index] = np.rint(blended).astype(np.uint8)

        result[..., 3] = 255

        return result

    tiles = np.stack(
        [
            tile(off_color),
            tile(on_color),
            tile(None),
        ]
    )

    _tile_cache[key] = tiles

    return tiles


def grid_pixel_size(
    grid: np.ndarray,
    dot_size: int = 4,
    dot_spacing: int = 1,
) -> tuple[int, int]:
    stride = dot_size + dot_spacing
    rows, cols = grid.shape

    width = cols * stride - dot_spacing
    height = rows * stride - dot_spacing

    return width, height


def render_dot_grid(
    grid: np.ndarray,
    fetcher: Fetcher | None = None,
    dot_size: int | None = None,
    dot_spacing: int | None = None,
    on_color: str | None = None,
    off_color: str | None = None,
    bg_color: str | None = None,
    border_size: int = 0,
    border_padding: int = 0,
    border_color: str = "#000000",
) -> QPixmap:
    actual_dot_size = (
        dot_size
        if dot_size is not None
        else (fetcher.fetch_config_item("dot_size", int, 4) if fetcher else 4)
    )

    actual_dot_spacing = (
        dot_spacing
        if dot_spacing is not None
        else (fetcher.fetch_config_item("dot_spacing", int, 1) if fetcher else 1)
    )

    actual_on_color = (
        on_color
        if on_color is not None
        else (
            fetcher.fetch_config_item("on_color", str, "#ffaa00")
            if fetcher
            else "#ffaa00"
        )
    )

    actual_off_color = (
        off_color
        if off_color is not None
        else (
            fetcher.fetch_config_item("off_color", str, "#1e1805")
            if fetcher
            else "#1e1805"
        )
    )

    actual_bg_color = (
        bg_color
        if bg_color is not None
        else (
            fetcher.fetch_config_item("bg_color", str, "#08080a")
            if fetcher
            else "#08080a"
        )
    )

    tiles = _tiles(
        actual_dot_size,
        actual_dot_spacing,
        actual_on_color,
        actual_off_color,
        actual_bg_color,
    )

    stride = actual_dot_size + actual_dot_spacing
    rows, cols = grid.shape

    width, height = grid_pixel_size(grid, actual_dot_size, actual_dot_spacing)

    grid_buffer = np.empty((rows * stride, cols * stride, 4), dtype=np.uint8)

    view = grid_buffer.reshape(
        rows,
        stride,
        cols,
        stride,
        4,
    ).transpose(0, 2, 1, 3, 4)

    if grid.dtype != np.uint8:
        grid = grid.astype(np.uint8, copy=False)

    np.take(tiles, grid, axis=0, out=view)

    if border_size > 0 or border_padding > 0:
        total_margin = border_size + border_padding
        out_w = width + total_margin * 2
        out_h = height + total_margin * 2

        full_buffer = np.empty((out_h, out_w, 4), dtype=np.uint8)
        border_rgb = _rgb(border_color)

        full_buffer[..., :3] = border_rgb
        full_buffer[..., 3] = 255

        if border_padding > 0:
            bg_rgb = _rgb(actual_bg_color)
            full_buffer[border_size : out_h - border_size, border_size : out_w - border_size, :3] = bg_rgb

        full_buffer[total_margin : total_margin + height, total_margin : total_margin + width] = grid_buffer[:height, :width]

        image = QImage(
            full_buffer.data,
            out_w,
            out_h,
            out_w * 4,
            QImage.Format.Format_RGB32,
        )
    else:
        cropped_buffer = grid_buffer[:height, :width]
        image = QImage(
            cropped_buffer.copy().data,
            width,
            height,
            width * 4,
            QImage.Format.Format_RGB32,
        )

    return QPixmap.fromImage(image)


def clear_render_caches() -> None:
    _tile_cache.clear()
