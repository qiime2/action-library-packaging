#!/usr/bin/env bash

set -e

# TODO: move this below the guard when done testing
PACKAGE_VERSION=$(conda search \
    -c $BUILD_DIR \
    $PACKAGE_NAME \
    --json | \
    jq '."$PACKAGE_NAME"[0].version')

# TODO: remove this debugging statement
echo $PACKAGE_VERSION

if [[ -z $LIBRARY_TOKEN ]] || [[ $GITHUB_EVENT_NAME == "pull_request" ]]
then
    echo "Skipping library upload due to missing Library token or incorrect github event type."
    exit 0
fi

# --fail-with-body is what we need, but that version of curl isn't on GH runners, yet
resp=$(curl \
  --silent \
  --include \
  --data "token=$LIBRARY_TOKEN" \
  --data "version=$PACKAGE_VERSION" \
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
    echo "ERROR: Something went wrong. Unable to upload to Library."
    echo $resp
    exit 1
fi

echo "Successfully notified Library of this build. q2-congratulations!"
