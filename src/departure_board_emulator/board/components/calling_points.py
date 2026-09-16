from __future__ import annotations

import math
from typing import Any

import numpy as np

from departure_board_emulator.board.base import BoardBase
from departure_board_emulator.board.line import line_util as LU


class CallingPoints(BoardBase):
    def line_is_free(self, index: int) -> bool:
        return not np.any(self.lines[index].grid == 1)

    def get_available_calling_rows(self) -> list[int]:
        available: list[int] = []

        for index in range(3, 15):
            if np.any(self.lines[index].grid == 1):
                break

            available.append(index)

        return available

    def get_calling_sections(self) -> list[str]:
        calling_points = self.data.get("CallingPoints", {})

        return [
            section
            for section in ("Front", "Middle", "Rear")
            if calling_points.get(section)
        ]

    def train_divides(self) -> bool:
        return len(self.get_calling_sections()) > 1

    def get_section_calling_points(
        self,
        section: str,
    ) -> list[dict[str, Any]]:
        calling_points = self.data.get("CallingPoints", {})
        destinations = self.data.get("Destinations", {})

        points = list(calling_points.get(section, []))

        destination = destinations.get(section)

        if destination:
            destination_tiploc = destination.get("TIPLOC")

            already_present = any(
                point.get("TIPLOC") == destination_tiploc for point in points
            )

            if not already_present:
                points.append(destination)

        return points

    def format_calling_point(
        self,
        point: dict[str, Any],
    ) -> str:
        name = point.get("Name", "")

        time = point.get("STA") or point.get("STD") or ""

        if time:
            return f"{name} ({time})"

        return name

    def get_portion_heading(self, section: str) -> str:
        destinations = self.data.get("Destinations", {})
        destination = destinations.get(section, {})

        coaches = destination.get("Coaches")

        if coaches is None:
            return f"{section} coaches"

        coach_word = "coach" if coaches == 1 else "coaches"

        return f"{section} {coaches} {coach_word}"

    def build_calling_pages(
        self,
    ) -> list[tuple[str | None, list[dict[str, Any]]]]:
        available_rows = self.get_available_calling_rows()

        if not available_rows:
            return []

        row_capacity = len(available_rows)

        sections = self.get_calling_sections()

        if not sections:
            return []

        dividing = self.train_divides()

        pages: list[tuple[str | None, list[dict[str, Any]]]] = []

        for section in sections:
            points = self.get_section_calling_points(section)

            if not points:
                continue

            if dividing:
                point_capacity = row_capacity - 1
                heading = self.get_portion_heading(section)
            else:
                point_capacity = row_capacity
                heading = None

            if point_capacity <= 0:
                continue

            number_of_pages = math.ceil(len(points) / point_capacity)

            for page_index in range(number_of_pages):
                start = page_index * point_capacity
                end = start + point_capacity

                page_points = points[start:end]

                pages.append(
                    (
                        heading,
                        page_points,
                    )
                )

        return pages

    def page_logic(self) -> None:
        self.lines[2].clear()

        for index in range(3, 12):
            self.lines[index].clear()

        pages = self.build_calling_pages()

        if not pages:
            self.current_page = 1
            self.total_pages = 1
            return

        self.total_pages = len(pages)

        if self.current_page > self.total_pages:
            self.current_page = 1

        heading, calling_points = pages[self.current_page - 1]

        self.lines[2].write_text(
            "Calling at:",
            [self.fonts["std"]],
            LU.TextConstraint.Free,
            LU.VerticalAlignment.Centre,
            LU.HorizontalAlignment.Left,
        )

        self.lines[2].write_text(
            f"Page {self.current_page} of {self.total_pages}",
            [self.fonts["std"]],
            LU.TextConstraint.Free,
            LU.VerticalAlignment.Centre,
            LU.HorizontalAlignment.Right,
        )

        available_rows = self.get_available_calling_rows()

        if not available_rows:
            return

        row_position = 0

        if heading is not None:
            line_index = available_rows[row_position]

            self.lines[line_index].write_text(
                heading,
                [self.fonts["std"]],
                LU.TextConstraint.Free,
                LU.VerticalAlignment.Centre,
                LU.HorizontalAlignment.Centre,
            )

            row_position += 1

        for point in calling_points:
            if row_position >= len(available_rows):
                break

            line_index = available_rows[row_position]

            text = self.format_calling_point(point)

            self.lines[line_index].write_text(
                text,
                [self.fonts["std"]],
                LU.TextConstraint.Truncate,
                LU.VerticalAlignment.Centre,
                LU.HorizontalAlignment.Left,
            )

            row_position += 1

        self.current_page += 1

        if self.current_page > self.total_pages:
            self.current_page = 1
