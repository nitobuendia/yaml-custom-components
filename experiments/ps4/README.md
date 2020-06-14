# PS4 Experiment

This is an experiment to showcase the minimum amount of code to support YAML support.

---

## Objectives

### What was the objective

To showcase that adding YAML is not a high maintenance task if the set up logic is share between the main `config_flow`, `async_setup_entry` and the deprecated `async_setup_platform`.

By delegating the implementation of `async_setup_platform` to `async_setup_entry`, the extra code and maintenance is very low and would allow to add YAML with minimal changes.

## What was *not* the objective

This solution does not represent an end to end solution since PS4 does not require a lot of discovery of devices, OAuth flows or refresh tokens. Further experiments should explore these other areas and find a solution.

---

## What was required to make it work

The changes are very minimal and explained below.

Do note that as this was distributed as a `custom_components`, we also imported `config_flow`, `translations`, `services.yaml`, `manifest.json`, etc. This is done in order to keep support for the UI and the custom component working perfectly. However, in the case of a core component this would not have been part of the implementation.

### 1. Define schema

In order to be able to validate the schema, it is required to define it first. While this is optional, it provides a lot of functionality for very little lines.

```python
import voluptuous
from homeassistant.helpers import config_validation

PLATFORM_SCHEMA = config_validation.PLATFORM_SCHEMA.extend({
    voluptuous.Required(const.CONF_HOST): config_validation.string,
    voluptuous.Optional(const.CONF_NAME): config_validation.string,
    voluptuous.Required(const.CONF_REGION): config_validation.string,
    voluptuous.Required(const.CONF_TOKEN): config_validation.string,
})
```

This defines the 4 fields that are required to run a PS4 media player. With this code, a new entry can be created using the usual configuration:

```yaml
media_player:
  - platform: ps4
    name: "PS4"
    token: !secret ps4_token
    host: !secret ps4_wifi_ip
    region: "Singapore"`
```

### 2. Create an async_setup_platform (setup_platform)

The only task that `async_setup_platform` performs is adapting the data that comes from the configuration.yaml to the required input of `async_setup_entry`.

The schema that the device requires is formatted like this:

```python
config_entry: {
  entry_id: string  # Unique entry id. You can use uuid or simply entity id as it's unique.
  data: {  # Contains devices and platform information.
    token: string  # PS4 token obtained from the app.
    devices [  # List of devices.
      {
        host: string  # IP of the PS4.
        name: string  # Name of the PS4.
        region: string  # Region of the PS4.
      }
    ]
  }
}
```

The only condition is that entry_id and data are accessed like attributes of a class (i.e. `config_entry.entry_id` or `config_entry.data`), whereas all the data inside `config_entry.data` is shaped like a dictionary (i.e. `config_entry.data['token']` or `config_entry.data.get('devices')`).

The code that was needed to transform from our configuration to `config_entry` is like this:

```python
import collections

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
```

The method `async_setup_entry` uses a different format of `config_entry` than what the `configuration.yaml` provides. As such, we used a `namedtuple` as a proxy for a very simple class that allows us to access fields like `config_entry.data` as it's done in the PS4 entity.

This currently supports only one device, but you could just keep appending the data to devices if using the same token or create a full new `Config` if it comes from a different platform.

### 3. Documentation

When manual configuration is available, the last step would be adding some documentation. In this case, we advocate to leave very minimal configuration and rely on the UI flow to generate the details if ever needed. This way, documentation does not become a burden.

Further experiments can explore how the UI can become a source of data for configuration.yaml without having to create advanced documentation.

### 4. Delegating all the other code

For those of you reading this with the intention of creating similar `custom_components`, I want to add a bit of explanation on how to achieve it. This is not part of the experiment, but of the `custom_components` logic and it would not be needed if the rest of the code was integrated in the core component.

You need to copy `services.yaml` and `manifest.json` to describe your services. This will allow the platform to know all the services that are required by your system.

Do not copy the whole component, you can easily delegate the implementation by doing this:

```python
from homeassistant.components.ps4 import media_player as ps4_media_player

async def async_setup_entry(hass, config_entry, async_add_entities):
  await ps4_media_player.async_setup_entry(
      hass, config_entry, async_add_entities)
```

This way, any changes on the core component will not affect your component and you will be able to take advantage of them by simply maintaining the Adapter logic.


If you want to support the UI flow as well, you can simply use the same mechanism to delegate it:

```python
from homeassistant import config_entries
from homeassistant.components.ps4 import config_flow

@config_entries.HANDLERS.register(const.DOMAIN)
class PlayStation4FlowHandler(config_flow.PlayStation4FlowHandler):

  def __init__(self):
    super().__init__()
```

This will implement the same UI flow that the core component has without having to do any coding. In other experiments, I will showcase a better way to improve the UI flow so it also spits out the required code for `configuration.yaml`, but for now this is a good sample start.

If you do this, you also want to import the `translations` folder so the messages show. In this experiments, I copied both manually, but it might best to have a way to copy the core folder to your custom_components automatically. This could be showcased in another experiments, but the main focus is to show how to minimize the core components support for YAML.

As for the constants, in my case I decided to create my own `const.py` to have flexibility, but virtually all the constants are coming from core constants or ps4 constants really:

```python
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
```
