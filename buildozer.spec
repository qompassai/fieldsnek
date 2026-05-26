# /qompassai/ONTrack/buildozer.spec
# Qompass AI — ONTrack Android build configuration
# Copyright (C) 2026 Qompass AI, All rights reserved.
# ----------------------------------------------------
# Tested combinations (May 2026):
#   buildozer == 1.5.0
#   python-for-android (p4a) == develop
#   Android SDK platform 34   build-tools 34.0.0
#   Android NDK 25b           (25.1.8937393)   <-- newer NDKs break p4a's CPython recipe
#   JDK 17 (jdk17-openjdk on Arch)
#   Python 3.11 on host
#
# Build:    bash build.sh                     # debug APK -> bin/
# Release:  buildozer android release         # unsigned AAB -> bin/  (sign with apksigner)
#
# IMPORTANT — do NOT add faster-whisper / ctranslate2 / ortools / sounddevice /
# pandas / numpy / pyproj here. They either have no p4a recipe or pull in
# native libs that cannot be cross-compiled to Android (the failure manifests
# as the cryptic `Py_DEPRECATED(VERSION_UNUSED)` error). Voice-on-device is
# handled by the Rust port (qompassai/ONTrack-rs) instead.

[app]
title                        = ONTrack
package.name                 = ontrack
package.domain               = com.tds.ontrack
version                      = 2.0.0
source.dir                   = .
source.include_exts          = csv,ico,jpeg,jpg,json,kv,png,py,txt
source.include_patterns      = assets/*,config/*,core/*,mobile/*
source.exclude_dirs          = .buildozer,.git,.github,.mypy_cache,.kivy,__pycache__,bin,build,dist,docs,gui,installer,pipewire,src,tests,tools,venv,.venv
source.exclude_patterns      = ontrack.spec,Cargo.toml,Cargo.lock,flake.nix,flake.lock,find_stubs.sh,tags,.coverage,renovate.jsonc,cliff.toml,gradle.properties

# Comma-separated, single line — buildozer / p4a parses this very strictly.
# Do NOT mix newlines and commas.
requirements                 = python3,kivy==2.3.0,android,plyer,pyjnius,requests,certifi,urllib3,chardet,idna,charset-normalizer,python-dotenv,pillow,openssl,sqlite3,libffi

orientation                  = portrait
fullscreen                   = 0
icon.filename                = %(source.dir)s/assets/icon.png
presplash.filename           = %(source.dir)s/assets/icon.jpg
presplash.color              = #002855
presplash.keep_on_top        = 1

# ── Android ────────────────────────────────────────────────────────────────
android.api                  = 34
android.minapi               = 26
android.ndk                  = 25b
android.ndk_api              = 26
android.sdk                  = 34
android.archs                = arm64-v8a, armeabi-v7a
android.allow_backup         = 0
android.copy_libs            = 1
android.hide_statusbar       = 0
android.manifest.application_name = ONTrack
android.category             = PRODUCTIVITY
android.features             = android.hardware.location,android.hardware.location.gps
android.accept_sdk_license   = True

# AAB / Play target requirements:
# Google Play requires apps targeting API 34 or higher for new releases (Aug 2024+).
android.release_artifact     = aab

android.permissions          = INTERNET,ACCESS_NETWORK_STATE,ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION,RECORD_AUDIO,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

p4a.bootstrap                = sdl2
p4a.branch                   = develop

languages                    = en
entrypoint                   = main.py

[buildozer]
# Keep pip clean — TDS and many corporate networks have extra-index mirrors
# that confuse p4a's recipe resolver.
android.pip_args             = --index-url https://pypi.org/simple/ --no-extra-index-url
bin_dir                      = /var/tmp/buildozer/ontrack/bin
build_dir                    = /var/tmp/buildozer/ontrack/build
build_workers                = 0
clean_build                  = 0
log_level                    = 2
warn_on_root                 = 1
