"""Coordinator class for Ariston module."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import timedelta
import logging
import time

import aiohttp
from ariston.base_device import AristonBaseDevice
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Timeout for API requests (in seconds)
API_REQUEST_TIMEOUT = 60


class DeviceDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages polling for state changes from the device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: AristonBaseDevice,
        scan_interval_seconds: int,
        coordinator_name: str,
        async_update_state: Callable,
    ) -> None:
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{device.name}-{coordinator_name}",
            update_interval=timedelta(seconds=scan_interval_seconds),
            # Don't pass update_method to parent - we override _async_update_data
        )

        self.device = device
        self._async_update_state = async_update_state
        self._coordinator_name = coordinator_name
        self._consecutive_errors = 0

    async def _async_update_data(self):
        """Fetch data from Ariston API with timeout and proper error handling.
        
        This method wraps the API call with a timeout to prevent hung requests
        from blocking the coordinator indefinitely. The ariston library (v0.19.9)
        has no HTTP timeout configured for async requests.
        """
        start_time = time.monotonic()
        
        _LOGGER.debug(
            "[%s] Starting data update for device %s",
            self._coordinator_name,
            self.device.name,
        )
        
        try:
            # Wrap the API call with a timeout to prevent hung requests
            await asyncio.wait_for(
                self._async_update_state(),
                timeout=API_REQUEST_TIMEOUT,
            )
            
            elapsed = time.monotonic() - start_time
            
            # Reset error counter on success
            if self._consecutive_errors > 0:
                _LOGGER.info(
                    "[%s] Data update recovered after %d consecutive errors "
                    "(took %.2fs)",
                    self._coordinator_name,
                    self._consecutive_errors,
                    elapsed,
                )
                self._consecutive_errors = 0
            else:
                _LOGGER.debug(
                    "[%s] Data update successful (took %.2fs)",
                    self._coordinator_name,
                    elapsed,
                )
            
            return self.device.data
            
        except asyncio.TimeoutError:
            elapsed = time.monotonic() - start_time
            self._consecutive_errors += 1
            
            _LOGGER.error(
                "[%s] API request TIMED OUT after %.2fs (timeout=%ds). "
                "This indicates the Ariston cloud API is unresponsive. "
                "Consecutive errors: %d",
                self._coordinator_name,
                elapsed,
                API_REQUEST_TIMEOUT,
                self._consecutive_errors,
            )
            
            raise UpdateFailed(
                f"Ariston API request timed out after {API_REQUEST_TIMEOUT} seconds. "
                f"The cloud API may be unresponsive."
            )
            
        except aiohttp.ClientError as err:
            elapsed = time.monotonic() - start_time
            self._consecutive_errors += 1
            
            _LOGGER.error(
                "[%s] HTTP connection error after %.2fs: %s. "
                "Consecutive errors: %d",
                self._coordinator_name,
                elapsed,
                err,
                self._consecutive_errors,
            )
            
            raise UpdateFailed(f"Connection error to Ariston API: {err}")
            
        except Exception as err:
            elapsed = time.monotonic() - start_time
            self._consecutive_errors += 1
            
            _LOGGER.error(
                "[%s] Unexpected error after %.2fs: %s (%s). "
                "Consecutive errors: %d",
                self._coordinator_name,
                elapsed,
                err,
                type(err).__name__,
                self._consecutive_errors,
            )
            
            raise UpdateFailed(f"Error communicating with Ariston API: {err}")
