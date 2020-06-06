"""Custom PlayStation 4 componenet with configuration.yaml integration."""

import voluptuous

from homeassistant.components import ps4
from homeassistant.helpers import config_validation

from . import const
from . import config_flow

PLATFORM_SCHEMA = config_validation.PLATFORM_SCHEMA.extend({
    voluptuous.Required(const.CONF_HOST): config_validation.string,
    voluptuous.Optional(const.CONF_NAME): config_validation.string,
    voluptuous.Required(const.CONF_REGION): config_validation.string,
    voluptuous.Required(const.CONF_TOKEN): config_validation.string,
})


async def async_setup(hass, config):
  await ps4.async_setup(hass, config)
  return True


async def async_setup_entry(hass, config_entry):
  await ps4.async_setup_entry(hass, config_entry)


async def async_unload_entry(hass, entry):
  await ps4.async_unload_entry(hass, entry)
