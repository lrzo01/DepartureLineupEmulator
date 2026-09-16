from __future__ import annotations

from typing import Any

from departure_board_emulator.board.base import BoardBase
from departure_board_emulator.board.line import line_util as LU


class Destination(BoardBase):
    def resolve_destinations(self) -> str:
        destinations = self.data["Destinations"]

        destination = destinations[self.current_destination]
        destination_text = destination["Name"]

        available_combos = len(destinations)

        if available_combos > 1:
            if self.current_destination == "Middle":
                self.current_destination = "Rear"
                destination_text += " &"
            elif self.current_destination == "Rear":
                self.current_destination = "Front"
                destination_text = "& " + destination_text
            elif self.current_destination == "Front":
                if available_combos == 2:
                    self.current_destination = "Rear"
                elif available_combos == 3:
                    self.current_destination = "Middle"

                destination_text += " &"
        else:
            via = destination.get("Via")

            if via is not None:
                if self.showing_via:
                    destination_text = "via " + via
                    self.showing_via = False
                else:
                    self.showing_via = True

        return destination_text

    def update_destination_line(self) -> None:
        self.lines[1].clear()

        destination_text = self.resolve_destinations()

        self.lines[1].write_text(
            destination_text,
            [
                self.fonts["tall"],
                self.fonts["wide"],
                self.fonts["std"],
            ],
            LU.TextConstraint.ReduceFontSize,
            LU.VerticalAlignment.Centre,
            LU.HorizontalAlignment.Left,
        )

    def update_time_state_line(self) -> None:
        self.lines[0].clear()

        departure_time = self.data.get("STD", "")

        self.lines[0].write_text(
            departure_time,
            [
                self.fonts["tall"],
                self.fonts["wide"],
                self.fonts["std"],
            ],
            LU.TextConstraint.Free,
            LU.VerticalAlignment.Centre,
            LU.HorizontalAlignment.Left,
        )

        secondary_line = ""

        if self.showing_plat:
            if self.data.get("DepStatus") == "Cancelled":
                self.showing_plat = False
                secondary_line = "Cancelled"
            else:
                boarding_info: Any = self.data.get("BoardingInfo") or {}

                boarding_status = boarding_info.get("BoardingStatus")

                if boarding_status and "Boarding" not in boarding_status:
                    secondary_line = boarding_status
                else:
                    platform = self.data.get("Platform")

                    if platform == "BUS":
                        secondary_line = "BUS"
                    else:
                        secondary_line = (
                            f"Platform {platform}" if platform else "Platform -"
                        )

                self.showing_plat = False

        else:
            dep_status = self.data.get("DepStatus")

            if dep_status == "Exp":
                if self.data.get(
                    "ExpectedDepTimestamp",
                    "",
                ) > self.data.get("DepTimestamp", ""):
                    etd = self.data.get("ETD", "")

                    secondary_line = f"Exp {etd}" if etd else "Delayed"
                else:
                    secondary_line = "On time"

            elif dep_status == "Delayed":
                secondary_line = "Delayed"
            elif dep_status == "Cancelled":
                secondary_line = "Cancelled"
            else:
                secondary_line = "On time"

            self.showing_plat = True

            if dep_status == "Cancelled":
                self.showing_plat = False

        self.lines[0].write_text(
            secondary_line,
            [
                self.fonts["tall"],
                self.fonts["wide"],
                self.fonts["std"],
            ],
            LU.TextConstraint.ReduceFontSize,
            LU.VerticalAlignment.Centre,
            LU.HorizontalAlignment.Right,
        )

    def update_toc_line(self) -> None:
        self.lines[15].clear()

        toc_name = self.data.get(
            "ATOCDesc",
            "Unknown",
        )

        self.lines[15].write_text(
            toc_name,
            [
                self.fonts["long"],
                self.fonts["wide"],
                self.fonts["std"],
            ],
            LU.TextConstraint.ReduceFontSize,
            LU.VerticalAlignment.Centre,
            LU.HorizontalAlignment.Left,
        )

    def destination_cycle(self) -> None:
        if "Destinations" not in self.data:
            return

        for i in range(3, 14):
            self.lines[i].clear()

        self.update_time_state_line()
        self.update_destination_line()
        self.update_toc_line()

        self.refresh_extra_messages()
        self.render_extra_message()

        show_associated = self.has_associated_page() and not self.associated_page_shown

        self.showing_associated_page = show_associated

        if show_associated:
            more_to_come = self.render_associated_page()

            if not more_to_come:
                self.associated_page_shown = True
                self.calling_point_cycles = 0

            self.current_page = 1

        else:
            self.coach_formation()
            self.page_logic()

            self.calling_point_cycles += 1

            min_cycles = self.fetcher.fetch_config_item(
                "associated_page_calling_cycles", int, 3
            )

            if (
                self.current_page == 1
                and self.current_amenity_page == 0
                and self.calling_point_cycles >= min_cycles
            ):
                self.associated_page_shown = False

        if show_associated:
            return

        amenity_pages = self.get_amenity_page_count()
        has_letters = self.has_coach_letters()

        if amenity_pages == 0:
            self.current_amenity_page = 0
        elif not has_letters:
            self.current_amenity_page += 1

            if (
                self.current_amenity_page == 0
                or self.current_amenity_page > amenity_pages
            ):
                self.current_amenity_page = 1
        else:
            self.current_amenity_page += 1

            if self.current_amenity_page > amenity_pages:
                self.current_amenity_page = 0
