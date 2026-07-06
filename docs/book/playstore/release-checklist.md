<!-- #################################################################
<!-- /qompassai/.config/mdbook/playstore/release-checklist.md
<!-- Qompass AI Release Checklist
<!-- SPDX-License-Identifier: Apache-2.0
<!-- Copyright (c) 2026 Qompass AI
<!--
<!-- Licensed under the Apache License, Version 2.0 (the "License");
<!-- you may not use this file except in compliance with the License.
<!-- You may obtain a copy of the License at:
<!--   http://www.apache.org/licenses/LICENSE-2.0
<!--
<!-- Unless required by applicable law or agreed to in writing, software
<!-- distributed under the License is distributed on an "AS IS" BASIS,
<!-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
<!-- See the License for the specific language governing permissions and
<!-- limitations under the License.
<!-- #################################################################
-->

# Google Play Store Release Checklist

:::admonish info "Prepare your app build (Android)"
- Verify `versionCode` and `versionName` in your Gradle config:

```gradle
android {
    defaultConfig {
        applicationId "ai.qompass.ontrack"
        minSdk 24
        targetSdk 34

        versionCode 42
        versionName "2.0.0"
    }
}
```

- Build a _release_ App Bundle (`.aab`):

```bash
./gradlew bundleRelease
# Result: app/build/outputs/bundle/release/app-release.aab
```

- Sign the bundle (if you manage signing yourself):

```bash
jarsigner \
  -verbose \
  -sigalg SHA256withRSA \
  -digestalg SHA-256 \
  -keystore /path/to/your.keystore \
  app-release.aab \
  ontrack-release-key
```

- Verify the signature:

```bash
jarsigner -verify -verbose -certs app-release.aab
```
:::

:::admonish info "Screenshots and visuals"
- Launch your phone emulator and take screenshots:

```bash
# Start emulator (example)
emulator -avd Pixel_6_API_34 -netdelay none -netspeed full &

adb wait-for-device
adb shell monkey -p ai.qompass.ontrack -c android.intent.category.LAUNCHER 1

adb exec-out screencap -p > screenshots/android-phone/home.png
```

- Create tablet screenshots similarly (7"/10" AVDs):

```bash
emulator -avd Nexus_7_API_30 &
emulator -avd Pixel_C_API_30 &
```

- Prepare your app icon and feature graphic using an image tool, then export PNGs with the required dimensions.
:::

:::admonish info "Store listing content"
- Example structure for a `playstore/description.txt` file you can version-control:

```text
Short description:
Route optimization and field planning for fiber installs.

Full description:
ONTrack helps field technicians and planners optimize daily routes,
visualize fiber install jobs, and minimize drive time. Key features:
- Import job lists and addresses
- Automatic route optimization
- Map visualization with OSRM/Google Maps
- Offline-friendly workflows

Use ONTrack to keep your field operations efficient and transparent.
```

- Example categories / tags you might keep in `playstore/metadata.json`:

```json
{
  "category": "Productivity",
  "type": "App",
  "content_rating": "Everyone"
}
```
:::

:::admonish info "Policies, privacy, and data safety"
- Keep your Data Safety answers in a reusable JSON file:

```json
{
  "data_collected": [
    { "type": "Location", "purpose": "Routing", "shared": false },
    { "type": "Crash logs", "purpose": "Diagnostics", "shared": false }
  ],
  "data_not_collected": [
    "Contacts",
    "Payment info"
  ],
  "permissions": [
    { "name": "ACCESS_FINE_LOCATION", "reason": "Route optimization and map centering" }
  ]
}
```

- Declare permissions in `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

- Point your Play Console to your hosted privacy policy, and keep the Markdown source in your repo:

```markdown
<!-- docs/PRIVACY_POLICY.md -->
# ONTrack Privacy Policy

ONTrack collects location and crash data to provide routing and improve
stability. We do not sell or share personal data with third parties...
```
:::

:::admonish info "Testing and rollout"
- Create internal or closed testing tracks with versioned notes:

```text
Track: internal-test
Version: 2.0.0 (42)
Notes:
- New routing engine
- Updated OSRM base URL support
- Improved crash reporting
```

- Use `bundletool` locally to test your `.aab` on a device:

```bash
bundletool build-apks \
  --bundle=app-release.aab \
  --output=ontrack.apks \
  --mode=universal

bundletool install-apks \
  --apks=ontrack.apks
```

- Plan a staged rollout in a YAML/JSON config you can track:

```yaml
rollout:
  initial_percentage: 20
  monitor:
    crash_rate_threshold: 1.0
    anr_rate_threshold: 0.7
  next_steps:
    - if crash_rate < crash_rate_threshold: increase to 50%
    - if crash_rate >= crash_rate_threshold: pause and hotfix
```
:::

:::admonish info "Post-release monitoring"
- Script to quickly pull crash/ANR info (example for your own dashboard):

```bash
play_console_export.sh --app ai.qompass.ontrack --out reports/play_vitals.json
```

- Keep a simple changelog file for each release:

```markdown
<!-- docs/CHANGELOG_PLAY.md -->
## 2.0.0
- Initial public release on Google Play
- Added route optimization for fiber installs
- Integrated OSRM and optional Google Maps API
```
:::
