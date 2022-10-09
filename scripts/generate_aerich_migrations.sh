#!/bin/sh

set -eu


get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/"
}

PROJECT_DIR="$(get_abs_filename $0)/.."

cleanup() {
  # cleaning sqlite db
  echo "Removing /tmp/foo"
  rm  -rf /tmp/tmp.db

  # shutting down postgres container
  cd $PROJECT_DIR
  docker-compose -f docker-compose-migration.yml down
}

# making sure we leave the system clean
trap cleanup EXIT


poetry install

# I activate the env instead of using poetry run because the pyproject in the migration folder gives it problems
. "$(poetry env info -p)/bin/activate"

# I create a new SQLite db to run the migrations and generate a new one
echo "Generating SQLite migrations"
export DYNACONF_DB_URL="sqlite:///tmp/tmp.db"
cd "$PROJECT_DIR/mobilizon_reshare/migrations/sqlite/"

aerich upgrade
aerich migrate

# I use a dedicated docker-compose file to spin up a postgres instance, connect to it, run the migrations and generate a
# new one

echo "Generating postgres migrations"
export DYNACONF_DB_URL="postgres://mobilizon_reshare:mobilizon_reshare@localhost:5432/mobilizon_reshare"
cd $PROJECT_DIR

docker-compose -f docker-compose-migration.yml up -d

cd "$PROJECT_DIR/mobilizon_reshare/migrations/postgres/"
until [ "$(docker inspect mo-re_db_1 --format='{{json .State.Health.Status}}')" = "\"healthy\"" ];
do
  echo "Waiting for postgres"
  if [ "$(docker inspect mo-re_db_1 --format='{{json .State.Health.Status}}')" = "\"healthy\"" ]
  then
    break
  fi
  sleep 1s
done
aerich upgrade
aerich migrate
