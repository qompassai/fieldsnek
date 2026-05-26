[app]
title                        = FieldSnek
package.name                 = fieldsnek
package.domain               = com.qompassai
version                      = 2.0.0
source.dir                   = .
source.include_exts          = csv,ico,jpeg,jpg,json,kv,png,py,txt
source.include_patterns      = assets/*,config/*,core/*,mobile/*
source.exclude_dirs          = .buildozer,.git,.github,.mypy_cache,.kivy,__pycache__,bin,build,dist,docs,gui,installer,pipewire,src,tests,tools,venv,.venv
source.exclude_patterns      = fieldsnek.spec,Cargo.toml,Cargo.lock,flake.nix,flake.lock,find_stubs.sh,tags,.coverage,renovate.jsonc,cliff.toml,gradle.properties

requirements                 = python3,kivy==master,android,plyer,pyjnius,requests,certifi,urllib3,chardet,idna,charset-normalizer,python-dotenv,pillow,openssl,sqlite3,libffi

orientation                  = portrait
fullscreen                   = 0
icon.filename                = %(source.dir)s/assets/icon.png
presplash.filename           = %(source.dir)s/assets/icon.jpg
presplash.color              =
presplash.keep_on_top        = 1

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
android.extra_manifest_xml   = ./android_manifest_extras.xml
android.accept_sdk_license   = True

android.release_artifact     = aab

android.permissions          = INTERNET,ACCESS_NETWORK_STATE,ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION,RECORD_AUDIO,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

p4a.bootstrap                = sdl2
p4a.branch                   = develop

languages                    = en
entrypoint                   = main.py

[buildozer]
android.pip_args             = --index-url https://pypi.org/simple/ --no-extra-index-url
bin_dir                      = /var/tmp/buildozer/fieldsnek/bin
build_dir                    = /var/tmp/buildozer/fieldsnek/build
build_workers                = 0
clean_build                  = 0
log_level                    = 2
warn_on_root                 = 1
