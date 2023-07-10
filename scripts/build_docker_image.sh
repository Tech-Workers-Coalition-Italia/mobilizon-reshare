#!/bin/sh
set -eu

guix time-machine -C channels-lock.scm -- build -f guix.scm

guix time-machine -C channels-lock.scm -- pack -L . -f docker -S /opt/bin=bin --save-provenance --root=docker-image.tar.gz --entry-point=bin/scheduler.py mobilizon-reshare-scheduler python
