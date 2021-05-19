#!/usr/bin/env bash

set -xev
# TODO: uncomment when done developing
# set -e

compgen -A variable

echo "BUILD_DIR=$BUILD_DIR" >> $GITHUB_ENV
echo "RUNNER_OS=$RUNNER_OS" >> $GITHUB_ENV
echo "RECIPE_PATH=$RECIPE_PATH" >> $GITHUB_ENV
echo "PACKAGE_NAME=$PACKAGE_NAME" >> $GITHUB_ENV
echo "BUILD_TARGET=$BUILD_TARGET" >> $GITHUB_ENV
echo "ADDITIONAL_TESTS=$ADDITIONAL_TESTS" >> $GITHUB_ENV
echo "LIBRARY_TOKEN=$LIBRARY_TOKEN" >> $GITHUB_ENV

# update the following at release time
case "$BUILD_TARGET" in
    tested)
        Q2_CHANNEL='https://packages.qiime2.org/qiime2/2021.8/tested'
        ;;

    staged)
        Q2_CHANNEL='https://packages.qiime2.org/qiime2/2021.8/staged'
        ;;

    released)
        Q2_CHANNEL='qiime2/label/2021.4'
        ;;

    *)
        Q2_CHANNEL='qiime2/label/2021.4'
        ;;
esac
echo "Q2_CHANNEL=$Q2_CHANNEL" >> $GITHUB_ENV

sudo conda upgrade -n base -q -y -c defaults --override-channels conda

sudo conda install -n base -q -y -c defaults --override-channels conda-build conda-verify
