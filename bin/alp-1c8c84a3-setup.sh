#!/usr/bin/env bash

set -e

sudo conda upgrade \
  -n base \
  -q \
  -y \
  -c defaults \
  --override-channels \
  conda

sudo conda install \
  -n base \
  -q \
  -y \
  -c conda-forge \
  -c defaults \
  --override-channels \
  boa \
  conda-build \
  conda-verify
