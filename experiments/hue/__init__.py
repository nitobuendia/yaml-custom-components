"""Hue platform."""

from homeassistant.components import hue


async def async_setup(hass, config):
  return await hue.async_setup(hass, config)


async def async_setup_entry(hass, entry):
  return await hue.async_setup_entry(hass, entry)


async def async_unload_entry(hass, entry):
  return await hue.async_unload_entry(hass, entry)
