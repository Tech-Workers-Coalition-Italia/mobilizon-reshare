#!/bin/sh
set -eu

if [ "$#" -ge 1 ] && [ "$1" = "-d" ]; then
    conf_path="docker/image-debug.scm"
else
    conf_path="docker/image.scm"
fi

guix time-machine -C channels-lock.scm -- build -L . -f guix.scm

guix time-machine -C channels-lock.scm -- system image -t docker -L . --root=docker-image.tar.gz "$conf_path"
