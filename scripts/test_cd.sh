#!/bin/sh
get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/"
}
set -eu
PROJECT_DIR="$(get_abs_filename $0)/.."
echo $PROJECT_DIR
echo "$(pwd)"
cd "$PROJECT_DIR/mobilizon_reshare/migrations/sqlite/"
echo $(pwd)

cd $PROJECT_DIR
echo $(pwd)

cd "$PROJECT_DIR/mobilizon_reshare/migrations/postgres/"
echo $(pwd)
