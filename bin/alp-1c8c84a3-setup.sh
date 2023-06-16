#!/usr/bin/env bash

set -e

sudo conda install \
  -n base \
  -q \
  -y \
  -c conda-forge \
  -c defaults \
  --override-channels \
  --update-all \
  conda=23.3.1 \
  boa \
  conda-build \
  conda-verify
