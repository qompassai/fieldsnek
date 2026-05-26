#!/usr/bin/env bash
set -euo pipefail
unset GIT_OPTIONAL_LOCKS
unset GIT_DISCOVERY_ACROSS_FILESYSTEM

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export ANDROIDSDK="${ANDROID_SDK_ROOT}"
if [ -z "${ANDROIDNDK:-}" ]; then
    if [ -d "${ANDROID_SDK_ROOT}/ndk" ]; then
        ANDROIDNDK="$(find "${ANDROID_SDK_ROOT}/ndk" -maxdepth 1 -mindepth 1 -type d -name '29.*' | sort | tail -1)"
    fi
    : "${ANDROIDNDK:=${ANDROID_SDK_ROOT}/ndk/29.0.13599879}"
fi
export ANDROIDNDK
export ANDROIDAPI=36
export NDKAPI=26
export ANDROIDNDKVER=29

export PATH="${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools:${JAVA_HOME}/bin:/usr/bin:/bin"

PIP_CLEAN_ENV=(env -u PIP_EXTRA_INDEX_URL -u PIP_INDEX_URL -u PIP_FIND_LINKS)

BUILDOZER_BIN=""
for cand in \
    "${HOME}/venv_p4a_develop/bin/buildozer" \
    "${HOME}/.local/bin/buildozer" \
    "$(command -v buildozer 2>/dev/null || true)"; do
    if [ -n "${cand}" ] && [ -x "${cand}" ]; then
        BUILDOZER_BIN="${cand}"
        break
    fi
done
if [ -z "${BUILDOZER_BIN}" ]; then
    echo "[build.sh] buildozer not found." >&2
    echo "           Quick fix: run ./scripts/setup-venv.sh once (creates" >&2
    echo "           ~/venv_p4a_develop with the correct toolchain), then re-run" >&2
    echo "           ./build.sh release." >&2
    echo "           Manual setup: see docs/ANDROID_BUILD.md §1." >&2
    exit 127
fi

MODE="${1:-debug}"
shift || true

case "${MODE}" in
    clean)
        echo "[build.sh] cleaning .buildozer and bin/ ..."
        "${PIP_CLEAN_ENV[@]}" "${BUILDOZER_BIN}" android clean || true
        rm -rf .buildozer bin
        echo "[build.sh] clean complete. Re-run ./build.sh debug or ./build.sh release."
        exit 0
        ;;
    debug)
        TARGET="android debug"
        ;;
    release)
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
echo "[build.sh] BUILDOZER=${BUILDOZER_BIN}"
echo "[build.sh] target=${TARGET}"

"${PIP_CLEAN_ENV[@]}" "${BUILDOZER_BIN}" --verbose ${TARGET} "$@" 2>&1 | tee ~/buildozer_debug.log
