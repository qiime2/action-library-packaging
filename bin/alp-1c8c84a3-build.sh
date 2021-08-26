#!/usr/bin/env bash

set -e

cbc_fp="${RECIPE_PATH}/conda_build_config.yaml"
if [ -e "${cbc_fp}" ]
then
    echo "WARNING: overwriting existing ${cbc_fp}"
fi

wget -O "${cbc_fp}" "${CBC_URL}"

additional_tests_fp="${GITHUB_WORKSPACE}/additional_tests.yaml"
touch $additional_tests_fp
if [[ -z $ADDITIONAL_TESTS ]]
then
    echo "No additional tests specified"
else
    printf "test:\n  commands:\n    - ${ADDITIONAL_TESTS}\n" >> $additional_tests_fp
fi

sudo conda build \
    -c $Q2_CHANNEL \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --output-folder $BUILD_DIR \
    --no-anaconda-upload \
    --append-file $additional_tests_fp \
    $RECIPE_PATH
