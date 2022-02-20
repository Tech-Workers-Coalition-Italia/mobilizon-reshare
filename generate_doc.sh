#!/bin/bash
export SECRETS_FOR_DYNACONF="mobilizon_reshare/.secrets.toml"

poetry run pdoc --force --html --output-dir api-documentation mobilizon_reshare
