"""Creates a wrapper with support for configuration.yaml for PS4 component."""

import collections
import logging

from homeassistant import util
from homeassistant.components.ps4 import media_player as ps4_media_player

from . import const

_LOGGER = logging.getLogger(__name__)

Config = collections.namedtuple(
    'Config', f'{const.CONF_ENTRY_ID} {const.CONF_DATA}')


async def async_setup_platform(
        hass, config, async_add_entities, discovery_info=None):
  """Loads configuration and delegates to official integration."""
  # Load configuration.yaml
  host = config.get(const.CONF_HOST)
  name = config.get(const.CONF_NAME, const.DEFAULT_NAME)
  region = config.get(const.CONF_REGION)
  token = config.get(const.CONF_TOKEN)

  # Format it in the new config_entry.yaml format
  config_entry = Config(
      util.slugify(name),
      {
          const.CONF_TOKEN: token,
          const.CONF_DEVICES: [
              {
                  const.CONF_HOST: host,
                  const.CONF_NAME: name,
                  const.CONF_REGION: region,
              },
          ],
      }
  )

  await ps4_media_player.async_setup_entry(
      hass, config_entry, async_add_entities)

  return True


async def async_setup_entry(hass, config_entry, async_add_entities):
  await ps4_media_player.async_setup_entry(
      hass, config_entry, async_add_entities)
