#!/usr/bin/env bash

set -xev
# TODO: uncomment when done developing
# set -e

# update the following at release time
case "$INPUT_BUILD_TARGET" in
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
echo "BUILD_DIR=$BUILD_DIR" >> $GITHUB_ENV
echo "RUNNER_OS=$RUNNER_OS" >> $GITHUB_ENV

sudo conda upgrade -n base -q -y -c defaults --override-channels conda

sudo conda install -n base -q -y -c defaults --override-channels conda-build conda-verify
