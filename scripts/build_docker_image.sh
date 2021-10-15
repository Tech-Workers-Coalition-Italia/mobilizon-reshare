#!/bin/sh
set -eu

guix time-machine -C channels-lock.scm -- system docker-image -L . -L ./patches docker-image.scm
