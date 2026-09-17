from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QResizeEvent, QShowEvent
from PySide6.QtWidgets import (
    QCompleter,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QMainWindow,
)

from departure_board_emulator.board.board import Board
from departure_board_emulator.board.render import render_dot_grid
from departure_board_emulator.fetch import DataSource, Fetcher
from departure_board_emulator.font import Font
from departure_board_emulator.ui import Ui_MainWindow


class BoardColumn:
    def __init__(self, scene: QGraphicsScene, board: Board) -> None:
        self.board: Board = board

        self.structural_item: QGraphicsPixmapItem = QGraphicsPixmapItem()
        scene.addItem(self.structural_item)

        self.message_item: QGraphicsPixmapItem = QGraphicsPixmapItem(
            self.structural_item
        )

        y, _height, _width = board.get_row_pixel_bounds(14)

        dot_size = board.fetcher.fetch_config_item("dot_size", int, 4)
        dot_spacing = board.fetcher.fetch_config_item("dot_spacing", int, 1)
        border_size = board.fetcher.fetch_config_item("border_size", int, 12)
        border_padding = board.fetcher.fetch_config_item("border_padding", int, 8)
        stride = dot_size + dot_spacing
        margin = border_size + border_padding

        self.message_item.setPos(margin, margin + y * stride)

    def redraw_structure(self) -> None:
        border_size = self.board.fetcher.fetch_config_item("border_size", int, 12)
        border_padding = self.board.fetcher.fetch_config_item("border_padding", int, 8)
        self.structural_item.setPixmap(
            render_dot_grid(
                self.board.get_static_grid(),
                fetcher=self.board.fetcher,
                border_size=border_size,
                border_padding=border_padding,
            )
        )

    def redraw_message(self) -> None:
        self.message_item.setPixmap(
            render_dot_grid(
                self.board.get_extra_message_grid(), fetcher=self.board.fetcher
            )
        )

    def remove(self, scene: QGraphicsScene) -> None:
        scene.removeItem(self.structural_item)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(
        self,
        fetcher: Fetcher,
        data_source: DataSource,
        default_startup_location: str,
        board: Board,
    ) -> None:
        super().__init__()

        self.setupUi(self)

        self.fetcher: Fetcher = fetcher
        self.data_source: DataSource = data_source

        self.shared_fonts: dict[str, Font] = dict(board.fonts)

        self.last_valid_location: str = default_startup_location
        self.valid_stations: list[str] = self.fetcher.produce_autocompletion_list()

        self.completer: QCompleter = QCompleter(
            self.valid_stations,
            self,
        )

        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        self.crsClusterLineEdit.setCompleter(self.completer)
        self.crsClusterLineEdit.setText(default_startup_location)
        self.crsClusterLineEdit.editingFinished.connect(self.update_station_view)

        self.completer.activated.connect(self.select_station)

        self.scene: QGraphicsScene = QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.graphicsView.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.columns: list[BoardColumn] = [BoardColumn(self.scene, board)]

        self.cached_services: list[dict[str, Any]] = []

        if hasattr(self, "displayClusterSpinner"):
            self.displayClusterSpinner.valueChanged.connect(
                lambda: self._apply_board_count(preserve_existing=True)
            )

        destination_cycle_ms = fetcher.fetch_config_item(
            "destination_cycle_ms", int, 5000
        )
        target_fps = fetcher.fetch_config_item("target_fps", int, 60)
        timer_interval = max(1, 1000 // target_fps)

        self.destination_timer: QTimer = QTimer(self)
        self.destination_timer.timeout.connect(self.cycle_destinations)
        self.destination_timer.start(destination_cycle_ms)

        self.scroll_timer: QTimer = QTimer(self)
        self.scroll_timer.timeout.connect(self.tick_scrolls)
        self.scroll_timer.start(timer_interval)

        self.update_station_view()

    def select_station(self, station: str) -> None:
        self.crsClusterLineEdit.setText(station)
        self.update_station_view()

    def display_count(self) -> int:
        if hasattr(self, "displayClusterSpinner"):
            return max(1, self.displayClusterSpinner.value())

        return 1

    def cycle_destinations(self) -> None:
        changed = False

        for column in self.columns:
            if not column.board.data:
                continue

            column.board.destination_cycle()
            column.redraw_structure()
            column.redraw_message()

            changed = True

        if changed:
            self._layout_columns()

    def tick_scrolls(self) -> None:
        for column in self.columns:
            if not column.board.data:
                continue

            if column.board.tick_scroll():
                column.redraw_message()

    def set_board_count(
        self,
        count: int,
        services: list[dict[str, Any]],
        preserve_existing: bool = False,
    ) -> None:
        while len(self.columns) < count:
            new_board = Board(self.fetcher, fonts=self.shared_fonts)
            col = BoardColumn(self.scene, new_board)
            col.board.render_blank_board()
            col.redraw_structure()
            col.redraw_message()
            self.columns.append(col)

        while len(self.columns) > count:
            column = self.columns.pop()
            column.remove(self.scene)

        for i, column in enumerate(self.columns):
            if i < len(services):
                service = services[i]
                current_uid = (column.board.data or {}).get("UID")
                new_uid = service.get("UID")

                if preserve_existing and column.board.data and current_uid == new_uid:
                    continue

                column.board.data = service
                column.board.reset_destination_cycle()
                column.board.destination_cycle()
                column.redraw_structure()
                column.redraw_message()
            else:
                is_blanked = getattr(column.board, "_is_blanked", False)
                if preserve_existing and is_blanked:
                    continue

                column.board.data = {}
                column.board._is_blanked = True
                column.board.reset_destination_cycle()
                column.board.render_blank_board()
                column.redraw_structure()
                column.redraw_message()

        self._layout_columns()
        self._fit_view()

    def _apply_board_count(self, preserve_existing: bool) -> None:
        count = self.display_count()

        self.set_board_count(
            count,
            self.cached_services[:count],
            preserve_existing=preserve_existing,
        )

    def _layout_columns(self) -> None:
        if not self.columns:
            return

        spacing_x = 16.0
        spacing_y = 16.0

        viewport = self.graphicsView.viewport().size()
        view_width = max(1, viewport.width())
        view_height = max(1, viewport.height())

        board_width = max(
            item.structural_item.pixmap().width() for item in self.columns
        )

        board_height = max(
            item.structural_item.pixmap().height() for item in self.columns
        )

        if board_width <= 0 or board_height <= 0:
            return

        count = len(self.columns)

        best_columns = 1
        best_scale = 0.0

        for columns in range(1, count + 1):
            rows = (count + columns - 1) // columns

            layout_width = columns * board_width + (columns - 1) * spacing_x

            layout_height = rows * board_height + (rows - 1) * spacing_y

            scale = min(
                view_width / layout_width,
                view_height / layout_height,
            )

            if scale > best_scale:
                best_scale = scale
                best_columns = columns

        columns = best_columns
        rows = (count + columns - 1) // columns

        total_width = columns * board_width + (columns - 1) * spacing_x

        for index, item in enumerate(self.columns):
            row = index // columns
            column = index % columns

            row_start = row * columns
            row_count = min(columns, count - row_start)

            row_width = row_count * board_width + (row_count - 1) * spacing_x

            row_offset = (total_width - row_width) / 2

            x = row_offset + column * (board_width + spacing_x)
            y = row * (board_height + spacing_y)

            item.structural_item.setPos(x, y)

        bounds = self.scene.itemsBoundingRect()

        if not bounds.isEmpty():
            self.scene.setSceneRect(bounds)

    def _fit_view(self) -> None:
        rect = self.scene.sceneRect()
        if not rect.isEmpty():
            viewport_size = self.graphicsView.viewport().size()
            if viewport_size.width() > 0 and viewport_size.height() > 0:
                scale_x = viewport_size.width() / rect.width()
                scale_y = viewport_size.height() / rect.height()
                scale = min(scale_x, scale_y)

                if self.columns:
                    board_w = self.columns[0].structural_item.pixmap().width()
                    board_h = self.columns[0].structural_item.pixmap().height()
                    if board_w > 0 and board_h > 0:
                        ref_cols = 3
                        ref_rows = 2
                        ref_w = ref_cols * board_w + (ref_cols - 1) * 16.0
                        ref_h = ref_rows * board_h + (ref_rows - 1) * 16.0
                        min_scale = min(
                            viewport_size.width() / ref_w,
                            viewport_size.height() / ref_h,
                        )
                        scale = max(scale, min_scale)

                self.graphicsView.resetTransform()
                self.graphicsView.scale(scale, scale)
                self.graphicsView.centerOn(rect.center())

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        self._layout_columns()
        self._fit_view()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)

        self._fit_view()

    def update_station_view(self) -> None:
        station_text = self.crsClusterLineEdit.text().strip()

        matched_station = next(
            (
                station
                for station in self.valid_stations
                if station.lower() == station_text.lower()
            ),
            None,
        )

        if matched_station is None:
            self.crsClusterLineEdit.setText(self.last_valid_location)
            return

        self.last_valid_location = matched_station

        self.crsClusterLineEdit.setText(matched_station)

        self.setWindowTitle(f"Departures for {matched_station}")

        self.data_source.update(matched_station)

        self.cached_services = [
            service
            for service in self.data_source.data.get("services", [])
            if service.get("STD") and service.get("CallingPoints")
        ]

        self._apply_board_count(preserve_existing=False)
