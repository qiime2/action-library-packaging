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

case "$RUNNER_OS" in
    macOS)
        echo "ARTIFACT_NAME=osx-64" >> $GITHUB_ENV
        ;;

    Linux)
        echo "ARTIFACT_NAME=linux-64" >> $GITHUB_ENV
        ;;

    *)
        exit 1
        ;;
esac
