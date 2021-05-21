#!/usr/bin/env bash

set -e

# Update when changing any subsequent bin/ scripts
# action steps
bash setup.sh
bash build.sh
node --unhandled-rejections=strict artifact-upload/script.js
bash testing.sh
bash library.sh