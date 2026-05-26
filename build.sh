#!/usr/bin/env bash
# shellcheck shell=bash
# /qompassai/ONTrack/build.sh
# Copyright (C) 2026 Qompass AI, All rights reserved
# ----------------------------------------
# OnTrack Android build driver.
#
# Usage:
#   ./build.sh                  # debug APK (default)
#   ./build.sh release          # release AAB for Play Store
#   ./build.sh clean            # nuke .buildozer cache and rebuild from scratch
#
# Expects an Arch Linux host with:
#   - jdk17-openjdk
#   - android-sdk-cmdline-tools-latest (AUR) + platform 34 + build-tools 34.0.0
#   - Android NDK 25b (25.1.8937393) — installed via sdkmanager (see docs/ANDROID_BUILD.md)
#   - buildozer >= 1.5.0 (pipx or pip --user)
# ----------------------------------------
set -euo pipefail
unset GIT_OPTIONAL_LOCKS
unset GIT_DISCOVERY_ACROSS_FILESYSTEM

# ── Toolchain pins ───────────────────────────────────────────────────────────
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export ANDROIDSDK="${ANDROID_SDK_ROOT}"
export ANDROIDNDK="${ANDROID_SDK_ROOT}/ndk/25.1.8937393"
export ANDROIDAPI=34
export NDKAPI=21          # min SDK — keep ≤ NDK platform floor
export ANDROIDNDKVER=25b

export PATH="${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools:${JAVA_HOME}/bin:/usr/bin:/bin"

# Strip any pip mirrors that leak from the user shell — they break p4a wheels.
PIP_CLEAN_ENV=(env -u PIP_EXTRA_INDEX_URL -u PIP_INDEX_URL -u PIP_FIND_LINKS)

# ── Subcommand dispatch ──────────────────────────────────────────────────────
MODE="${1:-debug}"
shift || true

case "${MODE}" in
    clean)
        echo "[build.sh] cleaning .buildozer and bin/ ..."
        "${PIP_CLEAN_ENV[@]}" ~/.local/bin/buildozer android clean || true
        rm -rf .buildozer bin
        echo "[build.sh] clean complete. Re-run ./build.sh debug or ./build.sh release."
        exit 0
        ;;
    debug)
        TARGET="android debug"
        ;;
    release)
        # AAB output for Play Console (configured via android.release_artifact = aab)
        TARGET="android release"
        ;;
    *)
        echo "[build.sh] unknown mode: ${MODE}" >&2
        echo "usage: $0 [debug|release|clean]" >&2
        exit 2
        ;;
esac

echo "[build.sh] JAVA_HOME=${JAVA_HOME}"
echo "[build.sh] ANDROID_HOME=${ANDROID_HOME}"
echo "[build.sh] ANDROIDNDK=${ANDROIDNDK}"
echo "[build.sh] target=${TARGET}"

# shellcheck disable=SC2086
"${PIP_CLEAN_ENV[@]}" ~/.local/bin/buildozer ${TARGET} "$@" 2>&1 | tee ~/buildozer_debug.log
