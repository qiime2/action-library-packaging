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
  mamba=1.4.2 \
  libmamba=1.4.2 \
  libmambapy=1.4.2 \
  boa \
  conda-build \
  conda-verify
