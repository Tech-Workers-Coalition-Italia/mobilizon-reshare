#!/usr/bin/env bash

set -eu

project_root="$(cd "$(dirname $(dirname "$0"))" && pwd)"

get_version () {
  cat "${project_root}/mobilizon_reshare/VERSION"
}

python -m pybadges \
    --left-text="python" \
    --right-text="3.10, 3.11" \
    --whole-link="https://www.python.org/" \
    --browser \
    --logo='https://dev.w3.org/SVG/tools/svgweb/samples/svg-files/python.svg' \
    --embed-logo=yes

python -m pybadges \
    --left-text="pypi" \
    --right-text="$(get_version)" \
    --whole-link="https://pypi.org/project/mobilizon-reshare/" \
    --browser

python -m pybadges \
    --left-text="LICENSE" \
    --right-text="Coopyleft" \
    --whole-link="https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/LICENSE" \
    --browser
