#!/usr/bin/env bash
set -euo pipefail

pdoc \
    --output-dir docs/html \
    --docformat google \
    core config gui mobile main
