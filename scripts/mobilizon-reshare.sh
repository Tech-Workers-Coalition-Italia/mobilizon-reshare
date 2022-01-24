#!/usr/bin/env bash

set -e

export MOBILIZON_RESHARE_LOG_DIR="/tmp"
export MOBILIZON_RESHARE_LOCAL_STATE_DIR="/tmp"
export SECRETS_FOR_DYNACONF="$(pwd)/.secrets.toml"
export SETTINGS_FILE_FOR_DYNACONF="$(pwd)/mobilizon_reshare.toml"
export ENV_FOR_DYNACONF="production"

poetry run mobilizon-reshare "$@"
