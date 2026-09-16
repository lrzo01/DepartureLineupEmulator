import os
import threading
import time
from typing import Any

import requests

import departure_board_emulator.fetch as FC


class DataSource:
    def __init__(
        self,
        tiploc: str = "EUSTON",
        fetcher: FC.Fetcher | None = None,
        refresh_secs: int = 30,
    ) -> None:
        self.tiploc: str | None = tiploc
        self.fetcher: FC.Fetcher | None = fetcher

        if not self.fetcher:
            raise ValueError("no fetcher")

        self.data: dict[str, Any] = {}
        self.refresh_secs: int = refresh_secs

        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def update(self, identifier: str) -> None:
        if not self.fetcher:
            raise ValueError("no fetcher")

        self.tiploc = self.fetcher.get_tiploc_from_crs_or_name(identifier)
        print(self.tiploc)
        self.reload_data()

    def _loop(self) -> None:
        while True:
            try:
                self.reload_data()
            except Exception as e:
                print(f"failure retrieving station data: {e}")

            time.sleep(self.refresh_secs)

    def reload_data(self) -> None:
        if not self.fetcher:
            raise ValueError("no fetcher")

        url = self.fetcher.fetch_config_item(
            "stations_url", str, "https://tiger-api-portal.worldline.global/services"
        )

        tiploc = self.tiploc
        if tiploc is not None:
            url = url + "/" + tiploc

            headers: dict[str, str] = {
                "x-api-key": os.getenv("WORLDLINE_TIGER_API_KEY", "")
            }

            request = requests.get(url, headers=headers, timeout=10)
            res = request.json()
            if isinstance(res, dict):
                self.data = res
