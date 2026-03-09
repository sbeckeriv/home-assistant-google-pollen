"""The Google Pollen integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LANGUAGE, CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DEFAULT_LANGUAGE
from .utils import fetch_pollen_data

_LOGGER = logging.getLogger(__name__)

DOMAIN = "google_pollen"
PLATFORMS = [Platform.SENSOR]

SERVICE_GET_POLLEN_FORECAST = "get_pollen_forecast"
CONF_DAYS = "days"

SERVICE_GET_POLLEN_FORECAST_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LATITUDE): cv.latitude,
        vol.Required(CONF_LONGITUDE): cv.longitude,
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): cv.string,
        vol.Optional(CONF_DAYS, default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=5)),
    }
)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Google Pollen component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Google Pollen from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    # Register service only once
    if not hass.services.has_service(DOMAIN, SERVICE_GET_POLLEN_FORECAST):
        async def handle_get_pollen_forecast(call: ServiceCall) -> dict[str, Any]:
            """Handle the service call to get pollen forecast."""
            latitude = call.data[CONF_LATITUDE]
            longitude = call.data[CONF_LONGITUDE]
            language = call.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
            days = call.data.get(CONF_DAYS, 1)
            
            # Get API key from the first config entry
            api_key = None
            for entry_id in hass.data[DOMAIN]:
                if isinstance(hass.data[DOMAIN][entry_id], dict):
                    api_key = hass.data[DOMAIN][entry_id].get(CONF_API_KEY)
                    if api_key:
                        break
            
            if not api_key:
                _LOGGER.error("No API key found in configuration")
                return {"error": "No API key configured"}
            
            try:
                data = await fetch_pollen_data(
                    api_key=api_key,
                    latitude=latitude,
                    longitude=longitude,
                    language=language,
                    days=days,
                )
                
                _LOGGER.info(
                    "Pollen forecast retrieved for location (%s, %s)",
                    latitude,
                    longitude,
                )
                
                return data
                
            except Exception as err:
                _LOGGER.error("Error fetching pollen data: %s", err)
                return {"error": str(err)}
        
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_POLLEN_FORECAST,
            handle_get_pollen_forecast,
            schema=SERVICE_GET_POLLEN_FORECAST_SCHEMA,
        )
    
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
