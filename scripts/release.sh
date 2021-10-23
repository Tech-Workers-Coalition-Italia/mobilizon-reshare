#!/usr/bin/env bash

set -eu

myself="$(basename "$0")"
version_file="$(pwd)/mobilizon_reshare/VERSION"
pyproject_toml="$(pwd)/pyproject.toml"
docker_compose_yml="$(pwd)/docker-compose.yml"
current_branch="$(git rev-parse --abbrev-ref HEAD)"
current_commit="$(git log -1 --format='%H')"
dryrun=0
verbose=0
publish=0
bump="INVALID"

required_commands=("getopt" "pysemver" "git")
valid_types=('major' 'minor' 'patch' 'prerelease' 'build')

error() {
  echo -e "$@" >/dev/fd/2
}

crash() {
  [ "$#" -gt 0 ] && error "$1"
  exit 1
}

check-dependencies() {
  for com in "${required_commands[@]}"; do
    if ! command -v "$com" >/dev/null; then
      error "$com not found but it's required! Please install it with your favourite package manager."
      crash "\n\t\t\t\tOr just use Guix ;)\n"
    fi
  done
}

usage() {
  cat <<EOF
Usage: ${myself} -b <bump-type> [-hpbvd]
Release a new version of Mobilizon Reshare according to https://semver.org

-h,          --help                  Show this help message.

-b,          --bump                  Select a version bump type

-p,          --publish               Publish current release to PyPI.

-d,          --dryrun                Show operations, instead of carrying them out.

             --list-types            List all valid version bump types.

-v,          --verbose               Run script in verbose mode. Will print out each step of execution.
EOF
}

validate-bump-type() {
  if [[ ${valid_types[*]} =~ (^|[[:space:]])"$1"($|[[:space:]]) ]]; then
    true
  else
    crash "Invalid bump type: $1"
  fi
}

validate-pypi-token() {
  if [ -z ${PYPI_TOKEN+x} ]; then
    crash "The PYPI_TOKEN environment variable is required but unset. Please set it to upload the new release to PyPI."
  fi
}

current-version() {
  cat "${version_file}"
}

release-new-version() {
  current="$(current-version)"
  next="$(pysemver bump "$1" "$current")"
  echo -e "\nRELEASING VERSION: ${next}"

  [ "$verbose" = "1" ] && echo "Updating $version_file"
  [ "$dryrun" = "0" ] && printf "%s" "$next" >"$version_file"

  [ "$verbose" = "1" ] && echo "Updating $pyproject_toml"
  [ "$dryrun" = "0" ] && sed -i -E "s/version.*=.*\"${current}\"$/version = \"${next}\"/" "$pyproject_toml"

  [ "$verbose" = "1" ] && echo "Updating $docker_compose_yml"
  [ "$dryrun" = "0" ] && sed -i "s/${current}/${next}/" "$docker_compose_yml"

  [ "$verbose" = "1" ] && echo "Committing ${pyproject_toml}, ${docker_compose_yml} and ${version_file}"
  [ "$dryrun" = "0" ] && git add "$docker_compose_yml" "${pyproject_toml}" "${version_file}" && git commit -m "Release v${next}."

  [ "$verbose" = "1" ] && echo "Tagging Git HEAD with v${next}"
  [ "$dryrun" = "0" ] && git tag "v${next}"

  [ "$verbose" = "1" ] && echo "Building package..."
  [ "$dryrun" = "0" ] && poetry build

}

restore-git-state () {
  # This way we can go back to a
  # detached HEAD state as well.
  if [ "${current_branch}" = "HEAD" ]; then
    git checkout "${current_commit}"
  else
    git checkout "${current_branch}"
  fi
}

parse-args() {
  [ "$#" -eq 0 ] && crash "$(usage)"

  options=$(getopt -l "help,publish,bump:,list-types,verbose,dryrun" -o "hpb:vd" -- "$@")

  # set --:
  # If no arguments follow this option, then the positional parameters are unset. Otherwise, the positional parameters
  # are set to the arguments, even if some of them begin with a ‘-’.
  eval set -- "$options"

  while true; do
    case $1 in
    -h | --help)
      usage
      exit 0
      ;;
    --list-types)
      echo "${valid_types[@]}"
      exit 0
      ;;
    -v | --verbose)
      verbose=1
      set -vx
      ;;
    -d | --dryrun)
      dryrun=1
      verbose=1
      ;;
    -p | --publish)
      publish=1
      ;;
    -b | --bump)
      shift
      bump="$1"
      ;;
    --)
      shift
      break
      ;;
    esac
    shift
  done

  if [ "$bump" = "INVALID" ] && [ "$publish" = "0" ]; then
    error "You can either build a new release or publish the current release to PyPI."
    crash "See ${myself} -h for more information."
  fi
}

parse-args "$@"

if [ "$bump" != "INVALID" ]; then
    check-dependencies
    validate-bump-type "$bump"
    release-new-version "$bump"
fi

if [ "$publish" = "1" ]; then
  validate-pypi-token

  # We make sure to actually publish the tagged version
  git checkout "v$(current-version)"
  set +e
  # If this command fails we still want to go back to the
  # branch we were on.
  poetry publish -u "__token__" -p "$PYPI_TOKEN"
  set -e
  restore-git-state
fi

exit 0
