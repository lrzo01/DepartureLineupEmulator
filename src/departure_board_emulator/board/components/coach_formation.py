from __future__ import annotations

from typing import Any

from departure_board_emulator.board.base import BoardBase


class CoachFormation(BoardBase):
    def get_coach_amenities(
        self,
        coach: dict[str, Any],
    ) -> list[str]:
        amenities: list[str] = []

        if coach.get("FirstClass"):
            amenities.append("%FIRST_CLASS%")

        if coach.get("BikeStorage"):
            amenities.append("%BIKE%")

        if coach.get("Catering"):
            amenities.append("%CAFE%")

        if coach.get("Wheelchairs"):
            amenities.append("%WHEELCHAIR%")

        return amenities

    def get_amenity_page_count(self) -> int:
        coaches: list[dict[str, Any]] = self.data.get("CoachList", [])

        if not coaches:
            return 0

        return max(
            (len(self.get_coach_amenities(coach)) for coach in coaches),
            default=0,
        )

    def formation_is_reversed(
        self,
        coaches: list[dict[str, Any]],
    ) -> bool:
        labels = [
            str(coach.get("CoachLetter", "")).strip().upper() for coach in coaches
        ]

        labels = [label for label in labels if label]

        if len(labels) < 2:
            return False

        def label_value(label: str) -> int | None:
            if label.isdigit():
                return int(label)

            if len(label) == 1 and label.isalpha():
                return ord(label)

            return None

        values = [label_value(label) for label in labels]

        valid_values: list[int] = [v for v in values if v is not None]

        if len(valid_values) != len(values):
            return False

        return all(
            valid_values[i] > valid_values[i + 1] for i in range(len(valid_values) - 1)
        )

    def parse_reservation_level_into_str(
        self,
        reservation_level: int | None,
    ) -> str:
        if not reservation_level or reservation_level <= 10:
            return "_EMPTY"
        elif reservation_level <= 25:
            return "_FULL1"
        elif reservation_level <= 45:
            return "_FULL2"
        elif reservation_level <= 65:
            return "_FULL3"
        elif reservation_level <= 85:
            return "_FULL4"
        else:
            return "_FULL5"

    def has_coach_letters(self) -> bool:
        return any(coach.get("CoachLetter") for coach in self.data.get("CoachList", []))

    def coach_formation(self) -> None:
        self.lines[12].clear()
        self.lines[13].clear()

        coaches: list[dict[str, Any]] = list(self.data.get("CoachList", []))

        if not coaches:
            return

        if (
            self.current_amenity_page == 0
            and not self.has_coach_letters()
            and self.get_amenity_page_count() > 0
        ):
            self.current_amenity_page = 1

        reversed_formation = self.formation_is_reversed(coaches)

        if reversed_formation:
            coaches.reverse()

        font = self.fonts["wide"]

        x = 0

        for i, coach in enumerate(coaches):
            reservation_level = coach.get("ReservationLevel")

            reservation_string = self.parse_reservation_level_into_str(
                reservation_level
            )

            is_first = i == 0
            is_last = i == len(coaches) - 1

            if reversed_formation and is_last:
                coach_identifier = "%REV" + reservation_string + "_DRIVING%"
            elif not reversed_formation and is_first:
                coach_identifier = "%REV_OP" + reservation_string + "_DRIVING%"
            else:
                coach_identifier = "%REV" + reservation_string + "%"

            coach_glyph = font.find_glyph_from_letter(coach_identifier)

            if not coach_glyph:
                continue

            self.lines[12].write_glyph(
                coach_identifier,
                font,
                x,
            )

            if self.current_amenity_page == 0:
                label = coach.get(
                    "CoachLetter",
                    "",
                )

                if label:
                    self.lines[13].write_glyph_in_box(
                        label,
                        font,
                        box_x=x,
                        box_width=coach_glyph.width,
                        invert=bool(coach.get("FirstClass")),
                    )

            else:
                amenities = self.get_coach_amenities(coach)

                amenity_index = self.current_amenity_page - 1

                if amenity_index < len(amenities):
                    amenity = amenities[amenity_index]

                    self.lines[13].write_glyph_in_box(
                        amenity,
                        font,
                        box_x=x,
                        box_width=coach_glyph.width,
                        invert=False,
                    )

            x += coach_glyph.width + font.default_spacing
