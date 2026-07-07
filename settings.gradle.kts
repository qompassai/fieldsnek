# #################################################################
# /qompassai/.GH/Qompass/ONTrack-rs/settings.gradel.kts
# Qompass AI Settings
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Qompass AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# #################################################################
plugins {
	id("org.gradle.toolchains.foojay-resolver-convention") version ("1.0.0")
}

if (!JavaVersion.current().isJava11Compatible) {
	throw GradleException("Jadx requires at least Java 11 for build (current version is '${JavaVersion.current()}')")
}

rootProject.name = "jadx"

include("jadx-core")
include("jadx-cli")
include("jadx-gui")

include("jadx-plugins-tools")

include("jadx-commons:jadx-app-commons")
include("jadx-commons:jadx-zip")
include("jadx-commons:jadx-analysis")

include("jadx-plugins:jadx-input-api")
include("jadx-plugins:jadx-dex-input")
include("jadx-plugins:jadx-java-input")
include("jadx-plugins:jadx-raung-input")
include("jadx-plugins:jadx-smali-input")
include("jadx-plugins:jadx-java-convert")
include("jadx-plugins:jadx-rename-mappings")
include("jadx-plugins:jadx-kotlin-metadata")
include("jadx-plugins:jadx-kotlin-source-debug-extension")
include("jadx-plugins:jadx-xapk-input")
include("jadx-plugins:jadx-aab-input")
include("jadx-plugins:jadx-apkm-input")
include("jadx-plugins:jadx-apks-input")
