#!/usr/bin/env bash
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

if [ -z "${VIRTUAL_ENV:-}" ] && [ -f "$HOME/venv_p4a_develop/bin/activate" ]; then
  . "$HOME/venv_p4a_develop/bin/activate"
fi

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

  bundle exec fastlane android validate

  bundle exec fastlane android internal

  bundle exec fastlane android closed

Note: bump 'version' in buildozer.spec before each upload — Play rejects a
versionCode <= the highest already uploaded.
EOF
    ;;
  apk)
    cat <<EOF

Next steps (APK → sideload):

  adb install -r "$BIN_DIR"/fieldsnek-*-debug.apk

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
