"""Utility functions for Google Pollen integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)


async def fetch_pollen_data(
    api_key: str,
    latitude: float,
    longitude: float,
    language: str,
    days: int = 1,
) -> dict[str, Any]:
    """Fetch pollen data from the API."""
    try:
        params = {
            "key": api_key,
            "location.latitude": latitude,
            "location.longitude": longitude,
            "languageCode": language,
            "days": days,
            "plantsDescription": "false",
        }
        async with aiohttp.ClientSession() as session, session.get(
            BASE_URL, params=params
        ) as response:
            response.raise_for_status()
            data = await response.json()

        _LOGGER.debug("API-result: %s", data)
        return data

    except aiohttp.ClientResponseError as error:
        _LOGGER.error("Error fetching pollen data: %s", error)
        raise

    except Exception as error:
        _LOGGER.error("Unexpected error: %s", error)
        raise
