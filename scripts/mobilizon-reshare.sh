#!/usr/bin/env bash

export MOBILIZON_RESHARE_LOG_DIR="/tmp"
export MOBILIZON_RESHARE_LOCAL_STATE_DIR="/tmp"
export PYTHONPATH="$(pwd):${PYTHONPATH}"
export SECRETS_FOR_DYNACONF="$(pwd)/.secrets.toml"
export SETTINGS_FILE_FOR_DYNACONF="$(pwd)/mobilizon_reshare.toml"
export ENV_FOR_DYNACONF="production"

python "$(pwd)/mobilizon_reshare/cli/cli.py" "$@"
