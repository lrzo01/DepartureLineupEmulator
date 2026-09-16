import os
import sys
from pathlib import Path
from typing import Any, TypeVar

from dotenv import load_dotenv
import requests
import toml

from departure_board_emulator.font import Font, json_to_font
import departure_board_emulator.types as Types

T = TypeVar("T")


def _resource_base() -> Path:
    """Return the base directory for bundled resources.

    When frozen by PyInstaller, data files are extracted to sys._MEIPASS.
    When running from source, walk up from this file to the project root
    (the directory that contains pyproject.toml / config.toml).
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    # src/departure_board_emulator/fetch/fetch.py → project root is 3 levels up
    return Path(__file__).resolve().parents[3]


class Fetcher:
    def __init__(self) -> None:
        base = _resource_base()
        load_dotenv(dotenv_path=base / ".env")
        self.config: dict[str, Any] = toml.load(base / "config.toml")
        self.locations: list[Types.Station] = self._fetch_locations()

    def get_tiploc_from_crs_or_name(self, identifier: str) -> str | None:
        for location in self.locations:
            if location["CRS"] == identifier or location["Name"] == identifier:
                return location["TIPLOC"]
        return None

    def _fetch_locations(self) -> list[Types.Station]:
        url = self.fetch_config_item(
            "locations_url", str, "https://tiger-api-portal.worldline.global/locations"
        )

        headers: dict[str, str] = {
            "x-api-key": os.getenv("WORLDLINE_TIGER_API_KEY", "")
        }

        request = requests.get(url, headers=headers)
        response = request.json()
        locations: list[Types.Station] = []

        # strictly typing the json schema of the worldline format would be great
        # i am not this patient and there is no documentation
        # woopsies for my bad practices

        if response and isinstance(response, list):
            for location in response: # type: ignore
                locations.append(location) # type: ignore

        return locations

    def fetch_font(self, font_name: str) -> Font:
        font_path = self.fetch_config_item("font_path", str, "fonts")
        full_font_path = _resource_base() / font_path / font_name
        opened_font: Font | None = None

        try:
            with open(full_font_path, "r", encoding="utf-8") as file:
                opened_font = json_to_font(file.read())
        except Exception as e:
            print(f"could not open font {font_name}: {e}")

        if opened_font:
            return opened_font
        else:
            raise Exception(f"could not open font {font_name}")

    def fetch_config_item(
        self, item_name: str, expected_type: type[T], default_value: T
    ) -> T:
        item = self.config.get(item_name)

        if item is None:
            if default_value is not None:
                return default_value
            else:
                raise KeyError(f"missing config item: {item_name}")
        elif not isinstance(item, expected_type):
            if expected_type is float and isinstance(item, int):
                return float(item)  # type: ignore
            raise TypeError(
                f"expected {expected_type.__name__}, got {type(item).__name__}"
            )

        return item

    def produce_autocompletion_list(self) -> list[str]:
        if not self.locations:
            raise ValueError("no locations?")

        items: list[str] = []

        for location in self.locations:
            items.append(location["CRS"])
            items.append(location["Name"])

        return items
