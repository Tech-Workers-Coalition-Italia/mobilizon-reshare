#!/bin/sh

set -eux

python -m pip install --upgrade pip
pip install poetry
poetry install
