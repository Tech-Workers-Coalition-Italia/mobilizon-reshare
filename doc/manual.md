# Manual

## What is mobilizon-reshare?

`mobilizon_reshare` is a Python application to publish events from Mobilizon on a broad selection of platforms.
This tool enables an organization to automate their social media strategy in regards to events and their promotion. 

## Configuration

The configuration is implemented through Dynaconf. It allows a variety of ways to specify configuration keys. 
Refer to their [documentation](https://www.dynaconf.com/) to discover how configuration files and environment variables can be specified. 

We provide a sample configuration in the 
[settings.toml](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/mobilizon_reshare/settings.toml) file and
[.secrets.toml](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/mobilizon_reshare/.secrets.toml) file.

Use these files as the base for your custom configuration.

### Publishers and notifiers

The first step to deploy your custom configuration is to specify the source Mobilizon instance and group and then
activate the publishers and notifiers you're interested in. For each one of them, you have to specify credentials and
options in the .secrets.toml file. 

### Publishing strategy

The second important step is to define when and how your posts should be published. `mobilizon-reshare` takes over the 
responsibility of deciding *what* and *when* to publish, freeing the humans from the need to curate the social media
strategy around your events. This might mean very different things for different users and covering common use cases is
a goal of this project. To do so though, you need to guide the tool and understand in detail the options available to 
configure it in accordance to the requirements of your desired social media strategy.

The first element is the selection strategy. This is the way the tool will decide which event to pick and 
publish among all those available. At every execution of `mobilizon-reshare` will publish at most one event so you have
to consider how the selected strategy will interact with the external scheduling. The strategies assume that the
schedule will fire at regular intervals, unless specified otherwise. These intervals can vary but they should be small 
compared to the publishing window. Ideally a few minutes to a couple hours.

Currently only one strategy is supported: `next_event`. The semantic of the strategy is the following: pick the next
event in chronological order that hasn't been published yet and publish it only if at least 
`break_between_events_in_minutes` minutes have passed.

## Recap

In addition to the event publication feature, `mobilizon-reshare` allows you to do periodical recap of your events.
In the current version, the two features are handled separately and triggered by different CLI commands (respectively
`mobilizon-reshare start` and `mobilizon-reshare recap`).

The recap command, when executed, will retrieve the list of already published events and summarize in a single message 
to publish on all the active publishers. At the moment it doesn't support any decision logic and will always publish
when triggered.

## Core Concepts

### Publisher

A Publisher is responsible publishing an event or a message on a given platform. 

Currently the following publishers are supported:

- Facebook
- Mastodon
- Twitter
- Telegram
- Zulip

### Notifier

Notifiers are similar to Publishers and share most of the implementation. Their purpose is to
notify the maintainers when something unexpected happens. 

### Formatter

A formatter is responsible for the formatting and validation of an event or a message on a given platform.
Different platform require different templates and rules and therefore formatting is considered a platform-specific 
issue.

### Publication Strategy

A Publication Strategy is responsible for selecting the event to publish. Currently it's possible to publish only one 
event per run, under the assumption that the user will implement a social media strategy that doesn't require
concurrent publishing of multiple events on the same platform. Through proper scheduling and configuration is still
possible to achieve such behavior if required.

### Coordinator

A coordinator is responsible for publishing a message or an event across different platforms using different logics.
It uses publishers and formatters to compose and send the message and compile a report of how the publication went.
