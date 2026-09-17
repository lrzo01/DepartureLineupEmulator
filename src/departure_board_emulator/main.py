import sys
from PySide6.QtWidgets import QApplication

from departure_board_emulator.board import Board
from departure_board_emulator.fetch import DataSource, Fetcher
from departure_board_emulator.window import MainWindow


def main() -> None:
    fetcher = Fetcher()

    default_startup_location = fetcher.fetch_config_item(
        "startup_location", str, "EUSTON"
    )
    refresh_secs = fetcher.fetch_config_item("refresh_secs", int, 30)
    data_source = DataSource(default_startup_location, fetcher, refresh_secs)

    app = QApplication(sys.argv)
    board = Board(fetcher)
    window = MainWindow(fetcher, data_source, default_startup_location, board)

    window.show()
    sys.exit(app.exec())
