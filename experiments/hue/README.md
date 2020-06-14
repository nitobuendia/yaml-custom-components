# Hue Experiment

This is an experiment to showcase how UI flow can act as a self-documenting feature for YAML configuration.

---

## Objectives

### What was the objective

To showcase that the UI configuration flow can be used to generate the same data needed for the `configuration.yaml` and allow the user to take the last decision on the configuration.

The underlying objective is to prove that the same `config_flow` can be used to set up both UI and YAML configuration without adding significant cost to the component owner.

### What was *not* the objective

To implement the code required to read YAML configuration. This is why we focused on Hue component which still supports YAML configuration.

This experiment is also not intended to be a `custom_component` as the original core component has all the required documentation and features, but it could be used in the future. Nonetheless, this would work if it gets installed as a `custom_component`.

---

## What was required to make it work

The only change required is to add an additional setup before `async_create_entry` that confirms the output with the user for validation.

### 0. Understanding the original device creation

The method `async_step_link` in the `hue` core component is responsible for getting the bridge information and creating the entry device. This is the logic responsible for this:

```python
async def async_step_link(self, user_input=None):
  # ...
    return self.async_create_entry(
        title=bridge.config.name,
        data={
            "host": bridge.host,
            "username": bridge.username,
            CONF_ALLOW_HUE_GROUPS: False,
        },
    )
  # ...
```

However, we wanted to add an additional step to ensure that we could validate and read the configuration. As such, we have replaced this logic with a few changes described below.

### 1. Store device data into a class attribute

Instead of directly creating the entry, we store the data required into a class attribute, which will allow us to use it later to finally create the entry.

```python
  self._set_up_data = {
      'title': title,
      'data': {
          'host': host,
          'username': username,
          'allow_hue_groups': allow_hue_groups,
      }
  }
```

> Note: while it was not required, for this experiment, we have stored the original values into variables as we will be using them in two different places on this implementation.

```python
  title = bridge.config.name
  host = bridge.host
  username = bridge.username
  allow_hue_groups = False
```

### 2. Format data into YAML Configuration format

Change the format from config_entry (`_set_up_data`) to the one required by YAML configuration.

```python
import yaml

yaml_data = {
    'hue': {
        'bridges': [{
            'host': host,
            'allow_hue_groups': allow_hue_groups,
        }]
    }
}
yaml_configuration = yaml.dump(yaml_data)
```

> Note: `yaml_data` is only required because the data required by `async_create_entry` and YAML configuration are different. We advocate to have an equivalent setup so there is no need to maintain two different schemas. If this was true, this would only have required this line: `yaml_configuration = yaml.dump(self._set_up_data)`

### 3. Show data before creating the device

We need to edit the original `async_step_link` to make a call to a new step before calling `async_create_entry`. This is done by passing the previous data into a form like this:

```python
return self.async_show_form(
    step_id="confirmation",
    description_placeholders={
        'yaml': yaml_configuration,
    }
)
```

> Note: this logic replaces the previously described `return self.async_create_entry(...)`.


### 4. Add additional step to show YAML configuration

When the form is executed, it triggers a form which will show the YAML data. Once the user submits the form, it will create the entry. The code responsible for this:

```python
  async def async_step_confirmation(self, user_input=None):
    """Creates device entries after confirmation."""
    if not self._set_up_data:
      raise ValueError('Configuration flow failed.')

    return self.async_create_entry(
        title=self._set_up_data.get('title'),
        data=self._set_up_data.get('data'),
    )
```

As a new step is created, you need to also add some translations to show the message:

```json
"confirmation": {
  "title": "Confirm Configuration",
  "description": "Your device configuration is ready. \n\nIf you prefer to set up the device manually, use this code on your `configuration.yaml`:\n\n```yaml\n{yaml}```\n\nIf you prefer to set it up via UI, simply click submit below."
}
```

---

## Conclusions

## For Component Owners

The same UI flow can be used to generate data to both manual YAML configurations as well as UI configurations. This will allow to ease the need to document the source of the `configuration.yaml` parameters. This reduces the cost for component owners to provide YAML configuration.

## For UI Users

For users who prefer to use the UI, there is no changes in their current workflows. At worst, the may have one additional step where they see the configuration. However, this can also be optionally shown only to user who enable "advanced" mode; similar to how some `Configuration` are shown only to some users. The `config_flow` allows to do this type of conditional send to one step or another.

## For YAML Users

Users who want to maintain components via YAML are encouraged to use the UI to set up if they are not sure how the data should be filled in. However, once the data is filled in, the users can edit it or create new ones using the same structure.
