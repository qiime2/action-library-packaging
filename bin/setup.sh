#!/usr/bin/env bash

# upgrade base conda
sudo conda upgrade -n base -q -y -c defaults --override-channels conda

# install conda-build and friends
sudo conda install -n base -q -y -c defaults --override-channels conda-build conda-verify

# run conda-build
sudo conda build \
    -c q2Channel \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --output-folder buildDir \
    --no-anaconda-upload \
    recipePath