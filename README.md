[![CI](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/actions/workflows/main.yml)

The goal of `mobilizon_reshare` is to provide a suite to reshare Mobilizon events on a broad selection of platforms. This
tool enables an organization to automate their social media strategy in regards
to events and their promotion. 


# Usage

## Installation

`mobilizon_reshare` is distributed through Pypi and DockerHub. Use 

```shell
$ sudo pip install mobilizon-reshare
```

to install the tool in your system or virtualenv.

This should install the command `mobilizon-reshare` in your system. Use it to access the CLI and discover the available
commands and their description.

We know that using `pip` to interact with your system interpreter is not the best practice in the world, but right now we don't
have the effort to maintain Linux distributions packages besides the [Guix package](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/docker/mobilizon-reshare.scm) that we need for production. 

## Run on your local system

Once you have installed `mobilizon_reshare` you can schedule the refresh from Mobilizon with your system's `cron`:

```bash
$ sudo crontab -l
*/15 * * * * mobilizon-reshare start
```

## Deploying through Docker Compose

To run `mobilizon_reshare` in a production environment you can use the image published to DockerHub. We also provide an example [`docker-compose.yml`](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/docker-compose.yml).
The image *runs with root privileges*, since they are required to run cron. Right now it 

# Contributing

We welcome contributions from anybody. Currently our process is not structured but feel free to open or take issues through Github in case you want to help us. We have setup some instructions to setup a development environment [here](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/doc/contributing.md).
