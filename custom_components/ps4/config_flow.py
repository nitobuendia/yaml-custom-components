"""Delegates config flow to core component."""

from homeassistant import config_entries
from homeassistant.components.ps4 import config_flow

from . import const


# TODO(nitobuendia): add flow to obtain token dynamically.
@config_entries.HANDLERS.register(const.DOMAIN)
class PlayStation4FlowHandler(config_flow.PlayStation4FlowHandler):

  def __init__(self):
    super().__init__()
