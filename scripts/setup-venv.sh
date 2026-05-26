#!/usr/bin/env bash
# /qompassai/ONTrack/scripts/setup-venv.sh
# Copyright (C) 2026 Qompass AI, All rights reserved
# -----------------------------------------------------------------------------
# One-shot bootstrap for the Python 3.14 venv that build.sh expects at
# ~/venv_p4a_develop.
#
# Idempotent: re-running is safe; existing venv is reused unless --recreate
# is passed.
#
# Run this once per machine, then ./build.sh release just works.
# -----------------------------------------------------------------------------
set -euo pipefail

VENV_DIR="${HOME}/venv_p4a_develop"
RECREATE=0
for arg in "$@"; do
    case "${arg}" in
        --recreate) RECREATE=1 ;;
        -h|--help)
            cat <<EOF
usage: $0 [--recreate]

Creates ${VENV_DIR} with Python 3.14 and installs:
  - buildozer (master from git)
  - cython 0.29.34
  - legacy-cgi, setuptools, wheel

Requires:
  - python3.14 on PATH (Arch: pacman -S python  if system python is 3.14,
    otherwise install python314 from AUR)
  - git
EOF
            exit 0
            ;;
    esac
done

# ── Sanity checks ────────────────────────────────────────────────────────────
if ! command -v python3.14 >/dev/null 2>&1; then
    echo "[setup-venv] python3.14 not on PATH." >&2
    echo "             Arch: install via 'pacman -S python' if system python" >&2
    echo "             is 3.14, otherwise 'paru -S python314' from AUR." >&2
    exit 127
fi
if ! command -v git >/dev/null 2>&1; then
    echo "[setup-venv] git not found. pacman -S git" >&2
    exit 127
fi

# ── (Re)create venv ──────────────────────────────────────────────────────────
if [ "${RECREATE}" = "1" ] && [ -d "${VENV_DIR}" ]; then
    echo "[setup-venv] --recreate: removing existing ${VENV_DIR}"
    rm -rf "${VENV_DIR}"
fi

if [ ! -d "${VENV_DIR}" ]; then
    echo "[setup-venv] creating venv at ${VENV_DIR} with $(python3.14 --version)"
    python3.14 -m venv "${VENV_DIR}"
else
    echo "[setup-venv] reusing existing venv at ${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# ── Strip pip mirrors that break p4a wheel resolution ────────────────────────
unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL PIP_FIND_LINKS

python -m pip install --upgrade pip setuptools wheel

# Pinned per docs/ANDROID_BUILD.md and Buildozer 1.6.x.dev0 requirements.
# Cython 0.29.34 is the last release whose generated C is compatible with
# both the legacy Kivy 2.3 sources AND Python 3.14's stricter C-API.
python -m pip install --upgrade \
    "cython==0.29.34" \
    "legacy-cgi" \
    "git+https://github.com/kivy/buildozer.git@master#egg=buildozer"

# ── Verify ───────────────────────────────────────────────────────────────────
echo
echo "[setup-venv] versions:"
python --version
python -m pip show buildozer | grep -E "^(Name|Version|Location):"
python -c "import Cython; print('Cython', Cython.__version__)"

cat <<EOF

[setup-venv] done. To use:

    source ${VENV_DIR}/bin/activate
    cd ~/.GH/Qompass/ONTrack
    ./build.sh release

Or just run ./build.sh release directly — build.sh auto-detects
${VENV_DIR}/bin/buildozer.
EOF
