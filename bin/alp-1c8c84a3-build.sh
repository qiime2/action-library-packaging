#!/usr/bin/env bash

set -e

sudo conda build \
    -c $Q2_CHANNEL \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --output-folder $BUILD_DIR \
    --no-anaconda-upload \
    $RECIPE_PATH

export PACKAGE_VERSION=$(conda search \
    -c $BUILD_DIR \
    $PACKAGE_NAME \
    --json | \
    jq '."$PACKAGE_NAME"[0].version')
