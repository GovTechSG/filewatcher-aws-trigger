#!/usr/bin/env sh
set -e

find . -type f -not -path '*/\.*' -name '*.py' -exec \
    bash -c "echo {} && pylint -vvv {}" \;
