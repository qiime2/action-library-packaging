#!/usr/bin/env bash

set -e

env | sort
less $GITHUB_ENV

# update the following at release time
DEV_CYCLE=2021.8
REL_CYCLE=2021.4

# TODO: When composite actions are supported, replace vars below with
# Github env vars using github.workspace and runner.os syntax
export BUILD_DIR=${GITHUB_WORKSPACE}/built-package
# TODO: When composite actions are supported, replace vars below with
# Github env vars using input.var syntax
export RECIPE_PATH="$(env | sed -n 's/^INPUT_RECIPE-PATH=\(.*\)/\1/p')"
export PACKAGE_NAME="${INPUT_PACKAGE-NAME}"
export BUILD_TARGET="${INPUT_BUILD-TARGET}"
export ADDITIONAL_TESTS="${INPUT_ADDITIONAL-TESTS}"
export LIBRARY_TOKEN="${INPUT_LIBRARY-TOKEN}"

case "$RUNNER_OS" in
    macOS)
        export ARTIFACT_NAME=osx-64
        export PLATFORM="osx"
        ;;

    Linux)
        export ARTIFACT_NAME=linux-64
        export PLATFORM="linux"
        ;;

    *)
        # TODO: log error msg
        exit 1
        ;;
esac

case "$BUILD_TARGET" in
    tested)
        Q2_CHANNEL="https://packages.qiime2.org/qiime2/${DEV_CYCLE}/tested"
        ENV_URL="https://raw.githubusercontent.com/qiime2/environment-files/master/${DEV_CYCLE}/test/qiime2-${DEV_CYCLE}-py38-${PLATFORM}-conda.yml"
        ;;

    staged)
        Q2_CHANNEL="https://packages.qiime2.org/qiime2/${DEV_CYCLE}/staged"
        ENV_URL="https://raw.githubusercontent.com/qiime2/environment-files/master/${DEV_CYCLE}/staging/qiime2-${DEV_CYCLE}-py38-${PLATFORM}-conda.yml"
        ;;

    released)
        Q2_CHANNEL="qiime2/label/r${REL_CYCLE}"
        ENV_URL="https://raw.githubusercontent.com/qiime2/environment-files/master/${REL_CYCLE}/release/qiime2-${REL_CYCLE}-py38-${PLATFORM}-conda.yml"
        ;;

    *)
        Q2_CHANNEL="qiime2/label/r${REL_CYCLE}"
        ENV_URL="https://raw.githubusercontent.com/qiime2/environment-files/master/${REL_CYCLE}/release/qiime2-${REL_CYCLE}-py38-${PLATFORM}-conda.yml"
        ;;
esac
export Q2_CHANNEL=${Q2_CHANNEL}
export ENV_URL=${ENV_URL}

# Update when changing any subsequent bin/ scripts
# action steps
bash bin/setup.sh
bash bin/build.sh
node --unhandled-rejections=strict artifact-upload/script.js
bash bin/testing.sh
bash bin/library.sh