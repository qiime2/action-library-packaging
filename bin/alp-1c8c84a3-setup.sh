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
  conda \
  boa \
  conda-build \
  conda-verify
