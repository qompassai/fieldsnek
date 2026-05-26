# OnTrack TODO


---

---


###  `flake.nix` — `CHANGELOG.md` referenced but does not exist

```nix
changelog = "https://github.com/qompassai/Python/blob/main/ontrack/CHANGELOG.md";
```

**TODO:** Create `ontrack/CHANGELOG.md` (even a stub), or remove the attribute.

---

### `config/settings.py` — `ORG_NAME` hardcoded to `"TDS Telecom"`

**TODO:** Load from environment to support multi-org deployments:
```python
ORG_NAME: str = os.getenv("ORG_NAME", "TDS Telecom")
```

Add `ORG_NAME=""` to `.env.example`.

---

### `core/matrix.py` — `_google_matrix` passes address strings, not lat/lng coords

The Google Distance Matrix API call uses raw address strings as `origins`/`destinations`.
The API re-geocodes them server-side, which may produce different canonical forms than
`geocoder.py` used. Using the already-geocoded coordinates is more reliable and avoids
a second geocoding round-trip.

**TODO:**
```python
origins = '|'.join(
    f"{locations[i+ri]['lat']},{locations[i+ri]['lng']}"
    for ri in range(min(batch, n - i))
)
```

---

###  `ontrack.spec` — `datas` list omits `gui/` and `mobile/`

PyInstaller's `Analysis` discovers Python packages via `pathex`, but any non-Python
data files (`.kv` Kivy layouts, templates, etc.) added later to `gui/` or `mobile/`
will be silently dropped from the frozen binary.

**TODO:**
```python
datas=[
    ("assets",  "assets"),
    ("config",  "config"),
    ("gui",     "gui"),
    ("mobile",  "mobile"),
],
```

---

###  `renovate.jsonc` — file comment points to wrong repo

```jsonc
// /qompassai/bunker/renovate.json5
```

**TODO:**
```jsonc
// /qompassai/Python/ontrack/renovate.jsonc
```

---

###  `tags` file committed to version control

A `tags` (ctags/etags) file is present at `ontrack/tags`. This is a local developer
tooling artifact.

**TODO:** Add to `.gitignore`:
```
tags
.tags
```

---

###  `scaffold_ontrack.py` — stale bootstrapper with outdated stub content

The scaffold script creates minimal stubs that are now superceded by the full
implementations. It should not be confused with production code.

**TODO:** Move to `tools/scaffold_ontrack.py` and add a prominent comment:
```python
# NOTE: This is a one-time project bootstrapper. All files it would create
# already exist with full implementations. Do not run this on an existing checkout.
```

---

### 32. `README.md` — likely stale, needs a full update

Verify `README.md` documents:
- Desktop install: `pip install -r requirements.txt && python main.py`
- Android build: `nix develop` → `bash build.sh`
- `.env` setup (copy `.env.example` → `.env`)
- `ONTRACK_WHISPER_MODEL` env var for model selection
- PipeWire echo-cancel setup: reference `pipewire/README.md` and `pipewire/51-ontrack-echo-cancel.conf`
- `python assets/convert.py` must be run before first build

---

###  `tests/` — no `__init__.py`

`tests/` has no `__init__.py`. While `pytest` discovers tests without it, absolute
imports inside tests (e.g. `from core.solver import ...`) require the repo root on
`sys.path`. This works with `pytest` run from the `ontrack/` directory but may fail
when run from the repo root or in certain CI configurations.

**TODO:** Add an empty `tests/__init__.py`, or add `pythonpath = ["."]` to
`pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

---


