#!/usr/bin/env bash

set -e

env | sort
less $GITHUB_ENV

echo "::group::setup.sh"

# update the following at release time
DEV_CYCLE=2021.8
REL_CYCLE=2021.4

# variable setup
# - run: echo "BUILD_DIR=${{ github.workspace }}/built-package" >> $GITHUB_ENV
#     shell: bash
# - run: echo "RUNNER_OS=${{ runner.os }}" >> $GITHUB_ENV
#     shell: bash
# - run: echo "RECIPE_PATH=${{ inputs.recipe-path }}" >> $GITHUB_ENV
#   shell: bash
# - run: echo "PACKAGE_NAME=${{ inputs.package-name }}" >> $GITHUB_ENV
#   shell: bash
# - run: echo "BUILD_TARGET=${{ inputs.build-target }}" >> $GITHUB_ENV
#   shell: bash
# - run: echo "ADDITIONAL_TESTS=${{ inputs.additional-tests }}" >> $GITHUB_ENV
#   shell: bash
# - run: echo "LIBRARY_TOKEN=${{ inputs.library-token }}" >> $GITHUB_ENV
#   shell: bash

case "$RUNNER_OS" in
    macOS)
        echo "ARTIFACT_NAME=osx-64" >> $GITHUB_ENV
        PLATFORM="osx"
        ;;

    Linux)
        echo "ARTIFACT_NAME=linux-64" >> $GITHUB_ENV
        PLATFORM="linux"
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
echo "Q2_CHANNEL=$Q2_CHANNEL" >> $GITHUB_ENV
echo "ENV_URL=$ENV_URL" >> $GITHUB_ENV

sudo conda upgrade -n base -q -y -c defaults --override-channels conda

sudo conda install -n base -q -y -c defaults --override-channels conda-build conda-verify

echo "::endgroup::"
