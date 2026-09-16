from __future__ import annotations

from departure_board_emulator.board.components.associated_page import (
    AssociatedPage,
)
from departure_board_emulator.board.components.calling_points import (
    CallingPoints,
)
from departure_board_emulator.board.components.coach_formation import (
    CoachFormation,
)
from departure_board_emulator.board.components.destination import Destination
from departure_board_emulator.board.components.extra_messages import (
    ExtraMessages,
)
from departure_board_emulator.board.components.grid import GridCompositing
from departure_board_emulator.board.components.text_layout import TextLayout


class Board(
    CoachFormation,
    ExtraMessages,
    AssociatedPage,
    CallingPoints,
    Destination,
    TextLayout,
    GridCompositing,
):
    def reset_destination_cycle(self) -> None:
        self.current_destination = "Front"
        self.showing_via = False
        self.showing_plat = False
        self.current_page = 1
        self.showing_calling_at = True
        self.current_amenity_page = 0

        self.showing_associated_page = False
        self.associated_page_shown = False
        self.associated_page_index = 0
        self.calling_point_cycles = 0

        self.extra_messages = []
        self.current_extra_message = 0
        self.reset_scroll()
