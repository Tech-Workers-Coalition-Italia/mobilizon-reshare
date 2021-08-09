The goal of mobilizon_reshare is to provide a suite to reshare Mobilizon events on a broad selection of platforms. This
tool enables an organization to automate their social media strategy in regards
to events and their promotion. 


# Usage


## Scheduling and temporal logic

The tool is designed to work in combination with a scheduler that executes it at
regular intervals. mobilizon_reshare allows fine-grained control over the logic to decide when
to publish an event, with the minimization of human effort as its first priority.

## Configuration

The configuration is implemented through Dynaconf. It allows a variety of ways to specify configuration keys. 
Refer to their [documentation](https://www.dynaconf.com/) to discover how configuration files and environment variables can be specified. 

We provide a sample configuration in the [settings.toml](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/mobilizon_reshare/settings.toml) file.  

### Event selection

### Publishers

### Notifiers




# Contributing 

We welcome contributions from anybody. Currently our process is not structured yet but feel free to open or take issues through Github in case you want to help us.

## Core Concepts

### Publisher

A Publisher is responsible for formatting and publishing an event on a given platform. 

Currently the following publishers are supported:

* Telegram

### Notifier

Notifiers are similar to Publishers and share most of the implementation. Their purpose is to
notify the maintainers when something unexpected happens. 

### Publication Strategy

A Publication Strategy is responsible for selecting the event to publish. Currently it's possible to publish only one 
event per run, under the assumption that the user will implement a social media strategy that doesn't require
concurrent publishing of multiple events on the same platform. Through proper scheduling and configuration is still
possible to achieve such behavior if required.



## Develop

To run pre-commit hooks run `pre-commit install` after cloning the repository.

Make sure to have `pre-commit` installed in your active python environment. To install: `pip install pre-commit`. For more info: https://pre-commit.com/
