"""Coordinator for Google Pollen data updates."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .utils import fetch_pollen_data

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=4)


class GooglePollenDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for fetching and updating Google Pollen data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
        latitude: float,
        longitude: float,
        language: str,
    ) -> None:
        """Initialize the coordinator."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.language = language

        super().__init__(
            hass,
            _LOGGER,
            name="Pollen",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            data = await fetch_pollen_data(
                api_key=self.api_key,
                latitude=self.latitude,
                longitude=self.longitude,
                language=self.language,
                days=4,
            )

            _LOGGER.debug("Pollen data: %s", data)

            if "error" in data:
                error_message = data["error"]["message"]
                raise UpdateFailed(f"Error communicating with API: {error_message}")

            daily_info = data.get("dailyInfo", [])
            result = {}

            for day_index, day_info in enumerate(daily_info):
                pollen_type_info = day_info.get("pollenTypeInfo", [])
                plant_info = day_info.get("plantInfo", [])
                all_info = pollen_type_info + plant_info

                for pollen_info in all_info:
                    pollen_code = pollen_info.get("code")
                    if pollen_code not in result:
                        result[pollen_code] = {}
                    result[pollen_code][day_index] = {
                        "category": str(
                            pollen_info.get("indexInfo", {}).get("category", "No Data")
                        ),
                        "display_name": str(pollen_info.get("displayName", "")),
                        "in_season": str(pollen_info.get("inSeason", "False")),
                        "last_updated": datetime.now().isoformat(),
                        "description": str(
                            pollen_info.get("indexInfo", {}).get("indexDescription", "")
                        ),
                        "index_value": float(
                            pollen_info.get("indexInfo", {}).get("value", 0)
                        ),
                    }

            for pollen_code, pollen_data in result.items():
                result[pollen_code][0]["tomorrow"] = float(
                    pollen_data.get(1, {}).get("index_value", 0)
                )
                result[pollen_code][0]["day 3"] = float(
                    pollen_data.get(2, {}).get("index_value", 0)
                )
                result[pollen_code][0]["day 4"] = float(
                    pollen_data.get(3, {}).get("index_value", 0)
                )

            _LOGGER.debug("Result data: %s", result)

            return result

        except (ConnectionError, TimeoutError) as error:
            raise UpdateFailed(f"Network error updating Google Pollen data: {error}") from error
        except ValueError as error:
            raise UpdateFailed(f"Data error updating Google Pollen data: {error}") from error
        except Exception as error:
            raise UpdateFailed(f"Unexpected error updating Google Pollen data: {error}") from error
