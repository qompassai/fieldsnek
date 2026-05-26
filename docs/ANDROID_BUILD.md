# OnTrack — Android Build Runbook (Arch Linux)

This is the reference procedure for building the OnTrack Kivy app into a
Google Play–ready Android App Bundle (`.aab`) on an Arch Linux workstation.

It documents the exact toolchain pins that work as of May 2026. The previous
build failure (`Py_DEPRECATED(VERSION_UNUSED) __attribute__((__deprecated__))`
during `pythonforandroid.toolchain create`) was caused by:

1. A malformed multi-line `requirements =` in `buildozer.spec` that p4a was
   parsing as a single recipe name.
2. Desktop-only dependencies (`faster-whisper`, `ctranslate2`, `ortools`,
   `geopy`, `numpy`, `pandas`) that have no python-for-android recipe.
3. Android NDK 29, which breaks p4a's CPython recipe.

The fixes in this branch (`fix/android-build`) address all three.

---

## 1. Pre-flight on Arch Linux

```bash
# JDK 17 — newer JDKs break Gradle/AGP used by p4a.
sudo pacman -S --needed jdk17-openjdk

# Android command-line tools (AUR).
yay -S --needed android-sdk-cmdline-tools-latest

# Build dependencies for native extensions used by Kivy/p4a.
sudo pacman -S --needed base-devel git python python-pip \
    autoconf automake libtool pkgconf cmake ninja \
    zlib openssl libffi sqlite ccache unzip

# Buildozer — pin to a release that knows about NDK 25.
pip install --user --upgrade 'buildozer>=1.5.0' Cython==0.29.36

# Make sure ~/.local/bin is on PATH (add to ~/.zshrc/.bashrc if missing).
export PATH="$HOME/.local/bin:$PATH"
```

Set the env vars the build script expects (also add to your shell rc):

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export ANDROID_HOME=/opt/android-sdk
export ANDROID_SDK_ROOT=/opt/android-sdk
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$JAVA_HOME/bin:$PATH"
```

## 2. Install Android SDK + NDK 25b

```bash
# Accept all licenses first.
yes | sdkmanager --licenses

# Platform 34 + matching build-tools + NDK 25b (the only NDK p4a is happy with).
sdkmanager \
    "platform-tools" \
    "platforms;android-34" \
    "build-tools;34.0.0" \
    "ndk;25.1.8937393"
```

After this, `$ANDROID_SDK_ROOT/ndk/25.1.8937393` must exist. The build script
exports `ANDROIDNDK` to that exact path.

## 3. Clone and check out the fix branch

```bash
git clone git@github.com:qompassai/ONTrack.git
cd ONTrack
git checkout fix/android-build
```

## 4. Build

```bash
# Always start from a clean cache the first time after pulling toolchain changes.
./build.sh clean

# Debug APK (sideload-friendly).
./build.sh debug

# Release AAB for Play Console.
./build.sh release
```

Output lands in `./bin/`:

- `ontrack-1.0-arm64-v8a-debug.apk`
- `ontrack-1.0-arm64-v8a-release.aab`

A full debug log is tee'd to `~/buildozer_debug.log`.

## 5. Sign the release AAB

Play Console uses Play App Signing, so you only need an *upload* key. Generate
one once and keep it offline:

```bash
keytool -genkey -v \
    -keystore ~/.android/ontrack-upload.keystore \
    -alias ontrack-upload \
    -keyalg RSA -keysize 4096 -validity 10000
```

Tell buildozer about it before `./build.sh release` (or export in your shell):

```bash
export P4A_RELEASE_KEYSTORE=$HOME/.android/ontrack-upload.keystore
export P4A_RELEASE_KEYSTORE_PASSWD='<your-keystore-passwd>'
export P4A_RELEASE_KEYALIAS=ontrack-upload
export P4A_RELEASE_KEYALIAS_PASSWD='<your-key-passwd>'
```

## 6. Upload to Google Play Console

1. Sign in to <https://play.google.com/console> as **phaedrusflow**
   (account ID `7351560589446098345`).
2. Pick the OnTrack app (or create it: Internal app → Productivity → English (US)).
3. Left nav → **Release → Testing → Internal testing → Create new release**.
4. Upload `bin/ontrack-1.0-arm64-v8a-release.aab`.
5. Fill in release notes, **Save → Review release → Start rollout**.

The Computer agent can drive the upload step via a local Comet browser
session if Comet is already signed in as `phaedrusflow`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Py_DEPRECATED(VERSION_UNUSED) __attribute__((__deprecated__))` during `toolchain create` | NDK too new (>= 26) | Re-install NDK 25b: `sdkmanager "ndk;25.1.8937393"` |
| `Recipe with name '<long-string>' not found` | Multi-line `requirements =` in `buildozer.spec` | Keep `requirements =` on one comma-separated line |
| `Could not find ortools / faster-whisper / numpy` | Desktop-only dep in mobile requirements | Remove from `buildozer.spec`; guard import in code |
| `Gradle build failed: Unsupported class file major version 65` | Wrong JDK | `export JAVA_HOME=/usr/lib/jvm/java-17-openjdk` |
| `aidl is missing` | build-tools not installed | `sdkmanager "build-tools;34.0.0"` |
| Build cache wedged after upgrading p4a | Stale `.buildozer/` | `./build.sh clean` |

## Reference

- python-for-android recipes: <https://github.com/kivy/python-for-android/tree/develop/pythonforandroid/recipes>
- Buildozer docs: <https://buildozer.readthedocs.io/>
- Play Console signing: <https://support.google.com/googleplay/android-developer/answer/9842756>
