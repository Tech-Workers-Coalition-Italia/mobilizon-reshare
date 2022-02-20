[![CI](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/actions/workflows/main.yml)

The goal of `mobilizon_reshare` is to provide a suite to reshare Mobilizon events on a broad selection of platforms. This
tool enables an organization to automate their social media strategy in regards
to events and their promotion. 

# Platforms

`mobilizon-reshare` currently supports the following social platforms:

- Facebook
- Mastodon
- Twitter
- Telegram
- Zulip

# Usage

## Scheduling and temporal logic

The tool is designed to work in combination with a scheduler that executes it at
regular intervals. `mobilizon_reshare` allows fine-grained control over the logic to decide when
to publish an event, with the minimization of human effort as its first priority.

## Installation

`mobilizon_reshare` is distributed through [Pypi](https://pypi.org/project/mobilizon-reshare/) and [DockerHub](https://hub.docker.com/r/fishinthecalculator/mobilizon-reshare). Use

```shell
$ pip install mobilizon-reshare
```

to install the tool in your system or virtualenv.

This should install the command `mobilizon-reshare` in your system. Use it to access the CLI and discover the available
commands and their description.

### Guix package

If you run the Guix package manager you can install `mobilizon_reshare` from the root of the repository by running:

``` shell
$ guix install -L . mobilizon-reshare.git
```

To use the same dependencies used in CI env:

``` shell
$ guix time-machine -C channels-lock.scm -- install -L . mobilizon-reshare.git
```

## Run on your local system

Once you have installed `mobilizon_reshare` you can schedule the refresh from Mobilizon with your system's `cron`:

```bash
$ sudo crontab -l
*/15 * * * * mobilizon-reshare start
```

## Deploying through Docker Compose

To run `mobilizon_reshare` in a production environment you can use the image published to DockerHub. We also provide an example [`docker-compose.yml`](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/docker-compose.yml).

# Contributing

We welcome contributions from anybody. Currently our process is not structured but feel free to open or take issues through Github in case you want to help us. We have setup some instructions to setup a development environment [here](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/doc/contributing.md).
