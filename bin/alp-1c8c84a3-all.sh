#!/usr/bin/env bash

set -e

# lowercase variables are local to the script, uppercase variables are global

# update the following at release time
dev_cycle=2021.8
rel_cycle=2021.4

export BUILD_DIR="${GITHUB_WORKSPACE}/built-package"
# TODO: When composite actions are supported, replace vars below with
# Github env vars using input.var syntax
export RECIPE_PATH="$(env | sed -n 's/^INPUT_RECIPE-PATH=\(.*\)/\1/p')"
export PACKAGE_NAME="$(env | sed -n 's/^INPUT_PACKAGE-NAME=\(.*\)/\1/p')"
export BUILD_TARGET="$(env | sed -n 's/^INPUT_BUILD-TARGET=\(.*\)/\1/p')"
export ADDITIONAL_TESTS="$(env | sed -n 's/^INPUT_ADDITIONAL-TESTS=\(.*\)/\1/p')"
export LIBRARY_TOKEN="$(env | sed -n 's/^INPUT_LIBRARY-TOKEN=\(.*\)/\1/p')"

case "$RUNNER_OS" in
    macOS)
        export ARTIFACT_NAME="osx-64"
        export PLATFORM="osx"
        ;;

    Linux)
        export ARTIFACT_NAME="linux-64"
        export PLATFORM="linux"
        ;;

    *)
        echo "ERROR: Compatible operating system not found"
        exit 1
        ;;
esac

case "$BUILD_TARGET" in
    dev)
        export Q2_CHANNEL="https://packages.qiime2.org/qiime2/${dev_cycle}/tested"
        export CBC_URL="https://raw.githubusercontent.com/qiime2/package-integration/main/${dev_cycle}/tested/conda_build_config.yaml"
        ;;

    release)
        export Q2_CHANNEL="qiime2/label/r${rel_cycle}"
        export CBC_URL="https://raw.githubusercontent.com/qiime2/package-integration/main/${rel_cycle}/tested/conda_build_config.yaml"
        ;;

    *)
        echo "ERROR: invalid build target"
        exit 1
        ;;
esac


# Update when changing any subsequent bin/ scripts
# action steps
echo "::group::setup"
alp-1c8c84a3-setup.sh
echo "::endgroup::"

echo "::group::build"
alp-1c8c84a3-build.sh
echo "::endgroup::"

echo "::group::artifact-upload"
alp-1c8c84a3-artifact-upload.js
echo "::endgroup::"

echo "::group::library"
alp-1c8c84a3-library.sh
echo "::endgroup::"
