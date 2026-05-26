# /qompassai/ONTrack/buildozer.fieldsnek.spec
# Qompass AI — FieldSnek Android build configuration
# Copyright (C) 2026 Qompass AI, All rights reserved.
# ----------------------------------------------------
# FieldSnek is the Play Store branding of the ONTrack codebase.
# Same source tree, different package_name and listing.
#
# Build via the helper (recommended):
#   bash scripts/build-android.sh aab fieldsnek    # AAB for Play
#   bash scripts/build-android.sh apk fieldsnek    # APK for sideload
#
# Buildozer has no --spec flag; it always reads ./buildozer.spec from cwd.
# The wrapper symlinks this file to buildozer.spec for the duration of the
# build, then restores the original. To bypass the wrapper manually:
#   mv buildozer.spec buildozer.spec.bak
#   ln -s buildozer.fieldsnek.spec buildozer.spec
#   buildozer --verbose android release
#   rm buildozer.spec && mv buildozer.spec.bak buildozer.spec
# ----------------------------------------------------
# Tested combinations (May 2026, Python 3.14 / Play Store target):
#   buildozer            == git+https://github.com/kivy/buildozer  (master)
#   python-for-android   == develop  (required for Python 3.14)
#   cython               == 0.29.34  (host) ; p4a builds Kivy with its own cython 0.29.36
#   Android SDK platform 36   build-tools 36.0.0
#   Android NDK 29            (r29)         <-- required by p4a develop
#   JDK 17 (jdk17-openjdk on Arch)
#   Python 3.14 on host (`python3.14 -m venv venv_p4a_develop`)
#
# Why Kivy is pinned to `master` (not 2.3.1):
#   Kivy 2.3.1 ships pre-generated Cython C that calls `_PyLong_AsByteArray`
#   with 5 args. Python 3.14 changed that signature to 6 args (added
#   `with_exceptions`), so the build dies with:
#       error: too few arguments to function call, expected 6, have 5
#   Kivy master regenerates Cython with cython>=3.1 (Python-3.14-aware).
#   See https://github.com/kivy/python-for-android/pull/3271 (closes #3274).
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
title                        = FieldSnek
package.name                 = fieldsnek
package.domain               = com.qompassai
version                      = 2.0.0
source.dir                   = .
source.include_exts          = csv,ico,jpeg,jpg,json,kv,png,py,txt
source.include_patterns      = assets/*,config/*,core/*,mobile/*
source.exclude_dirs          = .buildozer,.git,.github,.mypy_cache,.kivy,__pycache__,bin,build,dist,docs,gui,installer,pipewire,src,tests,tools,venv,.venv
source.exclude_patterns      = ontrack.spec,Cargo.toml,Cargo.lock,flake.nix,flake.lock,find_stubs.sh,tags,.coverage,renovate.jsonc,cliff.toml,gradle.properties

# Comma-separated, single line — buildozer / p4a parses this very strictly.
# Do NOT mix newlines and commas.
requirements                 = python3,kivy==master,android,plyer,pyjnius,requests,certifi,urllib3,chardet,idna,charset-normalizer,python-dotenv,pillow,openssl,sqlite3,libffi

orientation                  = portrait
fullscreen                   = 0
icon.filename                = %(source.dir)s/assets/icon.png
presplash.filename           = %(source.dir)s/assets/icon.jpg
presplash.color              = #002855
presplash.keep_on_top        = 1

# ── Android ────────────────────────────────────────────────────────────────
android.api                  = 36
android.minapi               = 26
android.ndk                  = 29
android.ndk_api              = 26
android.sdk                  = 36
android.archs                = arm64-v8a, armeabi-v7a
android.allow_backup         = 0
android.copy_libs            = 1
android.hide_statusbar       = 0
android.manifest.application_name = FieldSnek
android.category             = PRODUCTIVITY
# android.features was removed: p4a develop dropped the --feature CLI flag
# (kivy/python-for-android, build.py on develop has no add_argument for it).
# <uses-feature> nodes are now injected via the file below.
# android.features           = android.hardware.location,android.hardware.location.gps
android.extra_manifest_xml   = ./android_manifest_extras.xml
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
bin_dir                      = /var/tmp/buildozer/fieldsnek/bin
build_dir                    = /var/tmp/buildozer/fieldsnek/build
build_workers                = 0
clean_build                  = 0
log_level                    = 2
warn_on_root                 = 1
