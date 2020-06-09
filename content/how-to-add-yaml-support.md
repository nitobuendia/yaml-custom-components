# How to Fix and Add YAML Support

In the post [The future of YAML](https://community.home-assistant.io/t/the-future-of-yaml/186879), Home-Assistant team explains the decision of [ADR0010](https://github.com/home-assistant/architecture/blob/master/adr/0010-integration-configuration.md) to drop YAML support for integrations.

In [this article](https://github.com/nitobuendia/yaml-custom-components/blob/master/content/the-reasons-behind.md), we have explained how we understand that some of the reasoning of this article is compatible with YAML support.

One of the areas that can be expanded is on the cost of maintenance and, more specifically, on how a fix to this problem could be implemented. If you do not want to read the whole post, you can jump directly to the Conclusions at the end and only read those sections on those opinions you want to debate or comment.

---

*Before starting and adventuring into fixes we need to understand where is the problem and cost of these solutions.*

## The cost of maintenance

### Double onboarding process
One of the main cost of YAML is that it produces two different onboarding flows: one in the UI that produces JSON files; and one that reads from `configuration.yaml` and produces a similar onboarding.

### Changes in data structures
Changing the data structures, especially in the configuration, is another point. This is not so much a cost to the maintainers to the users who need to change the configuration file when new versions are coming.

---

*How do we fix these problems?*

---

## [1] Adapter Pattern

[Adapter Pattern](https://en.wikipedia.org/wiki/Adapter_pattern) is a software design pattern that allows one instance to be used like another. You could think of it as a translator.

In our case, we would have a function or class that receives the `configuration.yaml` data, reads it and adapts it to the structure that is required by the UI workflow.

### Data Structures

This is the data that is generated from the UI workflow and stored in ``:

```json
  {
      "connection_class": "local_poll",
      "data": {
          "devices": [
              {
                  "host": "192.168.86.150",
                  "name": "PlayStation 4",
                  "region": "Singapore"
              }
          ],
          "token": "aef4dadbbb-token-redacted-690df0c3293ab6c69d0f690fb5915a9f8"
      },
      "domain": "ps4",
      "entry_id": "56d918766f1d44bf9c2526bbea9aafb9",
      "options": {},
      "source": "user",
      "system_options": {
          "disable_new_entities": false
      },
      "title": "PlayStation 4",
      "unique_id": null,
      "version": 3
  }
```

From this structure, the parameters that are pure configuration are: host, name, region and token.

As such, this could have been stored in YAML as follows:

```yaml
host: 192.168.86.150
name: "PlayStation 4"
region: "Singapore"
token: "aef4dadbbb-token-redacted-690df0c3293ab6c69d0f690fb5915a9f8"
```

> Note: storing the token like this is not a good idea. We will touch on this topic below, but for the purpose of this topic, let's just compare structures.

### Device initialization

Checking the existing code of the [PS4 component](https://github.com/home-assistant/core/blob/1edbdcb67b8062b9c558bf24f77be65090c2d2cd/homeassistant/components/ps4/media_player.py#L58), you can see that the data that the system requires is exactly that:

```python
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up PS4 from a config entry."""
    config = config_entry
    creds = config.data[CONF_TOKEN]
    device_list = []
    for device in config.data["devices"]:
        host = device[CONF_HOST]
        region = device[CONF_REGION]
        name = device[CONF_NAME]
        ps4 = pyps4.Ps4Async(host, creds, device_name=DEFAULT_ALIAS)
        device_list.append(PS4Device(config, name, host, region, ps4, creds))
    async_add_entities(device_list, update_before_add=True)


class PS4Device(MediaPlayerEntity):
    """Representation of a PS4."""

    def __init__(self, config, name, host, region, ps4, creds):
        """Initialize the ps4 device."""
        self._entry_id = config.entry_id
        self._ps4 = ps4
        self._host = host
        self._name = name
        self._region = region
        self._creds = creds
        self._state = None
        self._media_content_id = None
        self._media_title = None
        self._media_image = None
        self._media_type = None
        self._source = None
        self._games = {}
        self._source_list = []
        self._retry = 0
        self._disconnected = False
        self._info = None
        self._unique_id = None
```

In particular:

* token: `creds = config.data[CONF_TOKEN]`
* host: `host = device[CONF_HOST]`
* region: `region = device[CONF_REGION]`
* name: `name = device[CONF_NAME]`
* entry_id: `self._entry_id = config.entry_id`

Both entries contain the same required data to work, except for `entry_id` which is a unique id. For this purpose, `entity_id` or a `uuid` [can be used](https://github.com/home-assistant/core/blob/7722e417ad61689cb07825d31adabcddc18c475c/tests/common.py#L688).

### Translating data structures

However, while we have the same data, we do not have it in the same exact format. This is where the adaptor pattern comes in:

```python
import collections
from homeassistant.components.ps4 import media_player as ps4_media_player

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
  entry_id = util.slugify(name)

  # Format it in the new config_entry.yaml format
  config_entry = Config(
      entry_id,
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

  await async_setup_entry(hass, config_entry, async_add_entities)

  return True
```

In this case `async_setup_platform` is the function that gets triggered to create entities from `configuration.yaml` whereas `async_setup_entry` is used to initialize the ones coming from the UI flow.

What we are doing in the code above is that when `async_setup_platform` is triggered the configuration data is formatted exactly as it is needed for the existing ps4 `async_setup_entry` component (i.e. like the JSON we showed before). In particular like this:

```python
  config_entry = Config(
      entry_id,
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
```

This allows to have both workflows without having to maintain two different workflows as the `async_setup_platform` simply translates the code into the one needed for `async_setup_entry` and only this one workflow needs to be maintained.

> Note: this is not exactly an adapter pattern as we are not really wrapping the actual `media_player` into another class that translates everything. However, you can see them as equivalent as what it does is allowing the YAML to configure the `async_setup_entry` method without originally having the required structured data for the interface.

### Current usage and implementation

Some has raised this as something [not desirable or against guidelines](https://community.home-assistant.io/t/the-future-of-yaml/186879/616).

First, Adapter Pattern, [and its variants](https://sourcemaking.com/design_patterns/adapter), are a commonly used software development pattern. The solution is perfectly valid Python and works on Home-Assistant. Any guidelines against them are mere decisions not based on software principles or Python language.

Second, this pattern is currently used across several platforms today.

MQTT devices like [light](https://github.com/home-assistant/core/blob/7e387f93d622231ee7ed6128ee7d54c103ac48c7/homeassistant/components/mqtt/light/__init__.py) or [vacuum](https://github.com/home-assistant/core/blob/7e387f93d622231ee7ed6128ee7d54c103ac48c7/homeassistant/components/mqtt/vacuum/__init__.py#L34) use a similar implementation:

```python
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up MQTT vacuum through configuration.yaml."""
    await _async_setup_entity(config, async_add_entities, discovery_info)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up MQTT vacuum dynamically through MQTT discovery."""

    async def async_discover(discovery_payload):
        """Discover and add a MQTT vacuum."""
        discovery_data = discovery_payload.discovery_data
        try:
            config = PLATFORM_SCHEMA(discovery_payload)
            await _async_setup_entity(
                config, async_add_entities, config_entry, discovery_data
            )
        except Exception:
            clear_discovery_hash(hass, discovery_data[ATTR_DISCOVERY_HASH])
            raise

    async_dispatcher_connect(
        hass, MQTT_DISCOVERY_NEW.format(DOMAIN, "mqtt"), async_discover
    )


async def _async_setup_entity(
    config, async_add_entities, config_entry, discovery_data=None
):
    """Set up the MQTT vacuum."""
    setup_entity = {LEGACY: async_setup_entity_legacy, STATE: async_setup_entity_state}
    await setup_entity[config[CONF_SCHEMA]](
        config, async_add_entities, config_entry, discovery_data
    )
```

Both `async_setup_platform` and `async_setup_entry` methods reads and adjust the date and delegate to `_async_setup_entity`. This can also be found on more advanced cases like [cast media_player](https://github.com/home-assistant/core/blob/7e56f2cc0e2ff3ed106bcc0e3bcc14888aefe755/homeassistant/components/cast/media_player.py#L111) or [met weather](https://github.com/home-assistant/core/blob/4e3b079a29c95beb2f5f9abf9db426d2c25f4fbc/homeassistant/components/met/weather.py#L56).

A reverse of this approach can be found on all demo devices like [demo climate](https://github.com/home-assistant/core/blob/1593bdf2e9cc4840a7dc3cbca843c98f10a023c9/homeassistant/components/demo/climate.py#L95) where `async_setup_entry` calls `async_setup_platform` instead of vice versa:

```python
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Demo climate devices."""
    async_add_entities(
        [
            ... edited ...
        ]
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo climate devices config entry."""
    await async_setup_platform(hass, {}, async_add_entities)
```


---

## [2] Migrations and advanced translations

The Adapter Pattern solves the problem as long as the data required is equivalent. However, if the data structure changes, the method or data structure needs to change.

Fixing this would be an extra-mile, but it can be done within existing infrastructure.

### Breaking changes
Breaking changes is one of the reasons that the post mentions as a reason to move away from YAML. However, [as explained](https://github.com/nitobuendia/yaml-custom-components/blob/master/content/the-reasons-behind.md), these problems are not exclusive to YAML and the JSON has the same problem. We will talk in this section how the current system fixes this and how it also applies to YAML.

### Breaking changes for the user
One option here would be not making any fixes. UI should still be the default configuration. If you use it, the developers maintain the fix for you. If you opt-in for manual configuration, then it is up to the user to keep these up to date and deal with breaking changes. It is a trade off.

There are, nonetheless, ways to solve this problem.

### Types of changes

#### Changes in structure
This is a change in the same of the structure. This is not a problem as long as the required parameters are the same, as the Adapter logic would just change to reshape the structure of the data with a few lines of code (i.e. still low maintenance).

You could just change from:

```python
  config_entry = Config(
      entry_id,
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
```

To:

```python
  config_entry = Config(
      entry_id,
      {
          const.CONF_DEVICES: [
              {
                  const.CONF_TOKEN: token,
                  const.CONF_NAME: name,
                  const.CONF_HOST: host,
                  const.CONF_REGION: region,
              },
          ],
      }
  )
```

This would not affect the user and would solve the issue with one line change.

#### Renaming of attributes
When a parameter still remains but receives a new name, it creates problem with the existing configuration. For example: what if the parameter is no longer `host` but `hosts`?

On the code, the obvious fix is to change this line from `const.CONF_HOST: host,` to `const.CONF_HOSTS: host,`. However, it is not as simple as that since the value is also obtained like this: `host = config.get(const.CONF_HOST)`.

If you want to support both `host` and `hosts`, it can become a mess:

```python
# Option 1.
hosts = config.get(const.CONF_HOST) or config.get(const.CONF_HOSTS)
# Option 2.
hosts = config.get(const.CONF_HOST, config.get(const.CONF_HOSTS))
```

One already discussed option is to simply break the configuration as the user chose this method. However, this can also be fixed with migrations which will be covered later.

#### Dropped fields
Dropped fields do not constitute a problem as these could simply be ignored or highlighted on the configuration.

#### New field
This is a major issue in any flow because you need new input from the user; whether it is added via YAML or via a UI flow, it is irrelevant; both require user input.

### Migrations, versioning data

The way the UI flow solves this problem is by having a migration system. This is an [example for the PS4 component](https://github.com/home-assistant/core/blob/1edbdcb67b8062b9c558bf24f77be65090c2d2cd/homeassistant/components/ps4/__init__.py#L77):

```python
async def async_migrate_entry(hass, entry):
    """Migrate old entry."""
    config_entries = hass.config_entries
    data = entry.data
    version = entry.version

    _LOGGER.debug("Migrating PS4 entry from Version %s", version)

    reason = {
        1: "Region codes have changed",
        2: "Format for Unique ID for entity registry has changed",
    }

    # Migrate Version 1 -> Version 2: New region codes.
    if version == 1:
        loc = await location.async_detect_location_info(
            hass.helpers.aiohttp_client.async_get_clientsession()
        )
        if loc:
            country = loc.country_name
            if country in COUNTRIES:
                for device in data["devices"]:
                    device[CONF_REGION] = country
                version = entry.version = 2
                config_entries.async_update_entry(entry, data=data)
                _LOGGER.info(
                    "PlayStation 4 Config Updated: \
                    Region changed to: %s",
                    country,
                )

    # Migrate Version 2 -> Version 3: Update identifier format.
    if version == 2:
        # Prevent changing entity_id. Updates entity registry.
        registry = await entity_registry.async_get_registry(hass)

        for entity_id, e_entry in registry.entities.items():
            if e_entry.config_entry_id == entry.entry_id:
                unique_id = e_entry.unique_id

                # Remove old entity entry.
                registry.async_remove(entity_id)

                # Format old unique_id.
                unique_id = format_unique_id(entry.data[CONF_TOKEN], unique_id)

                # Create new entry with old entity_id.
                new_id = split_entity_id(entity_id)[1]
                registry.async_get_or_create(
                    "media_player",
                    DOMAIN,
                    unique_id,
                    suggested_object_id=new_id,
                    config_entry=entry,
                    device_id=e_entry.device_id,
                )
                entry.version = 3
                _LOGGER.info(
                    "PlayStation 4 identifier for entity: %s \
                    has changed",
                    entity_id,
                )
                config_entries.async_update_entry(entry)
                return True

    msg = f"""{reason[version]} for the PlayStation 4 Integration.
            Please remove the PS4 Integration and re-configure
            [here](/config/integrations)."""

    hass.components.persistent_notification.async_create(
        title="PlayStation 4 Integration Configuration Requires Update",
        message=msg,
        notification_id="config_entry_migration",
    )
    return False
```

What this does is move from the data structure in version 1 to version 2, from version 2 to version 3. The version is stored in the JSON (`"version": 3` above).

Since our Adapter Pattern is converting from `configuration.yaml` to the same format as the JSON, this method can also be used in YAML.

For example:

```yaml
host: 192.168.86.150
name: "PlayStation 4"
region: "Singapore"
token: "aef4dadbbb-token-redacted-690df0c3293ab6c69d0f690fb5915a9f8"
version: 1
```

This gets placed into config_entry:

```python
  config_entry = Config(
      entry_id,
      {
          const.CONF_TOKEN: token,
          const.CONF_DEVICES: [
              {
                  const.CONF_HOST: host,
                  const.CONF_NAME: name,
                  const.CONF_REGION: region,
              },
          ],
      },
      version,
  )
```

Which runs through `async_migrate_entry` and outputs it in version 3, the same way as it natively does with `config_entries = hass.config_entries`.

This does require some thought on writing this function in a way that simply does the job of translating without changes in the registry (which is not used by the `configuration.yaml`) until the moment where the entity gets inserted.

> Note: yes, this involves a bit more of work; but I do not think this would be an expectation for the YAML maintenance. Just a way to bring both infrastructures together without having to maintain two different flows.

---

## [3] OAuth and equivalent workflows

One of the great additions that UI system is bringing is good integration flows. Some of these are inevitable and improving them are a great idea.

### The system before UI flows
If you wanted to get an OAuth token where the user needs to give permission. In the past, this was done via notifications, redirecting URLs and it was all non-Standard and chaotic.

For example, this is how [Google Calendar OAuth flow works](https://github.com/home-assistant/core/blob/1edbdcb67b8062b9c558bf24f77be65090c2d2cd/homeassistant/components/google/calendar.py#L43):

```python
def setup_platform(hass, config, add_entities, disc_info=None):
    """Set up the calendar platform for event devices."""
    if disc_info is None:
        return

    if not any(data[CONF_TRACK] for data in disc_info[CONF_ENTITIES]):
        return

    calendar_service = GoogleCalendarService(hass.config.path(TOKEN_FILE))
    entities = []
    for data in disc_info[CONF_ENTITIES]:
        if not data[CONF_TRACK]:
            continue
        entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, data[CONF_DEVICE_ID], hass=hass
        )
        entity = GoogleCalendarEventDevice(
            calendar_service, disc_info[CONF_CAL_ID], data, entity_id
        )
        entities.append(entity)

    add_entities(entities, True)
```

The path relies on a file stored in `hass.config.path(TOKEN_FILE)` which is created [like this](https://github.com/home-assistant/core/blob/1edbdcb67b8062b9c558bf24f77be65090c2d2cd/homeassistant/components/google/__init__.py#L130):

```python

def do_authentication(hass, hass_config, config):
    """Notify user of actions and authenticate.
    Notify user of user_code and verification_url then poll
    until we have an access token.
    """
    oauth = OAuth2WebServerFlow(
        client_id=config[CONF_CLIENT_ID],
        client_secret=config[CONF_CLIENT_SECRET],
        scope="https://www.googleapis.com/auth/calendar",
        redirect_uri="Home-Assistant.io",
    )
    try:
        dev_flow = oauth.step1_get_device_and_user_codes()
    except OAuth2DeviceCodeError as err:
        hass.components.persistent_notification.create(
            f"Error: {err}<br />You will need to restart hass after fixing." "",
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID,
        )
        return False

    hass.components.persistent_notification.create(
        (
            f"In order to authorize Home-Assistant to view your calendars "
            f'you must visit: <a href="{dev_flow.verification_url}" target="_blank">{dev_flow.verification_url}</a> and enter '
            f"code: {dev_flow.user_code}"
        ),
        title=NOTIFICATION_TITLE,
        notification_id=NOTIFICATION_ID,
    )

    def step2_exchange(now):
        """Keep trying to validate the user_code until it expires."""
        if now >= dt.as_local(dev_flow.user_code_expiry):
            hass.components.persistent_notification.create(
                "Authentication code expired, please restart "
                "Home-Assistant and try again",
                title=NOTIFICATION_TITLE,
                notification_id=NOTIFICATION_ID,
            )
            listener()

        try:
            credentials = oauth.step2_exchange(device_flow_info=dev_flow)
        except FlowExchangeError:
            # not ready yet, call again
            return

        storage = Storage(hass.config.path(TOKEN_FILE))
        storage.put(credentials)
        do_setup(hass, hass_config, config)
        listener()
        hass.components.persistent_notification.create(
            (
                f"We are all setup now. Check {YAML_DEVICES} for calendars that have "
                f"been found"
            ),
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID,
        )

    listener = track_time_change(
        hass, step2_exchange, second=range(0, 60, dev_flow.interval)
    )

    return True


def setup(hass, config):
    """Set up the Google platform."""
    if DATA_INDEX not in hass.data:
        hass.data[DATA_INDEX] = {}

    conf = config.get(DOMAIN, {})
    if not conf:
        # component is set up by tts platform
        return True

    token_file = hass.config.path(TOKEN_FILE)
    if not os.path.isfile(token_file):
        do_authentication(hass, config, conf)
    else:
        if not check_correct_scopes(token_file):
            do_authentication(hass, config, conf)
        else:
            do_setup(hass, config, conf)

    return True
```

This uses notifications, and non-standardized methods to make it work:

```python
    hass.components.persistent_notification.create(
        (
            f"In order to authorize Home-Assistant to view your calendars "
            f'you must visit: <a href="{dev_flow.verification_url}" target="_blank">{dev_flow.verification_url}</a> and enter '
            f"code: {dev_flow.user_code}"
        ),
        title=NOTIFICATION_TITLE,
        notification_id=NOTIFICATION_ID,
    )
```

We can agree this is not a good user experience. The new onboarding flows, with a UI is a new standard for these onboarding flows (e.g. [PS4](https://github.com/home-assistant/core/blob/1edbdcb67b8062b9c558bf24f77be65090c2d2cd/homeassistant/components/ps4/config_flow.py)).

However, there are a few considerations that needs to be done.

### Initialization of device flow

The fact that standardizing the OAuth flow is positive is not a synonym that this process must be initialized by the UI. The very same processes can be initialized starting from a `configuration.yaml` entry. Indeed, that's how they have worked until now.

If you do not have the token information, then this config flow is triggered regardless of whether it has been done in the UI or by adding a new entry on the configuration file.

### Reading and storing private information

The second part is storing the input information.

Until now, the configuration file would hold the configuration information whereas in some cases the OAuth access or refresh tokens were stored in files. In the new system, both the configuration and token and alike information get stored together.

There are advantages and disadvantages to both approaches:

* Splitting the data allows for different use cases of configuration vs private data.
* Merging the data eases retrieval and has one common place for the sensor.

Each advantage in one set up is a disadvantage on the other setup.

Nonetheless, what is clear is that the same UI flow that can store all the information, can also be used to store only token/private information even when the configuration comes from the configuration files. As such, this is not a breaking change, but one that can co-live with the existence of YAML.

If files are not a good approach, this private information could also be shown to the user to add to the configuration. This, of course, still has the same privacy and security issues as the existing system; but those are still true in the alternative version as all this is still stored in plain text.

Moreover, the Adapter Pattern can be used to merge the data from both configuration and token data into one source reducing this again to the same common problem which is trivial to solve.

---

## [4] Different implementations for different solutions

All the previous solutions can be implemented in several ways with different advantages or disadvantages.

### Native components

The best and easiest way is that the previous logic gets implemented on the component itself. This allows for the most configuration.

Of course, here there is the discussion about `cost of maintenance` again. One solution to this is to make it optional. The only must have flow is the UI workflow. However, if someone wants to implement YAML, they should be encouraged to do so because

1. This is positive for users as it does not hamper existing options, but increases their options.
2. Rejecting contributions from contributors who want to improve the product and support is demotivating goes against the same principles that were quoted on the article as reasons for this change.

### Centralized system

A net positive way to solve this would be having a centralized Adapter Pattern solution that reads from all the configurations and transforms it into the input required for each module.

This would be a big win as no additional code, no matter how small, needs to be created for each component; but it solves the problem in a centralized manner with economies of scale in development.

However, this would require that all the integrations use a common standard on how to store information; which is unclear today, and it would make very hard to add small variations per platform which can increase coverage. Adding customizations for each component on the central system would be messy and would start defeating the purpose of Single Responsibility Principle.

### Custom components

Until the Home-Assistant team accepts that YAML should be a first class citizen and revokes [ADR0010](https://github.com/home-assistant/architecture/blob/master/adr/0010-integration-configuration.md), the only solution that contributors can do is creating custom components.

You can see an [minimal example on this GitHub component](https://github.com/nitobuendia/yaml-custom-components/tree/master/custom_components/ps4).

This is not ideal as a user would have to install a custom component for any and all the components that would like to use via configuration. This should be supported natively.

This will also be the argument that might be yielded by the Home-Assistant team to argue that they support this use case and encourage open source; while rejecting valuable contributions to the main application that we love.

In addition, this will only be possible for as long as `async_setup_platform` and `setup_platform` are maintained. However, if no official platform is created this way, there is no guarantee that even these functions will exist in the future.

It was also clear in the past that YAML was not going away at all, now it's going away only for Integrations. Who knows whether this will also be remove for Custom Integrations in the future.

---

## Conclusions

1. Adding YAML support can be done by redirecting calls from `async_setup_platform` to `async_setup_entry` without having to maintain two flows; therefore, not increasing maintenance cost.
1. UI should be a must and first, YAML support can be secondary and optional. However, YAML support should not be prohibited or discouraged.
1. Breakages for those who opt in for YAML instead of UI are expected; similar to what happens when you use Lovelace dashboards.
1. If, and only if, we wanted to provide a better YAML experience (at, here yes, greater maintenance cost):

    1. The existing UI flows also work to get the data for YAML configuration, providing the best of both experiences.
    1. The same migration code that is used today for the UI flows can be used for transforming the YAML contents with minimal changes.
