# FieldSnek — TDS Telecom Field Route Optimizer

Route optimization tool for TDS field service technicians.
Enter addresses manually or load a CSV/Excel file, optimize the drive order,
preview each stop in Street View, and launch turn-by-turn navigation in
Google Maps or ArcGIS FieldMaps.

---

<details>
<summary>Features</summary>

| Feature | Desktop | Android |
|---|---|---|
| Manual address entry | ✓ | ✓ |
| CSV / Excel import | ✓ | – |
| Current location as start | ✓ (IP) | ✓ (GPS) |
| Drag-to-reorder stops | ✓ | ✓ (delete/add) |
| TSP route optimization | OR-Tools | Nearest-neighbor |
| Distance backend: OSRM | ✓ | ✓ |
| Distance backend: Google | ✓ (key) | ✓ (key) |
| Street View preview | ✓ (key) | ✓ (key) |
| Launch Google Maps | ✓ | ✓ |
| Launch ArcGIS FieldMaps | ✓ | ✓ |
| Launch Waze | ✓ | ✓ |
| Add/remove stops after solve | ✓ | ✓ |
| Re-optimize after edits | ✓ | ✓ |
| CSV export | ✓ | – |
| Voice address entry | ✓ | ✓ |

</details>

---

## Quick Start — Desktop

### 1. Environment setup

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys. All keys are optional — the app runs
without them using free fallbacks. See [API Keys](#api-keys) for details.

### 2. Prepare assets

Run this once before the first build to generate all required icon sizes:

```bash
python assets/convert.py
```

### 3. Install dependencies and run

```bash
pip install -r requirements.txt
python main.py
```

---

## Environment Variables

<details>
<summary>All supported variables</summary>

| Variable | Required | Default | Description |
|---|---|---|---|
| `GOOGLE_MAPS_API_KEY` | No | `""` | Street View, Google geocoding, Google distance matrix |
| `ARCGIS_ITEM_ID` | No | `""` | Deep-link target for ArcGIS FieldMaps |
| `OSRM_BASE_URL` | No | `http://router.project-osrm.org` | Override with a self-hosted OSRM instance for offline routing |
| `FIELDSNEK_WHISPER_MODEL` | No | `base` | Whisper model size for voice input: `tiny`, `base`, `small`, `medium`, `large` |

Set values in `.env` or export them in your shell. The app reads `.env`
automatically on startup; Android builds use system env vars only.

</details>

---

## Build — Linux Desktop

<details>
<summary>PyInstaller one-file binary</summary>

```bash
pip install pyinstaller
pyinstaller fieldsnek.spec
# Output: dist/FieldSnek
```

With the Nix dev shell (recommended on NixOS / Arch + Nix):

```bash
nix develop
pyinstaller fieldsnek.spec
```

</details>

---

## Build — Windows

<details>
<summary>One-file EXE via Wine cross-compile or native</summary>

**Native (on Windows):**

```powershell
pip install pyinstaller
pyinstaller fieldsnek.spec
# Output: dist\FieldSnek.exe
```

**Cross-compile from Linux using Nix + Wine:**

```bash
nix develop .#windows
wine C:\Python312\Scripts\pyinstaller.exe fieldsnek.spec
```

First-time Wine setup (run once inside the windows shell):

```bash
wine python-3.12.x-amd64.exe /quiet InstallAllUsers=0 TargetDir=C:\Python312
wine C:\Python312\python.exe -m pip install pyinstaller customtkinter Pillow
```

</details>

---

## Build — Android APK

<details>
<summary>Buildozer via Nix dev shell</summary>

**Prerequisites:** Android SDK and NDK installed at `/opt/android-sdk`.
See `buildozer.spec` for target API and architecture settings.

```bash
nix develop .#buildozer
bash build.sh
# or directly:
buildozer android debug
```

**Release / Play Store signing:**

```bash
buildozer android release
```

> OR-Tools has no python-for-android recipe. The Android build uses a
> pure-Python nearest-neighbor solver instead, which gives good-quality
> routes for typical field workloads (30 stops or fewer).

</details>

---

## Build — Rust Core (Maturin)

<details>
<summary>PyO3 extension module</summary>

The `src/lib.rs` Rust core is compiled into a Python extension module via
Maturin. This replaces the pure-Python `core/` modules as they are ported.

```bash
nix develop .#maturin
maturin develop          # development build — installs into active venv
maturin build            # release wheel
```

**Windows cross-compile from Linux:**

```bash
cargo build --target x86_64-pc-windows-gnu
```

Verify the extension loaded correctly:

```bash
python3 -c "import fieldsnek; print(fieldsnek.__doc__)"
```

</details>

---

## API Keys

<details>
<summary>Optional — app works without any keys</summary>

| Key | Used for | Obtain |
|---|---|---|
| `GOOGLE_MAPS_API_KEY` | Street View images, geocoding, distance matrix | [console.cloud.google.com](https://console.cloud.google.com/google/maps-apis/credentials) |
| `ARCGIS_ITEM_ID` | Deep-link target in ArcGIS FieldMaps | Your ArcGIS Online map item URL |

Keys can also be entered from the **Settings** screen inside the app and
are stored only in `.env` — never transmitted to TDS servers.

</details>

---

## Distance Backends

| Backend | Requires | Notes |
|---|---|---|
| `osrm` (default) | None | Free public router — real road distances |
| `google` | `GOOGLE_MAPS_API_KEY` | Live traffic-aware, highest quality |
| `haversine` | None | Straight-line distance, no API calls |

For offline or enterprise deployments, set `OSRM_BASE_URL` to a
self-hosted OSRM instance on TDS infrastructure.

---

## Address File Format

<details>
<summary>CSV and Excel column requirements</summary>

Files must contain a column named `address`. Additional columns are ignored.

```csv
address
123 Main St Spokane WA
456 Elm St Coeur d'Alene ID
789 Oak Ave Post Falls ID
```

Supported formats: `.csv`, `.xlsx`, `.xls`

</details>

---

## Voice Input

<details>
<summary>Whisper model configuration and PipeWire echo cancellation</summary>

Voice address entry uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
for local, offline transcription. No audio is sent to any server.

**Model selection** — set in `.env` or as a shell export:

```bash
FIELDSNEK_WHISPER_MODEL=base   # default — good balance of speed and accuracy
FIELDSNEK_WHISPER_MODEL=small  # better accuracy, slightly slower
FIELDSNEK_WHISPER_MODEL=tiny   # fastest, lowest memory
```

**PipeWire echo cancellation** (Linux desktop — recommended when using
a laptop mic near speakers):

```bash
# Install the config file
cp pipewire/51-fieldsnek-echo-cancel.conf \
   ~/.config/pipewire/pipewire.conf.d/

# Restart PipeWire
systemctl --user restart pipewire pipewire-pulse
```

See [`pipewire/README.md`](pipewire/README.md) for full details and
troubleshooting.

</details>

---

## Architecture

<details>
<summary>Project structure</summary>

```
FieldSnek/
├── main.py                 # Entry point — detects desktop vs Android
├── core/                   # Pure-Python core (being ported to Rust)
│   ├── parser.py           # CSV/Excel -> address list
│   ├── geocoder.py         # Address -> lat/lng (Nominatim or Google)
│   ├── matrix.py           # Distance matrix (OSRM / Google / Haversine)
│   ├── solver.py           # TSP optimizer (OR-Tools or nearest-neighbor)
│   ├── exporter.py         # CSV export, Maps URL, FieldMaps URL, Street View
│   └── voice.py            # Whisper-based voice transcription
├── src/
│   └── lib.rs              # Rust core (PyO3 extension module via Maturin)
├── gui/                    # Desktop UI (CustomTkinter)
│   ├── app.py
│   ├── components/
│   │   ├── address_table.py
│   │   ├── file_picker.py
│   │   └── voice_button.py
│   └── views/
│       ├── home.py
│       ├── results.py
│       └── settings.py
├── mobile/                 # Android UI (Kivy)
│   ├── app.py
│   └── screens/
│       ├── home.py
│       ├── results.py
│       ├── settings.py
│       └── voice.py
├── config/
│   └── settings.py         # Env var loader (Final constants + dotenv)
├── assets/                 # Icons and splash — run convert.py before first build
├── pipewire/               # PipeWire echo-cancel config for Linux desktop
├── tests/                  # pytest test suite
├── buildozer.spec          # Android build config
├── fieldsnek.spec            # PyInstaller desktop build config
├── Cargo.toml              # Rust build manifest
├── pyproject.toml          # Python build config (Maturin backend)
└── flake.nix               # Nix dev shells (linux / buildozer / windows / maturin)
```

</details>

---

## TDS Internal Notes

- No address data is transmitted to TDS servers. All routing uses OSRM
  (free, no account required) or the technician's own Google Maps API key.
- ArcGIS FieldMaps deep links open the configured web map and search for
  the stop address using the `ARCGIS_ITEM_ID` item identifier.
- For offline or restricted-network deployments, set `OSRM_BASE_URL` to a
  self-hosted OSRM instance on TDS infrastructure.
- Whisper transcription runs fully on-device — no audio leaves the machine.

---

## License

See [LICENSE.md](LICENSE.md).
