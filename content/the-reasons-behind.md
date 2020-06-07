# What's the reason to drop YAML support from integration

In the post [The future of YAML](https://community.home-assistant.io/t/the-future-of-yaml/186879), Home-Assistant team explains the decision of [ADR0010](https://github.com/home-assistant/architecture/blob/master/adr/0010-integration-configuration.md) to drop YAML support for integrations.

This decision effectively makes support for YAML on Integrations maintenance mode only:

> * Any new integration that communicates with devices and/or services, must use configuration via the UI. Configuration via YAML is only allowed in very rare cases, which will be determined on a case by case basis.
> * Existing integrations that communicate with devices and/or services, are allowed and encouraged to implement configuration via the UI and remove YAML support.
> * We will no longer accept any changes to the YAML configuration for existing integrations that communicate with devices and/or services.

Some of the decisions to make this decision are:

*If you do not want to read the whole thing, jump to the conclusions; and only read the sections where you do not agree.*

---

## Making thing easier
> "Making things easier" by "enabling and empowering people with managing their Home Assistant instance via the user interface".

It is undoubtedly true that using UI is much easier for most basic cases, non-Tech savvy people and the ones who prefer convenience; all of which are reasons mentioned in the article.

Making UI first is a great decision for Home-Assistant. However, making UI only is a problem as it breaks a few user flows. If you want a full list, you can [read this article](https://github.com/nitobuendia/yaml-custom-components/blob/master/content/how-to-add-yaml-support.md), but highlighting some:

1. All current configurations will eventually break.
1. No easy bulk addition or support.
1. No partial versioning of components.
1. No flexible backups and restoring.
1. Reduced shareability for integrations and related entities.
1. Increased difficulty in troubleshooting.
1. Reduced documentation for users and developers.

As such, it is not true that this makes things easier; it also makes things harder for many users and use cases. Some of which also happen to be contributing to the ecosystem of components or add-ons.

---

## Breaking changes

### Advanced users: the right to break your system
We have all been there, the system broke because of an update as the interfaces are changed. It is painful. Home-Assistant team is claiming that the UI approach is the solution.

First and foremost, this is not just about not breaking the system, but about choice.

Today, in `lovelace` you can manage your Dashboards in the UI. However, you can also change it to manual mode and configure them in YAML. Of course, doing so, you can break the UI by implementing the wrong code. However, this is supported.

In other words, it is possible to have a UI-first method for those who do not want to break the system and want the ease; and a YAML method with other advantages, but with the disclaimer that it is at your own risk.

As such, it is not enough reason that breaking the system should be the main driver as this is an option that users may voluntarily opt-in when the UI is the first system.

### The fix is not exclusive to the UI system
Yes, the new UI config flow will solve the breaking changes. However, they are not telling you why or how the UI is able to solve the breaking changes.

The problem comes from a change in schema, new fields may be required or dropped, or existing ones changed. Suddenly, the data you have does not match the data you need.

The way this is handled is by the UI system is by creating a migration. This is an example from [ps4 component](https://github.com/home-assistant/core/blob/2f6ffe706873ce975792efca40f01c54828a7da5/homeassistant/components/ps4/__init__.py):

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

What this method is doing is reading the all the configuration, making changes in structure of the data and updating the version so it can be used in the current schema.

This is great, it is a great idea and way to handle it. However, what they do not tell you is that this is not something that can only be done with the new `.storage` JSON files.

The data in `config_entries = hass.config_entries` and `data = entry.data` are structured data similar to a dictionary. This data could also come from the YAML files and be supported exactly the same way.

As such, while this is a great improvement, it is not an improvement that is exclusive to the new UI methodology, but something that can easily be ported to YAML configuration as well.

---

## Privacy and Security

One of the claims to make the new changes is privacy and security. Home-Assistant has access to many APIs that can affect your home, life and expose your personal information.

It is true that this data should be protected as much as possible. The reasoning here is that having this data in YAML is unsafe. However, the new system stores and leverage this data as much as other systems.

This is are some excerpts from `core.config_entries`:

**Hue**:
```json
  {
      "connection_class": "local_poll",
      "data": {
          "bridge_id": "00178-redacted-FE6A3B07",
          "host": "192.168.1.2",
          "username": "zA2ksQx-redacted-hBaXnzEO80g1KKjKxrDaYpNao"
      },
      "domain": "hue",
      "entry_id": "dd73b58e701f4b0486be84a80c18d592",
      "options": {},
      "source": "user",
      "system_options": {
          "disable_new_entities": false
      },
      "title": "Living Room",
      "unique_id": "0017886a3b07",
      "version": 1
  },
```

**Spotify**:
```json
  "data": {
      "auth_implementation": "spotify",
      "id": "fv-user-redacted--dia",
      "name": "fv-user-redacted--dia",
      "token": {
          "access_token": "BQAUdEGaP1elVLZvPRcYUG-token-redacted-GvIxuCJX4weTy2jMSoeX0bh4ntHkjt_pjBx3MLgxVWRcQFiFUaq6pgdS3e5w2J5e25V0f3S76Fr8X-Br8-GKRuznjd4kC4",
          "expires_at": 1591521655.1966686,
          "expires_in": 3600,
          "refresh_token": "AQC7-z8BykITxy06fOx_YkP67u-refresh-token-redacted-_rMj6F4CJdep-XeWNAsS9IytKkcAc18x-9N6LvX1O4o-ddxKnhkx9veLxvqN",
          "scope": "user-modify-playback-state user-read-playback-state user-read-private",
          "token_type": "Bearer"
      }
  },
```

The current system still stores the same sensitive data like tokens, or usernames.

The only use case where this would be true is when sensitive data like username and password is required only once and may not thereafter. In this cases, this should not be part of the YAML configuration either. It should create an OAuth flow that allows you to store retrieve the data and store it safely (e.g. tokens).

Now, this is a good idea. Separating PII and sensitive details like usernames and passwords (why are we using those in the first place?!) or tokens and storing them securely is a priority. However, they need to be store as they need to be used.

And yes, of course, this requires UI, no one said the opposite; but the basic configuration still remains in YAML and can be used anywhere.

As such, this point is about improving the onboarding OAuth process, not about whether data should be stored in JSON under `.storage` or YAML. The approach of having the configuration in YAML and storing sensitive data in private files. Even better if we start encrypting and protecting this data rather than just hiding it and hoping to get [security through obscurity](https://en.wikipedia.org/wiki/Security_through_obscurity).

---

## A big maintenance cost
One of the main reasons is that doing all that was said before and maintaining a dual system would yield high maintenance cost for the contributors.

> Some contributors have decided to remove the YAML support to reduce their maintenance and support burden. The amount of energy that needs to be put in (to maintain both capabilities) can be too much and is complex. We have to understand and accept that. If we do not do that, a contributor could simply stop contributing.

It is partially true, but only partially.

### Where is the data?
What we have not told is where those complains are, or who are those contributors. Not with the objective of pointing fingers, but with the objective of transparency:

* How many contributors have complained?
* How many contributors have left because of YAML support?
* How does this compare to the ones that are complaining against the removal of YAML?

Checking the [first ~100 responses on the blog post](https://community.home-assistant.io/t/the-future-of-yaml/186879/627), these are some of the numbers that we get:

```text
Blog post: 1
  + Positive: 7
  + Neutral: 8
  + Negative: 18
  + Replies to others: 8
= Total Unique: 42
  + Repeated: 55
= Total Responses: 97
```

Crunching the numbers:

* 43% of the unique users in the first 100 posts are against the change.
* 2.5x users are against the change compared to those in favour.

Extending the numbers:

* At the moment, there are 600 responses on the post. Assuming the same ratio:
  * In 100 responses, 18 were unique users with a negative view of the change.
  * In 600 responses, this could be 108 users.

We could say that 108 users are not that many. However, let's not forget that this represents 42% of the ones who participated and that for every user who is actively complaining there are many who are not. For examples, some studies say that only [1 in 25 of annoyed users would complain](https://www.superoffice.com/blog/customer-complaints-good-for-business/). If this is true, we may have over 2,500+ users who are not happy with the decision.

### YAML is not the cost
YAML is just a structured language. This is currently being replaced with JSON files. Both are equivalent and inter-exchangeable if they have the same or equivalent structure.

Example:

**YAML**

```yaml
host: 127.0.0.1
name: Device
```

**JSON**

```json
{
  "host": "127.0.0.1",
  "name": "Device"
}
```

**Python**
```python
{
  'host': '127.0.0.1',
  'name': 'Device',
}
```

All these representations are equivalent and can be translated to each other. As such, this is not an inherent problem to YAML itself.

Additionally, YAML support is still available in other areas. So the capabilities to making that translation are still in the system and maintained. In any case, no one would complain if YAML gets changed to JSON or any other structured language. The argument here is to have an easily configurable format that can be created, edited or copied over.

As such, it is not a problem with YAML, but with how it is being used to create devices; and this can be refuted below.

### A simple solution
There are a few ways this can be solved. The easiest one would be an [Adapter Pattern](https://en.wikipedia.org/wiki/Adapter_pattern) which basically translates the YAML configuration into whatever same data the UI flow produces.

This an example of an implementation of `async_setup_platform` that reads the data from `configuration.yaml` and passes it to PS4 component (that can only be configured in the UI:

```python
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

  # Format it in the new config_entry JSON format.
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

This is much simpler logic that the one that was added for the migration across versions. Additionally, this only needs to be updated if there ever are changes in schema.

To read and discuss further about potential solutions you can read this article on [what would imply adding YAML support](https://github.com/nitobuendia/yaml-custom-components/blob/master/content/how-to-add-yaml-support.md).

### Respecting contributors time

In the post, Home-Assistant team celebrates the work of contributors.

> Those contributors do this in their free spare time, for which we all are eternally grateful. It is their work that enables Home Assistant to do what it can right now. It is what automates your home.

This is great. We all are grateful and love this work. They go even further to say that:

> Unfortunately, such a move creates breaking changes and often leads to a few pretty de-motivating comments, towards the contributor and the project in general. This is harmful to everybody, as the contributors get demotivated or, even worse, don’t want to implement new features or create a breaking change.

This sounds tough. No one wants to be in that situation. However, this is Home-Assistant decision on the same post:

> * Any new integration that communicates with devices and/or services, must use configuration via the UI. Configuration via YAML is only allowed in very rare cases, which will be determined on a case by case basis.
> * Existing integrations that communicate with devices and/or services, are allowed and encouraged to implement configuration via the UI and remove YAML support.
> * We will no longer accept any changes to the YAML configuration for existing integrations that communicate with devices and/or services.

In other words, if you are contributor who wants to dedicate your "spare time" to "enables Home Assistant to do what it can right now", you are not allowed. This is "de-motivating" for the contributor who wants to create value; risking the "contributors [to] get demotivated" and "harmful to everybody" as it affects both the users (who want the YAML support) and the contributors who are willing to invest the time to add it.

If adding YAML support is really costly and troublesome (which we already explained that it doesn't need to be), then let's make it optional. Contributors are not required to implement it. However, if a contributor is willing to spend their spare time, let's allow and encourage them to do it as it creates values for the users.

As such, if we really care about users and contributors, we should encourage contributors to create value; not discourage them from contributing.

---

## Conclusions

1. UI makes it easier for many users; but removing YAML breaks some user flows.
1. The migration system implemented to avoid breaking changes can also work for YAML configuration.
1. The problem of breaking exists in other systems like Lovelace Dashboards; this duality of UI with manual advance configuration empowers both "convenient" and "advanced" users with different benefits and costs for each.
1. Yes, storing sensitive data and token is problematic. Splitting `configuration` and `sensitive data` in a good onboarding flow is not exclusive to UI and can live with YAML support. Privacy and security should go beyond just that.
1. Using an Adapter Pattern can make it very easy to add YAML support without high maintenance cost. If we do not want to place burden in one contributor, let's make it optional so only Contributors who want to add it will; instead of preventing all from implementing it.
1. The numbers on the YAML deprecation post show that 43% of the unique users are unhappy with the decision.
