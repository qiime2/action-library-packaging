#!/usr/bin/env bash

set -e

echo "::group::build.sh"

sudo conda build \
    -c $Q2_CHANNEL \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --output-folder $BUILD_DIR \
    --no-anaconda-upload \
    $RECIPE_PATH

echo "::endgroup::"