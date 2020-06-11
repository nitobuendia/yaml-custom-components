# YAML Components - Home-Assistant
[ADR-010](https://github.com/home-assistant/architecture/blob/eeb2b93527ccf868745c11ff3e321e21b1bb90cd/adr/0010-integration-configuration.md) has officially deprecated YAML support for integrations which interacts with devices on Home-Assistant.

This component is a response to this decision by providing resources and solutions to [this polemic decision](https://community.home-assistant.io/t/the-future-of-yaml/186879) and it is open to anyone who wants to contribute to a temporary or long-term solution.

## Contents of this Repository

The component is divided in the following contents:

### Content: Articles and Argumentation

Folder: [content/](content/)

This folder contains arguments in favour of YAML Configuration support and in the search of a long-term solution for the Home-Assistant community. Some of these posts are meant to be published in the community, others in Home-Assistant repositories and others are for internal consumption.

* [The reasons behind YAML deprecation](content/the-reasons-behind.md) ([Published in the Community](https://community.home-assistant.io/t/the-future-of-yaml/186879/632)): Provides counterarguments to the reasons behind the YAML deprecation and why it is a negative result to do it.

* [Broken user flows](content/broken-user-flows.md) ([Published in the Community](https://community.home-assistant.io/t/the-future-of-yaml/186879/641)): Provides a comprehensive list of all the user flows and experiences that are broken due to the YAML deprecation. This is a compilation based on all the reasons mentioned on the post.

* How to fix YAML support (WIP): Provides suggestions and alternatives to YAML deprecation to provide a good path forward without most of the negative consequences given in ADR-0010.

* What to do after YAML deprecation (WIP): Provides a list of actions that both developers and users can take to fight against the deprecation, from very basic to very advanced.

### Experiments: Showcase of Solutions and Alternatives

Folder: [experiments/](experiments/) (WIP)

This folder contains experiments that aim at finding a solution to the YAML problem. This is not code that should be implemented on your Home-Assistant, but rather showcases of fixes that would allow Home-Assistant to provide YAML support with minimal cost.

### Custom Components: Core Components with YAML Support

Folder: [custom_components/](custom_components/)

This contains a folder of **official** [core components](https://github.com/home-assistant/core/tree/dev/homeassistant/components), which has been modified to add YAML support.

As a developer, you can foster and solve this problem for many users. As a user, you can keep your YAML configuration for core components even after the support has been removed.

## Contribute

Feel free to contribute by improving the article, creating or improving custom components or creating solutions / experiments to the YAML problem. You can also suggest your ideas and improvements on the `Issues` section.

If this work represents you, you can also support our voice on the Community, official GitHub repositories or on the Sponsor link above.
