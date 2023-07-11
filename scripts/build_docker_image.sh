#!/bin/sh
set -e

if [ "$1" = "--release" ] || [ "$1" = "-r" ]; then
  with_input="--with-input=mobilizon-reshare.git=mobilizon-reshare"
fi

guix time-machine -C channels-lock.scm -- build -L . ${with_input} mobilizon-reshare-scheduler

guix time-machine -C channels-lock.scm -- pack -L . ${with_input} -f docker -S /opt/bin=bin --save-provenance --root=docker-image.tar.gz --entry-point=bin/scheduler.py mobilizon-reshare-scheduler python
