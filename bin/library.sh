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

env | sort

# --fail-with-body is what we need, but that version of curl isn't on GH runners, yet
resp=$(curl \
  --silent \
  --include \
  --data "token=$LIBRARY_TOKEN" \
  --data "version=unknown" \
  --data "package_name=$PACKAGE_NAME" \
  --data "repository=$GITHUB_REPOSITORY" \
  --data "run_id=$GITHUB_RUN_ID" \
  --data "artifact_name=$ARTIFACT_NAME" \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --request POST https://library.qiime2.org/api/v1/packages/integrate/
)

code=$(echo $resp | grep HTTP | awk '{print $2}' )
if [[ $code -ne 200 ]]
then
    echo $resp
    exit 1
fi