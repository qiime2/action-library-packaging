#!/usr/bin/env bash

set -e

# Update when changing any subsequent bin/ scripts
# action steps
bash bin/setup.sh
bash bin/build.sh
node --unhandled-rejections=strict artifact-upload/script.js
bash bin/testing.sh
bash bin/library.sh