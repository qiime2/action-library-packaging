#!/usr/bin/env bash

set -e

# debugging
echo "github event type: $GITHUB_EVENT_NAME"
if [[ -n $LIBRARY_TOKEN ]]
then
  echo "library token is present"
fi
if [[ -z $LIBRARY_TOKEN ]]
then
  echo "library token is not present"
fi
if [[ $GITHUB_EVENT_NAME -eq "pull_request" ]]
then
  echo "int comparision: this is the incorrect event type for this script"
fi
if [[ $GITHUB_EVENT_NAME == "pull_request" ]]
then
  echo "string comparision: this is the incorrect event type for this script"
fi

if [[ -z $LIBRARY_TOKEN ]] || [[ $GITHUB_EVENT_NAME == "pull_request" ]]
then
    echo "Skipping library upload due to missing library token or incorrect github event type"
    exit 0
fi

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
    echo "ERROR: Something went wrong. Unable to upload to library."
    echo $resp
    exit 1
fi
