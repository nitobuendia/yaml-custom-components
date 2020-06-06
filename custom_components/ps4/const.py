"""Contants for PS4 Wrapper component."""

from homeassistant import const

# Platform constants.
DOMAIN = 'ps4'
PLATFORMS = ['media_player']

# Attributes.
CONF_HOST = const.CONF_HOST
CONF_NAME = const.CONF_NAME
CONF_REGION = const.CONF_REGION
CONF_TOKEN = const.CONF_TOKEN

# Secondary data attributes.
CONF_DATA = const.CONF_SERVICE_DATA
CONF_DEVICES = const.CONF_DEVICES
CONF_ENTRY_ID = 'entry_id'

# Services.
SERVICE_SEND_COMMAND = 'send_command'

# Service attributes.
ATTR_ENTITY_ID = const.ATTR_ENTITY_ID
ATTR_COMMAND = const.ATTR_COMMAND

# Default values.
DEFAULT_NAME = 'PlayStation'
