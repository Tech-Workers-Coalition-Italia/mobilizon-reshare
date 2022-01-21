#!/bin/sh

set -e

poetry run pytest -m "not timezone_sensitive"
