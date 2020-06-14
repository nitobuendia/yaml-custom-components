"""Config flow to configure Philips Hue.

This is a modified version of:
https://raw.githubusercontent.com/home-assistant/core/dev/homeassistant/components/hue/config_flow.py

The objective of this sample code is to showcase how to change existing logic to
support YAML from the UI config flow.
"""

import logging
import voluptuous
import yaml

from homeassistant import config_entries
from homeassistant.components.hue import const as hue_const
from homeassistant.components.hue import config_flow

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(hue_const.DOMAIN)
class CustomHueFlowHandler(config_flow.HueFlowHandler):
  """Custom Hue config flow.

  This wrapper on top of original provides YAML configuration at the end
  of the process.
  """

  def __init__(self):
    """Sets up the UI configuration handler."""
    self._set_up_data = None

  # Original async_step_link, but adding one extra step to confirm device.
  async def async_step_link(self, user_input=None):
    """Attempt to link with the Hue bridge.
    Given a configured host, will ask the user to press the link button
    to connect to the bridge.
    """
    _LOGGER.info('Custom Hue step link.')

    if user_input is None:
      return self.async_show_form(step_id="link")

    bridge = self.bridge
    assert bridge is not None
    errors = {}

    try:
      await config_flow.authenticate_bridge(self.hass, bridge)

      # Can happen if we come from import.
      if self.unique_id is None:
        await self.async_set_unique_id(
            config_flow.normalize_bridge_id(bridge.id), raise_on_progress=False
        )

      # Change async_create_entry to async_show_form with device confirmation.
      title = bridge.config.name
      host = bridge.host
      username = bridge.username
      allow_hue_groups = False

      self._set_up_data = {
          'title': title,
          'data': {
              'host': host,
              'username': username,
              'allow_hue_groups': allow_hue_groups,
          }
      }

      yaml_data = {
          'hue': {
              'bridges': [{
                  'host': host,
                  'allow_hue_groups': allow_hue_groups,
              }]
          }
      }
      yaml_configuration = yaml.dump(yaml_data)

      return self.async_show_form(
          step_id="confirmation",
          description_placeholders={
              'yaml': yaml_configuration,
          }
      )

    # Pre-existing error logic.
    except config_flow.AuthenticationRequired:
      errors["base"] = "register_failed"

    except config_flow.CannotConnect:
      _LOGGER.error("Error connecting to the Hue bridge at %s", bridge.host)
      errors["base"] = "linking"

    except Exception:  # pylint: disable=broad-except
      _LOGGER.exception(
          "Unknown error connecting with Hue bridge at %s", bridge.host
      )
      errors["base"] = "linking"

    _LOGGER.info('Ended up in form.')
    return self.async_show_form(step_id="link", errors=errors)

  # Changes to hue/config_flow.py.
  async def async_step_confirmation(self, user_input=None):
    """Creates device entries after confirmation."""
    if not self._set_up_data:
      raise ValueError('Configuration flow failed.')

    return self.async_create_entry(
        title=self._set_up_data.get('title'),
        data=self._set_up_data.get('data'),
    )
