#!/usr/bin/env bash

set -xev
# todo: uncomment when done developing
# set -e

# TODO: uncomment
# if [[ -z $LIBRARY_TOKEN || $GITHUB_EVENT_NAME -eq "pull_request" ]]
# then
#     # TODO: log msg
#     exit 0
# fi

curl \
  -d "token=$LIBRARY_TOKEN" \
  -d "version=unknown" \
  -d "package_name=$PACKAGE_NAME" \
  -d "repository=$GITHUB_REPOSITORY" \
  -d "run_id=$GITHUB_RUN_ID" \
  -d "artifact_name=$ARTIFACT_NAME" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -X POST https://library.qiime2.org/api/v1/packages/integrate/