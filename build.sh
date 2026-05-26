#!/usr/bin/env bash
# shellcheck shell=bash
# /qompassai/ONTrack/build.sh
# Copyright (C) 2026 Qompass AI, All rights reserved
# ----------------------------------------
set -euo pipefail
unset GIT_OPTIONAL_LOCKS
unset GIT_DISCOVERY_ACROSS_FILESYSTEM
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export PATH="/opt/android-sdk/cmdline-tools/latest/bin:/opt/android-sdk/platform-tools:$JAVA_HOME/bin:/usr/bin:/bin"
env -u PIP_EXTRA_INDEX_URL \
    -u PIP_INDEX_URL \
    -u PIP_FIND_LINKS \
    ~/.local/bin/buildozer android debug "$@" 2>&1 | tee ~/buildozer_debug.log
