#!/usr/bin/env bash

set -e

if [[ -z $ADDITIONAL_TESTS ]]
then
    echo "Skipping, no additional tests specified"
    exit 0
fi

wget -O env.yml $ENV_URL

sudo conda env create -q -p ./testing --file env.yml

PACKAGE_LENGTH=$(sudo conda list -p ./testing "^${PACKAGE_NAME}$" --json | jq length)

if [[ $PACKAGE_LENGTH -eq 0 ]]
then
sudo conda install \
    -p ./testing \
    -q -y \
    -c $BUILD_DIR \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --strict-channel-priority \
    $PACKAGE_NAME
elif [[ $PACKAGE_LENGTH -eq 1 ]]
then
sudo conda update \
    -p ./testing \
    -q -y \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --strict-channel-priority \
    --update-deps \
    $PACKAGE_NAME

sudo conda update \
    -p ./testing \
    -q -y \
    -c $BUILD_DIR \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --strict-channel-priority \
    --force-reinstall \
    $PACKAGE_NAME
else
    echo "ERROR: Something went wrong. Testing unsuccessful."
    exit 1
fi

sudo conda install \
    -p ./testing \
    -q -y \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --strict-channel-priority \
    pytest

source "$CONDA/etc/profile.d/conda.sh"
conda activate ./testing
eval $ADDITIONAL_TESTS
