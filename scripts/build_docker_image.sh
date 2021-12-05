#!/bin/sh
set -eu

guix time-machine -C channels-lock.scm -- build -L . -f guix.scm

guix time-machine -C channels-lock.scm -- system docker-image -L . --root=docker-image.tar.gz docker/image.scm
