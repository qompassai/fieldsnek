#!/usr/bin/env bash
# /qompassai/FieldSnek/installer/build_installer.sh
set -euo pipefail
cd "$(dirname "$0")"
echo "=== FieldSnek Installer Build ==="
if ! command -v uv &> /dev/null; then
    echo "uv not found — installing via astral.sh installer…"
    curl -fsSL https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
VENV="$(mktemp -d)/installer_build_venv"
uv venv "$VENV"
source "$VENV/bin/activate"

uv pip install --quiet --no-cache \
    customtkinter \
    Pillow \
    pyinstaller

echo "Building installer binary with PyInstaller…"
pyinstaller installer.spec --noconfirm --clean

echo ""
echo "=== Build complete ==="
ls -lh dist/FieldSnekInstaller* 2> /dev/null || true

deactivate
