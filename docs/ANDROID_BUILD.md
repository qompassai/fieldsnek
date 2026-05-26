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

- `ontrack-2.0.0-arm64-v8a-debug.apk`
- `ontrack-2.0.0-arm64-v8a-release.aab`

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

## 6. Upload to Google Play Console (CLI)

Google Play has a first-class CLI workflow via the **Google Play Developer
API v3**. Two solid tools — pick one:

- **`fastlane supply`** (Ruby, batteries-included, recommended)
- **`gpapi` / raw `curl` to `androidpublisher.googleapis.com`** (no extra deps)

The one-time setup (service account + JSON key) is identical for both.

### 6a. One-time setup — service account + Play API access

1. Sign in to <https://play.google.com/console> as **phaedrusflow**
   (account ID `7351560589446098345`) **once** to create the app shell:
   - **All apps → Create app**
   - Name: `OnTrack`, language `en-US`, App, Free
   - Accept the two declarations → **Create app**
   - Note the package name `com.tds.ontrack.ontrack` (must match
     `package.domain` + `package.name` in `buildozer.spec`).

2. **Setup → API access** → **Choose a project to link** →
   *Create new Google Cloud project* (or link an existing one).

3. **Service accounts → Create new service account** → click the Google
   Cloud Console link → **Create service account**:
   - Name: `ontrack-publisher`
   - Skip role grants in Cloud Console (Play Console grants the role).
   - Open the new service account → **Keys → Add key → JSON** →
     download `ontrack-publisher.json` and store it at
     `~/.config/ontrack/play-service-account.json` (chmod 600).

4. Back in Play Console **API access**, click **Grant access** on the new
   service account:
   - App permissions: add **OnTrack**
   - Account permissions: **Release manager** (Admin not required for uploads)
   - **Invite user → Send invite** (auto-accepts for service accounts).

### 6b. Upload with `fastlane supply`

```bash
# One-time install (Arch).
sudo pacman -S --needed ruby
gem install --user-install fastlane -NV
export PATH="$(ruby -e 'puts Gem.user_dir')/bin:$PATH"

# One-time bootstrap inside the repo (creates fastlane/Appfile + metadata/).
cd ~/ONTrack
fastlane supply init \
    --package_name com.tds.ontrack.ontrack \
    --json_key ~/.config/ontrack/play-service-account.json

# Upload the AAB to the Internal Testing track.
fastlane supply \
    --package_name com.tds.ontrack.ontrack \
    --json_key ~/.config/ontrack/play-service-account.json \
    --aab bin/ontrack-2.0.0-arm64-v8a-release.aab \
    --track internal \
    --release_status draft \
    --skip_upload_metadata false \
    --skip_upload_images true \
    --skip_upload_screenshots true
```

Promote internal → closed/production later with:

```bash
fastlane supply \
    --package_name com.tds.ontrack.ontrack \
    --json_key ~/.config/ontrack/play-service-account.json \
    --track internal \
    --track_promote_to production \
    --rollout 0.1   # 10% staged rollout
```

### 6c. Upload with pure `curl` (no Ruby)

Useful if you want zero extra deps or to script from CI.

```bash
SA=~/.config/ontrack/play-service-account.json
PKG=com.tds.ontrack.ontrack
AAB=bin/ontrack-2.0.0-arm64-v8a-release.aab

# 1. Mint a short-lived access token from the service-account JWT.
TOKEN=$(python - <<'PY'
import json, time, base64, pathlib, urllib.request, urllib.parse
import jwt  # pip install --user pyjwt cryptography
sa = json.loads(pathlib.Path.home().joinpath(".config/ontrack/play-service-account.json").read_text())
now = int(time.time())
assertion = jwt.encode(
    {"iss": sa["client_email"], "scope": "https://www.googleapis.com/auth/androidpublisher",
     "aud": "https://oauth2.googleapis.com/token", "iat": now, "exp": now + 3600},
    sa["private_key"], algorithm="RS256")
body = urllib.parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion}).encode()
resp = json.loads(urllib.request.urlopen("https://oauth2.googleapis.com/token", body).read())
print(resp["access_token"])
PY
)

# 2. Open an edit.
EDIT_ID=$(curl -sX POST \
    -H "Authorization: Bearer $TOKEN" \
    "https://androidpublisher.googleapis.com/androidpublisher/v3/applications/${PKG}/edits" \
    | jq -r .id)

# 3. Upload the AAB.
VERSION_CODE=$(curl -sX POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @"$AAB" \
    "https://androidpublisher.googleapis.com/upload/androidpublisher/v3/applications/${PKG}/edits/${EDIT_ID}/bundles?uploadType=media" \
    | jq -r .versionCode)
echo "uploaded versionCode=$VERSION_CODE"

# 4. Assign it to the internal track as a draft release.
curl -sX PUT \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    --data @<(cat <<JSON
{
  "track": "internal",
  "releases": [{
    "name": "2.0.0-internal-${VERSION_CODE}",
    "versionCodes": ["${VERSION_CODE}"],
    "status": "draft",
    "releaseNotes": [{"language":"en-US","text":"Initial internal test build."}]
  }]
}
JSON
) "https://androidpublisher.googleapis.com/androidpublisher/v3/applications/${PKG}/edits/${EDIT_ID}/tracks/internal"

# 5. Commit the edit (this is what actually publishes the draft).
curl -sX POST \
    -H "Authorization: Bearer $TOKEN" \
    "https://androidpublisher.googleapis.com/androidpublisher/v3/applications/${PKG}/edits/${EDIT_ID}:commit"
```

Swap `"status": "draft"` for `"completed"` to start the rollout
immediately, or `"inProgress"` + `"userFraction": 0.1` for a staged rollout.

### 6d. Required Play Console app-content forms

Internal-testing uploads work before these are complete, but you cannot
promote to production until every item below is green under
**Policy → App content**:

- Privacy policy URL
- App access (login credentials for review, if any)
- Ads declaration
- Content rating questionnaire
- Target audience and content
- Data safety form
- News app declaration
- Government app declaration

Fastlane can manage Data Safety via
`metadata/android/en-US/data_safety.yaml` once you have it filled in once;
the other forms are Console-only.

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
