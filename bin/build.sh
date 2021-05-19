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
    $INPUT_RECIPE_PATH

case "$RUNNER_OS" in
    macOS)
        ARTIFACT_NAME='osx-64'
        ;;

    Linux)
        ARTIFACT_NAME='linux-64'
        ;;

    *)
        exit 1
        ;;
esac

echo "ARTIFACT_NAME=$ARTIFACT_NAME" >> $GITHUB_ENV
