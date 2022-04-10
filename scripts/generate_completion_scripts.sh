#!/bin/sh

set -eu

export _MOBILIZON_RESHARE_COMPLETE=bash_source
scripts/mobilizon-reshare.sh > etc/bash_completion.d/mobilizon-reshare-completion.bash

export _MOBILIZON_RESHARE_COMPLETE=fish_source
scripts/mobilizon-reshare.sh > etc/fish/completions/mobilizon-reshare.fish

export _MOBILIZON_RESHARE_COMPLETE=zsh_source
scripts/mobilizon-reshare.sh > etc/zsh/mobilizon-reshare-completion.zsh
