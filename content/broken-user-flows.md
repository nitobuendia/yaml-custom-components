# What workflows are broken when YAML is phased out for Integrations

In the post [The future of YAML](https://community.home-assistant.io/t/the-future-of-yaml/186879), Home-Assistant team explains the decision of [ADR0010](https://github.com/home-assistant/architecture/blob/master/adr/0010-integration-configuration.md) to drop YAML support for integrations.

One of the main points is to `Make things easy for users`. This is partially true as having a powerful UI makes it easy for many users. However, there are different users and use cases; and UI is better for some, but worse for others compared to YAML.

In [this article](https://github.com/nitobuendia/yaml-custom-components/blob/master/content/the-reasons-behind.md), we talked about some user flows that were broken; and here we can expand on them.

## Summary of Broken Workflows

The full list of reasons, whose use case and explanation is expanded below:

1. All current configurations will eventually break.
1. No easy bulk addition or support.
1. No partial versioning of components.
1. No flexible backups and restoring.
1. Reduced shareability for integrations and related entities.
1. Increased difficulty in troubleshooting.
1. Reduced documentation for users and developers.

## Breaking existing integrations

**With UI only**, the developers are effectively encouraged to remove YAML support, even from existing integrations. This will effectively break every single current Home-Assistant installation which uses this. In may cases, these are hundreds of integrations over long periods of time.

**With YAML configuration**, everything keeps working as today. You can still use YAML, or happily move over to UI; progressively at your own pace, or at once.

Users affected: (everyone, technically), [595](https://community.home-assistant.io/t/the-future-of-yaml/186879/595), [634](https://community.home-assistant.io/t/the-future-of-yaml/186879/634)

## Bulk Addition or Editing

There are changes that some changes may affect several entities. To name some of these:

1. A change of local IP subnet or IP ranges that affects all devices.
2. A revamp of your identity or name that may affect usernames.
3. A decision to name all your devices on a certain structure.
4. Hiding or showing all/most entities on Google Assistant.

**With UI only**, making bulk changes to many entities will be painful and time consuming. Having to go one by one, without having a good way to keep track the entities that were changed. Not only that, but if I want to change all the usernames where I used to have value "x", there is no effective way for me to search and find all the configurations affected.

**With YAML configuration**, making bulk changes can be done easily in a configuration file. Using editors or git also will allow to search, and compare changes. As such, it is easy to find the places where changes are required, edit them and keep track of progress as you do it.

Users affected: [27](https://community.home-assistant.io/t/the-future-of-yaml/186879/27), [44](https://community.home-assistant.io/t/the-future-of-yaml/186879/44), [58](https://community.home-assistant.io/t/the-future-of-yaml/186879/58), [114](https://community.home-assistant.io/t/the-future-of-yaml/186879/114), [220](https://community.home-assistant.io/t/the-future-of-yaml/186879/220), [450](https://community.home-assistant.io/t/the-future-of-yaml/186879/450)

## (Partial) Versioning

**With UI only**, it becomes harder to create versions of configurations. If I change the settings of one component to experiment, and I want to revert them one week later, there is no way for me to do it. The options are restoring a full back up, which may be reverting more changes; or reading the `.storage` files and manually trying to understand the undocumented configuration files. In other words, there is no easy way to import partial past configurations. Even for the elements that are still shareable (like automations or template sensors), they lose a lot of context when you are not aware of the integrations implemented (e.g. that binary sensor, what is it tracking?).

**With YAML configuration**, all the versions are kept in track if you use a software like Google Drive or GitHub, you can see the history of changes and you can easily import the state to any of those versions.

Users affected: [2](https://community.home-assistant.io/t/the-future-of-yaml/186879/2), [27](https://community.home-assistant.io/t/the-future-of-yaml/186879/27), [124](https://community.home-assistant.io/t/the-future-of-yaml/186879/124), [185](https://community.home-assistant.io/t/the-future-of-yaml/186879/185), [457](https://community.home-assistant.io/t/the-future-of-yaml/186879/457), [478](https://community.home-assistant.io/t/the-future-of-yaml/186879/478), [481](https://community.home-assistant.io/t/the-future-of-yaml/186879/481)

## Flexible Backups and Partial Restores

**With UI only**:
Backing up is supposed to be well covered by the current system. However, this is only under certain conditions.

* The snapshots that Home-Assistant takes are full copies (you can select which options, but you copy all those). When you restore, you are restoring a full version.

* The backups are heavy and it might not be ideal to keep the backups for months or weeks.

* Snapshots are not available in all systems (e.g. Docker installations).

* If the backups are on a system like a Raspberry Pi, you are at a risk of losing them if the SD card goes corrupt and starting from scratch.

* To solve all these, you require additional systems (e.g. move them to NAS) which are not part of the native system; and requires technical implementations much harder than using Git for your config files.

**With YAML configuration**:
With YAML you still have all the previous options; however, now you are empowered to do more.

Adding `configurations.yaml` plus a simple (and available to everyone) like GitHub, you can:

* Create and import different versions of components; in full or partial (see versioning above).

* Keep years of history and be able to check, revert and have detailed data to make back ups.

* Import your configuration to new and fresh systems without importing everything that comes with the backups.

Users affected: [72](https://community.home-assistant.io/t/the-future-of-yaml/186879/72), [185](https://community.home-assistant.io/t/the-future-of-yaml/186879/185), [193](https://community.home-assistant.io/t/the-future-of-yaml/186879/193), [272](https://community.home-assistant.io/t/the-future-of-yaml/186879/272), [335](https://community.home-assistant.io/t/the-future-of-yaml/186879/335), [363](https://community.home-assistant.io/t/the-future-of-yaml/186879/363), [367](https://community.home-assistant.io/t/the-future-of-yaml/186879/367), [481](https://community.home-assistant.io/t/the-future-of-yaml/186879/481)

## Shareability

A lot of us learnt and started using Home-Assistant by learning from the configurations of others. This is not only from automations, but also about the key integrations and how they are used.

**With UI only**, the *integrations* are no longer shareable as part of your configurations. The JSON files contain sensitive data (like tokens or passwords), which cannot be removed automatically using systems like `secrets`. As such, only manually edited and cherry picked files can be shared. As a result, the sharing ecosystem will progressively weaken.

**With YAML configuration**, one can share their configurations easily for others to learn and get inspired. Using secrets allow to make this secure without manual intervention.

Users affected: [2](https://community.home-assistant.io/t/the-future-of-yaml/186879/2), [9](https://community.home-assistant.io/t/the-future-of-yaml/186879/9), [135](https://community.home-assistant.io/t/the-future-of-yaml/186879/135), [181](https://community.home-assistant.io/t/the-future-of-yaml/186879/181), [185](https://community.home-assistant.io/t/the-future-of-yaml/186879/185), [187](https://community.home-assistant.io/t/the-future-of-yaml/186879/187), [193](https://community.home-assistant.io/t/the-future-of-yaml/186879/193), [449](https://community.home-assistant.io/t/the-future-of-yaml/186879/449)

## Effective testing and troubleshooting

### Moving across servers or Home-Assistant versions

It is possible for users to have several versions of Home-Assistant at points of time; be it because there are migrations between servers, or tests between development and production installs.

**With UI only**, there is no effective way to fully migrate between servers. Snapshots provide part of that functionality, but it has the problems described in the backup section (e.g. not being able to only move part of the installation, or installing in different versions of Home-Assistant). The alternative is to edit across multiple files of undocumented JSON (risking breaking the system as you are not meant to edit them), or having to start from scratch.

**With YAML configuration**, you can easily copy/paste all or parts of the configuration and install; allowing you to start fresh installations.

### Troubleshooting

In the past, when I reported bugs, I had to recreate and isolate the bugs ([example](https://github.com/home-assistant/core/issues/35499)). To do this easily, I usually copied the affected configurations from my main installation into a docker or dev environment.

In some cases, it was conflict between two or more components (some might be custom, but not always or all of them). For example, I recently had a conflict between a custom component (Hue Sync Box remote) and an official component (Harmony). To troubleshoot it, I moved the two components to a dev environment and I was able to identify and fix the issue.

In other cases, some components temporarily failed ([example nmap](https://github.com/home-assistant/core/issues/31763)) and I had to disable them. This is not a problem with the configuration, but with the component itself. The way to solve it was connecting via Samba, commenting out the configuration and restarting via SSH. All worked after.

**With UI configuration**, there is no way to isolate components temporarily or move them into a dev environment. There is also no easy way to share the relevant configuration for others to recreate the environment and be able to fix it. If the system is crashing due to a bug, there is no way to access the UI to disable or remove the component and JSON files do not allow an easy way to do it. There's not a good way to recover from this mode.

**With YAML configuration**, you have control over which components to copy and isolate. You can share the configuration for others to reproduce. You can also comment out components even without access to the UI, which allows you to test hypothesis, iterate and recover the system from failure.

Users affected: [128](https://community.home-assistant.io/t/the-future-of-yaml/186879/128), [183](https://community.home-assistant.io/t/the-future-of-yaml/186879/183), [255](https://community.home-assistant.io/t/the-future-of-yaml/186879/255), [481](https://community.home-assistant.io/t/the-future-of-yaml/186879/481), [561](https://community.home-assistant.io/t/the-future-of-yaml/186879/561), [568](https://community.home-assistant.io/t/the-future-of-yaml/186879/568)

## Documentation for developers, users and the curious

One of the greatest things about Home-Assistant is the really good documentation of components; with all their parameters that allows you to learn and experiment.

**With UI only**, all the data is opaque to the user *and developers*. One could argue that this is by design. However, it is limiting contributors who can learn, tweak and in the future contribute to the main components.

**With YAML configuration**: those who are willing to learn and contribute have plenty of documentation on the integrations page. Since YAML is an option, the configuration details need to be present.

Users affected: [68](https://community.home-assistant.io/t/the-future-of-yaml/186879/68), [89](https://community.home-assistant.io/t/the-future-of-yaml/186879/89), [332](https://community.home-assistant.io/t/the-future-of-yaml/186879/332), [419](https://community.home-assistant.io/t/the-future-of-yaml/186879/419), [454](https://community.home-assistant.io/t/the-future-of-yaml/186879/454), [594](https://community.home-assistant.io/t/the-future-of-yaml/186879/594), [625](https://community.home-assistant.io/t/the-future-of-yaml/186879/625)
