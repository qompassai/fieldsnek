#!/usr/bin/env bash
# scripts/build-android.sh — Build signed Android artifacts for FieldSnek.
#
# Usage:
#   bash scripts/build-android.sh            # AAB only (default — for Play upload)
#   bash scripts/build-android.sh aab        # AAB only (explicit)
#   bash scripts/build-android.sh apk        # debug APK (sideloading)
#   bash scripts/build-android.sh both       # AAB + APK in one go
#   bash scripts/build-android.sh --help     # this message
#
# Why two artifacts?
#   AAB = upload to Google Play; Play repackages it per-device.
#   APK = direct install file; share over Signal/email to testers who
#         can't or won't use a Google account.
#
# Requires on the host:
#   - Python 3.14 venv at ~/venv_p4a_develop with buildozer installed
#     (run scripts/setup-venv.sh if missing).
#   - Android SDK platform 36, NDK r29, JDK 17 (auto-fetched by buildozer
#     on first run).
#   - For *signed* AABs, signing config in ~/.gradle/gradle.properties or
#     buildozer.spec's android.* signing keys. See docs/ANDROID_BUILD.md.
#     (The debug APK is signed with the Android debug keystore automatically.)

set -euo pipefail

MODE="${1:-aab}"

case "$MODE" in
  -h|--help|help)
    sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  aab|apk|both) ;;
  *)
    echo "ERROR: unknown mode '$MODE'" >&2
    echo "Run 'bash scripts/build-android.sh --help' for usage." >&2
    exit 64
    ;;
esac

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f buildozer.spec ]; then
  echo "ERROR: buildozer.spec not found in $ROOT_DIR" >&2
  exit 66
fi

BIN_DIR="/var/tmp/buildozer/fieldsnek/bin"

# Activate the p4a develop venv if present and not already active.
if [ -z "${VIRTUAL_ENV:-}" ] && [ -f "$HOME/venv_p4a_develop/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$HOME/venv_p4a_develop/bin/activate"
fi

# Sanity: buildozer must be on PATH inside whichever venv we're in.
if ! command -v buildozer >/dev/null 2>&1; then
  echo "ERROR: 'buildozer' not on PATH. Run scripts/setup-venv.sh first." >&2
  exit 69
fi

echo "==> Mode       : $MODE"
echo "==> Bin dir    : $BIN_DIR"
echo "==> Buildozer  : $(command -v buildozer)"
echo "==> Python     : $(python --version 2>&1)"
echo

build_release_aab() {
  echo "==> buildozer android release  (AAB)"
  buildozer --verbose android release
}

build_debug_apk() {
  echo "==> buildozer android debug  (APK, sideload)"
  # Buildozer's `debug` artifact is an APK, regardless of android.release_artifact.
  buildozer --verbose android debug
}

case "$MODE" in
  aab)
    build_release_aab
    ;;
  apk)
    build_debug_apk
    ;;
  both)
    build_release_aab
    build_debug_apk
    ;;
esac

echo
echo "==> Build complete. Artifacts in $BIN_DIR/"
ls -lh "$BIN_DIR"/*.aab "$BIN_DIR"/*.apk 2>/dev/null || true

case "$MODE" in
  aab)
    cat <<'EOF'

Next steps (AAB → Play Store):

  # Validate auth + bundle, no upload
  bundle exec fastlane android validate

  # Upload to Internal testing (draft)
  bundle exec fastlane android internal

  # Or Closed testing
  bundle exec fastlane android closed

Note: bump 'version' in buildozer.spec before each upload — Play rejects a
versionCode <= the highest already uploaded.
EOF
    ;;
  apk)
    cat <<EOF

Next steps (APK → sideload):

  # Install directly via adb
  adb install -r "$BIN_DIR"/fieldsnek-*-debug.apk

  # Or share the file over Signal / email to testers, who install via
  # "Install unknown apps" on their Android device. No Google account
  # required, no Play Console invite needed.
EOF
    ;;
  both)
    cat <<EOF

Next steps:

  AAB → Play Store : bundle exec fastlane android internal
  APK → sideload   : adb install -r "$BIN_DIR"/fieldsnek-*-debug.apk
                     (or share the .apk over Signal/email)
EOF
    ;;
esac
