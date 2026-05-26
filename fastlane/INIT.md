# FieldSnek — One-time Play Console Bootstrap

`fastlane supply` (the `upload_to_play_store` action) **cannot create a new
app on Google Play.** The Play Developer Publishing API v3 only updates apps
that already exist. The first AAB must be uploaded manually through the
Play Console UI.

This is the cause of:

```
Google Api Error: Invalid request - Package not found: com.qompassai.fieldsnek.
```

See the [fastlane docs](https://docs.fastlane.tools/actions/upload_to_play_store/#quick-start)
("Before using *supply* to connect to Google Play Store, you'll need to set
up your app manually first by uploading at least one build to Google Play
Store.") and [fastlane/fastlane#14686](https://github.com/fastlane/fastlane/issues/14686).

## Run this once, then never again

### 1. Create the app on Play Console

1. Sign in to <https://play.google.com/console> as **phaedrusflow**.
2. **Create app** ▸ fill in:
   - **App name:** FieldSnek
   - **Default language:** English (United States)
   - **App or game:** App
   - **Free or paid:** Free
   - Accept both declarations and click **Create app**.
3. After the app is created, open **Dashboard ▸ Set up your app** and locate
   **App content** + **Store listing** (you can fill these in later; they
   are not required to register the package name).

> The package name `com.qompassai.fieldsnek` is bound to the app when the
> **first AAB is uploaded**, not at app creation. So you must do step 2
> below before fastlane works.

### 2. Upload the first AAB manually

Build the signed AAB on your workstation:

```bash
cd ~/.GH/Qompass/ONTrack
source ~/venv_p4a_develop/bin/activate
bash scripts/build-android.sh aab fieldsnek
ls /var/tmp/buildozer/fieldsnek/bin/fieldsnek-2.0.0-*-release.aab
```

Then in Play Console:

1. **Testing ▸ Internal testing** (left sidebar)
2. **Create new release**
3. **App bundles ▸ Upload** → drag in
   `fieldsnek-2.0.0-arm64-v8a_armeabi-v7a-release.aab`
4. Add a one-line release note ("Initial bootstrap upload.") and click
   **Next ▸ Save**. You do NOT need to roll out yet — saving a draft is
   enough to register the package name with the API.

The package name `com.qompassai.fieldsnek` is now bound to this app on the
API side. All future uploads can go through fastlane.

### 3. Wire up the service account (already done for ONTrack)

You're reusing the existing service account at
`~/.config/fastlane/google-play-ontrack.json`, which is already wired up
for the ONTrack listing. You need to **grant it permissions on FieldSnek
too** — Play Console treats permissions per-app:

1. Play Console ▸ **Users and permissions**
2. Find the service-account email (the `client_email` from
   `google-play-ontrack.json`) — it should already be in your team.
3. Click into the user → **App permissions** tab → **Add app** → select
   FieldSnek → grant **Release to testing tracks** (and Production if you
   plan to ship there).
4. Save changes.

Verify the JSON is still valid (this checks auth, not per-app permission):

```bash
bundle exec fastlane android check_auth
```

### 4. Now fastlane will work

```bash
cd ~/.GH/Qompass/ONTrack

# Dry-run — validates AAB + credentials without uploading. Run this first.
bundle exec fastlane android validate

# Real upload — Closed Testing (alpha track), draft release
bundle exec fastlane android closed

# Or Internal Testing (fastest, no review required)
bundle exec fastlane android internal
```

## Track-name reference

| Play Console UI    | Play API track name |
|--------------------|--------------------:|
| Production         | `production`        |
| Open testing       | `beta`              |
| Closed testing     | `alpha`             |
| Internal testing   | `internal`          |

If you create a **custom closed-testing track** in Console (e.g. "fieldsnek-private"),
its API name is the exact lowercased string you typed in Console. Pass it via:

```bash
FASTLANE_TRACK=fieldsnek-private bundle exec fastlane android closed
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Package not found: com.qompassai.fieldsnek` | App not created on Console or no AAB uploaded yet | Follow §1 + §2 above |
| `forbidden: The caller does not have permission` | Service account has no role on FieldSnek (had one on ONTrack) | §3 — add FieldSnek to its App permissions list |
| `Unable to find the requested track - 'closed'` | Used UI name instead of API name | Use `internal` / `alpha` / `beta` / `production` |
| `forbidden: APK has the wrong package name` | `package.name` × `package.domain` in `buildozer.fieldsnek.spec` doesn't concatenate to `com.qompassai.fieldsnek` | Check `package.name = fieldsnek` + `package.domain = com.qompassai` |
| `Google Api Error: applicationNotFound` | Service-account JSON belongs to a different Cloud project than the app | Recreate the JSON in the project linked to your Play developer account |
| `apksNotAllowed: This Edit cannot upload APKs because Android App Bundles have been added.` | Trying to upload an APK after an AAB was uploaded | Use `aab:` only, set `skip_upload_apk: true` (already done) |
| versionCode error on upload | Play rejects a versionCode ≤ the highest already uploaded | Bump `version = 2.0.1` in `buildozer.fieldsnek.spec` before next build |

## Env var quick reference (Fastfile understands)

| Var | Effect |
|---|---|
| `FIELDSNEK_AAB` | Override AAB path (skip the buildozer-glob lookup) |
| `FIELDSNEK_BIN_DIR` | Override buildozer bin_dir (default `/var/tmp/buildozer/fieldsnek/bin`) |
| `FIELDSNEK_SKIP_BUILD=1` | Reuse newest AAB on disk; skip buildozer if found |
| `FASTLANE_TRACK` | Override `closed` lane's track name (default `alpha`) |

## Why this matters

The first manual upload is a Play policy thing — Google wants a human to
acknowledge the package-name binding before granting API write access.
Once done, every subsequent build can ship through CI without touching
the Console.

## Relationship to ONTrack

FieldSnek and ONTrack ship from the same git repo. The Python source tree
is identical; only `package_name`, `title`, and the Play Console listing
differ. Switching between them is a `--spec` flag away:

```bash
buildozer -v --spec buildozer.spec             android release   # ONTrack
buildozer -v --spec buildozer.fieldsnek.spec   android release   # FieldSnek
# or just:
bash scripts/build-android.sh aab ontrack
bash scripts/build-android.sh aab fieldsnek
```

Each app has its own `bin_dir` and `build_dir` under `/var/tmp/buildozer/`,
so they don't clobber each other's incremental state.
