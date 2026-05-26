#!/usr/bin/env bash
# scripts/build-android.sh — Build signed Android artifacts for ONTrack / FieldSnek.
#
# Usage:
#   bash scripts/build-android.sh                        # ONTrack AAB (default)
#   bash scripts/build-android.sh aab                    # ONTrack AAB (explicit)
#   bash scripts/build-android.sh aab fieldsnek          # FieldSnek AAB (for Play upload)
#   bash scripts/build-android.sh apk                    # ONTrack debug APK (sideloading)
#   bash scripts/build-android.sh apk fieldsnek          # FieldSnek debug APK (sideloading)
#   bash scripts/build-android.sh both                   # ONTrack AAB + APK
#   bash scripts/build-android.sh both fieldsnek        # FieldSnek AAB + APK
#   bash scripts/build-android.sh --help                 # this message
#
# Why two artifacts?
#   AAB = upload to Google Play; Play repackages it per-device.
#   APK = direct install file; share over Signal/email to testers who
#         can't or won't use a Google account.
#
# Why two apps in the same repo?
#   FieldSnek is the Play Store branding of the same ONTrack codebase.
#   It uses package_name `com.qompassai.fieldsnek` and a separate Play
#   Console listing, but shares all the Python sources.
#
# Requires on the host:
#   - Python 3.14 venv at ~/venv_p4a_develop with buildozer installed
#     (run scripts/setup-venv.sh if missing).
#   - Android SDK platform 36, NDK r29, JDK 17 (auto-fetched by buildozer
#     on first run).
#   - For *signed* AABs/APKs, the env vars used by your keystore wrapper.
#     The signing happens inside buildozer/p4a via gradle, controlled by
#     buildozer.spec's android.release_artifact + ~/.gradle/gradle.properties
#     or buildozer's android.* signing keys. See docs/ANDROID_BUILD.md.

set -euo pipefail

MODE="${1:-aab}"
APP="${2:-ontrack}"

case "$MODE" in
  -h|--help|help)
    sed -n '2,33p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  aab|apk|both) ;;
  *)
    echo "ERROR: unknown mode '$MODE'" >&2
    echo "Run 'bash scripts/build-android.sh --help' for usage." >&2
    exit 64
    ;;
esac

case "$APP" in
  ontrack)
    SPEC="buildozer.spec"
    BIN_DIR="/var/tmp/buildozer/ontrack/bin"
    ;;
  fieldsnek)
    SPEC="buildozer.fieldsnek.spec"
    BIN_DIR="/var/tmp/buildozer/fieldsnek/bin"
    ;;
  *)
    echo "ERROR: unknown app '$APP' (expected 'ontrack' or 'fieldsnek')" >&2
    exit 64
    ;;
esac

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f "$SPEC" ]; then
  echo "ERROR: spec file '$SPEC' not found in $ROOT_DIR" >&2
  exit 66
fi

# Activate the p4a develop venv if present and not already active.
VENV="${VIRTUAL_ENV:-}"
if [ -z "$VENV" ] && [ -f "$HOME/venv_p4a_develop/bin/activate" ]; then
  # shellcheck disable=SC1091
  . "$HOME/venv_p4a_develop/bin/activate"
fi

# Sanity: buildozer must be on PATH inside whichever venv we're in.
if ! command -v buildozer >/dev/null 2>&1; then
  echo "ERROR: 'buildozer' not on PATH. Run scripts/setup-venv.sh first." >&2
  exit 69
fi

echo "==> App        : $APP"
echo "==> Spec       : $SPEC"
echo "==> Mode       : $MODE"
echo "==> Bin dir    : $BIN_DIR"
echo "==> Buildozer  : $(command -v buildozer)"
echo "==> Python     : $(python --version 2>&1)"
echo

# Buildozer hardcodes the spec filename to ./buildozer.spec (no --spec flag
# exists in its argparse, despite what other docs claim). To support multiple
# specs in one repo, we temporarily swap buildozer.spec for the target spec,
# then restore the original on exit. The swap is symlink-based so the file
# contents on disk are never copied around.
SWAPPED=0
restore_spec() {
  if [ "$SWAPPED" = "1" ]; then
    rm -f buildozer.spec
    if [ -f buildozer.spec.bak ]; then
      mv buildozer.spec.bak buildozer.spec
    fi
    SWAPPED=0
  fi
}
trap restore_spec EXIT INT TERM

activate_spec() {
  if [ "$SPEC" = "buildozer.spec" ]; then
    return 0
  fi
  if [ -e buildozer.spec ] && [ ! -L buildozer.spec ]; then
    mv buildozer.spec buildozer.spec.bak
  elif [ -L buildozer.spec ]; then
    rm -f buildozer.spec
  fi
  ln -s "$SPEC" buildozer.spec
  SWAPPED=1
}

build_release_aab() {
  echo "==> [$APP] buildozer android release  (AAB)"
  activate_spec
  buildozer --verbose android release
}

build_debug_apk() {
  echo "==> [$APP] buildozer android debug  (APK, sideload)"
  # Buildozer's `debug` artifact is an APK, regardless of android.release_artifact.
  activate_spec
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
    cat <<EOF

Next steps (AAB → Play Store):

  # Validate auth + bundle, no upload
  bundle exec fastlane android validate

  # Upload to Internal testing (draft)
  bundle exec fastlane android internal

  # Or Closed testing
  bundle exec fastlane android closed

Note: bump 'version' in $SPEC before each upload — Play rejects a
versionCode <= the highest already uploaded.
EOF
    ;;
  apk)
    cat <<EOF

Next steps (APK → sideload):

  # Install directly via adb
  adb install -r "$BIN_DIR"/$APP-*-debug.apk

  # Or share the file over Signal / email to testers, who install via
  # "Install unknown apps" on their Android device. No Google account
  # required, no Play Console invite needed.
EOF
    ;;
  both)
    cat <<EOF

Next steps:

  AAB → Play Store : bundle exec fastlane android internal
  APK → sideload   : adb install -r "$BIN_DIR"/$APP-*-debug.apk
                     (or share the .apk over Signal/email)
EOF
    ;;
esac
