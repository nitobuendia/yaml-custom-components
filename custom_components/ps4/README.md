# PS4 Core Component

This is a `custom_component` which adds YAML configuration to the [core PS4 component](https://github.com/home-assistant/core/tree/dev/homeassistant/components/ps4). This component also allows you to configure devices via the UI.

## How to install

Copy the `ps4` folder to your `config/custom_components` folder.

## How to configure

Add the following details to your `configuration.yaml`:

```yaml
media_player:
  - platform: ps4
    name: "PS4"
    token: !secret ps4_token
    host: !secret ps4_wifi_ip
    region: "Singapore"
```

Where:

* name: The name of your device. Choose a unique device name.
* token: Your second screen PS4 token. *Documentation pending. Use the UI flow to obtain for the first time.*
* host: The IP of your PS4. Static IPs are recommended.
* region: [Region of your PlayStation](https://www.playstation.com/country-selector/index.html).

## How to use

Once the entities are created, it works the same way as the main component. Refer to the [original documentation](https://www.home-assistant.io/integrations/ps4/) for more information.
