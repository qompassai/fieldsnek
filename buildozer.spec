# /qompassai/ONTrack/buildozer.spec
[app]

title = ONTrack
package.name = ontrack
package.domain = com.tds
version = 2.0.0

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ico,json,csv,ttf,md,toml
source.include_patterns = assets/*,config/*,core/*,mobile/*,main.py
source.exclude_dirs = .buildozer,.git,.github,.mypy_cache,__pycache__,bin,build,dist,tests,venv,.venv
source.exclude_patterns = *.pyc,*.pyo

presplash.filename = %(source.dir)s/assets/icon.jpg
presplash.color = #002855
presplash.keep_on_top = 1
icon.filename = %(source.dir)s/assets/icon.png

orientation = portrait
fullscreen = 0

requirements = python3,kivy==2.3.0,Pillow,plyer,python-dotenv,requests,geopy

android.api = 35
android.minapi = 26
android.ndk = 29
android.ndk_api = 26
android.sdk_path = /opt/android-sdk
android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = 0
android.copy_libs = 1
android.hide_statusbar = 0
android.manifest.application_name = ONTrack
android.category = PRODUCTIVITY
android.features = android.hardware.location,android.hardware.location.gps

android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION,ACCESS_BACKGROUND_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,RECORD_AUDIO

osx.python_version = 3
osx.kivy_version = 2.3.0

p4a.bootstrap = sdl2
p4a.branch = develop

entrypoint = main.py
languages = en

[buildozer]
log_level = 2
warn_on_root = 1
build_workers = 0
clean_build = 0
build_dir = /var/tmp/buildozer/ontrack/build
bin_dir = /var/tmp/buildozer/ontrack/bin
android.pip_args = --index-url https://pypi.org/simple/ --no-extra-index-url

[python-for-android]
