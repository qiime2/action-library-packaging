#!/usr/bin/env bash

# setup action variables
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

# upgrade base conda
sudo conda upgrade -n base -q -y -c defaults --override-channels conda

# install conda-build and friends
sudo conda install -n base -q -y -c defaults --override-channels conda-build conda-verify
