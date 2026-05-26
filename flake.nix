{
  description = "FieldSnek — Route Optimization app (Linux · Android · Windows)";
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = {
    flake-utils,
    nixpkgs,
    rust-overlay,
    ...
  }:
    flake-utils.lib.eachSystem ["x86_64-linux"] (system: let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        overlays = [rust-overlay.overlays.default];
      };
      rustToolchain = pkgs.rust-bin.stable.latest.default.override {
        extensions = [
          "clippy"
          "rust-analyzer"
          "rust-src"
        ];
        targets = [
          "x86_64-pc-windows-gnu"
        ];
      };
      androidSdkRoot = "/opt/android-sdk";
      androidNdkRoot = "/opt/android-sdk/ndk/29.0.14206865";
      buildozerBase = "/var/tmp/buildozer/fieldsnek";
      meta = with pkgs.lib; {
        broken = false;
        changelog = "https://github.com/qompassai/fieldsnek/blob/main/CHANGELOG.md";
        description = "FieldSnek productivity app for field service technicians";
        downloadPage = "https://github.com/qompassai/fieldsnek/releases";
        homepage = "https://github.com/qompassai/fieldsnek/tree/main";
        hydraPlatforms = [];
        license = licenses.unfree;
        longDescription = ''
          FieldSnek is a desktop (Linux + Windows) and Android application for
          TDS field technicians. It provides location-aware job tracking,
          offline-capable workflows, and streamlined field reporting.
          Desktop builds use PyInstaller; Android builds use Buildozer /
          python-for-android targeting armeabi-v7a and arm64-v8a.
          Rust core modules are built with Maturin and exposed via PyO3.
        '';
        maintainers = [
          "Qompass AI"
        ];
        platforms = [
          "x86_64-linux"
        ];
        sourceProvenance = with sourceTypes; [
          binaryBytecode
          binaryNativeCode
          fromSource
        ];
      };
      commonPythonInputs = with pkgs; [
        python312
        python312Packages.cython
        uv
      ];
      commonNativeInputs = with pkgs; [
        curl
        git
        libffi
        openssl
        sqlite
        zlib
      ];
      mingwCC = pkgs.pkgsCross.mingwW64.stdenv.cc;
    in {
      devShells.default = pkgs.mkShell {
        name = "fieldsnek-linux";
        inherit meta;
        buildInputs =
          commonPythonInputs
          ++ commonNativeInputs
          ++ (with pkgs; [
            tcl
            tk
            upx
          ]);
        shellHook = ''
          echo "FieldSnek Linux desktop env"
          echo "  Python  : $(python3 --version)"
          echo "  uv      : $(uv --version)"
          if [ ! -d .venv ]; then
            echo "  Creating Linux venv with uv..."
            uv venv .venv
            uv pip install --quiet --no-cache \
              customtkinter \
              Pillow \
              pyinstaller
          fi
          source .venv/bin/activate
          echo "  PyInstaller: $(pyinstaller --version 2>/dev/null || echo 'not installed')"
          echo ""
          echo "  Ready. Run: pyinstaller fieldsnek.spec"
        '';
      };
      devShells.buildozer = pkgs.mkShell {
        name = "fieldsnek-buildozer";
        inherit meta;
        ANDROID_HOME = androidSdkRoot;
        ANDROID_NDK_HOME = androidNdkRoot;
        ANDROID_NDK_ROOT = androidNdkRoot;
        ANDROID_NDK_VERSION = "r29b";
        ANDROID_SDK_ROOT = androidSdkRoot;
        BUILDOZER_BIN_DIR = "${buildozerBase}/bin";
        BUILDOZER_BUILD_DIR = "${buildozerBase}/build";
        GRADLE_OPTS = "-Xms512m -Xmx4g -XX:+HeapDumpOnOutOfMemoryError -XX:MaxMetaspaceSize=512m";
        GRADLE_USER_HOME = "${buildozerBase}/gradle-home";
        JAVA_HOME = "${pkgs.jdk17}";
        JAVA_TOOL_OPTIONS = "";
        _JAVA_OPTIONS = "";
        CCACHE_TEMPDIR = "/var/tmp/buildozer/tmp";
        PIP_CONFIG_FILE = "/dev/null";
        TEMP = "/var/tmp/buildozer/tmp";
        TMP = "/var/tmp/buildozer/tmp";
        TMPDIR = "/var/tmp/buildozer/tmp";
        buildInputs =
          commonPythonInputs
          ++ commonNativeInputs
          ++ (with pkgs; [
            autoconf
            automake
            cmake
            jdk17
            libtool
            ninja
            unzip
            which
          ]);
        shellHook = ''
                    echo "FieldSnek Android (Buildozer) env"
                    echo "  Java       : $(java -version 2>&1 | head -1)"
                    echo "  NDK        : $ANDROID_NDK_ROOT"
                    echo "  SDK        : $ANDROID_SDK_ROOT"
                    echo "  TMPDIR     : $TMPDIR"
                    echo "  Gradle home: $GRADLE_USER_HOME"
                    if [ ! -f "$ANDROID_NDK_ROOT/ndk-build" ]; then
                      echo "  WARNING: NDK not found at $ANDROID_NDK_ROOT"
                    fi
                    if [ ! -d "$ANDROID_SDK_ROOT/platform-tools" ]; then
                      echo "  WARNING: Android SDK incomplete at $ANDROID_SDK_ROOT"
                    fi
                    mkdir -p "$BUILDOZER_BUILD_DIR" \
                             "$BUILDOZER_BIN_DIR" \
                             "$GRADLE_USER_HOME" \
                             "$TMPDIR"
                    export PATH="$(echo "$PATH" | tr ':' '\n' \
                      | grep -vE '(ccache|java-25|jdk-[^1]|jre-)' \
                      | tr '\n' ':')"
                    export PATH="${pkgs.jdk17}/bin:$PATH"
                    export PATH="$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:\
          $ANDROID_SDK_ROOT/platform-tools:\
          $ANDROID_SDK_ROOT/tools/bin:\
          $PATH"
                    if [ ! -d .venv-buildozer ]; then
                      echo "  Creating buildozer venv with uv..."
                      uv venv .venv-buildozer
                      uv pip install --quiet --no-cache buildozer cython
                    fi
                    source .venv-buildozer/bin/activate
                    echo "  Python    : $(python --version)"
                    echo "  Buildozer : $(buildozer --version 2>/dev/null || echo 'not installed')"
                    echo "  uv        : $(uv --version)"
                    echo ""
                    echo "  Ready. Run: buildozer android debug"
        '';
      };
      devShells.windows = pkgs.mkShell {
        name = "fieldsnek-windows";
        buildInputs =
          commonPythonInputs
          ++ commonNativeInputs
          ++ (with pkgs; [
            mingwCC
            pkgsCross.mingwW64.windows.pthreads
            wineWowPackages.stable
            upx
          ]);
        CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER = "${mingwCC}/bin/x86_64-w64-mingw32-gcc";
        shellHook = ''
          echo "FieldSnek Windows cross-compile env"
          echo "  MinGW CC : $(x86_64-w64-mingw32-gcc --version 2>/dev/null | head -1 || echo 'not found')"
          echo "  Wine     : $(wine --version 2>/dev/null || echo 'not found')"
          echo "  uv       : $(uv --version)"
          export WINEPREFIX="$HOME/.wine-fieldsnek"
          export WINEARCH="win64"
          mkdir -p "$WINEPREFIX"
          if [ ! -f "$WINEPREFIX/drive_c/Python312/python.exe" ]; then
            echo ""
            echo "  First-run: bootstrapping Windows Python 3.12 in Wine..."
            echo "  Download Python 3.12 installer and run:"
            echo "    wine python-3.12.x-amd64.exe /quiet InstallAllUsers=0 TargetDir=C:\\Python312"
            echo "    wine C:\\Python312\\python.exe -m pip install pyinstaller customtkinter Pillow"
            echo "  Then re-enter this shell to build."
          else
            echo "  Wine Python: $(wine C:\\Python312\\python.exe --version 2>/dev/null)"
          fi
          echo ""
          echo "  Ready. Run: wine C:\\Python312\\Scripts\\pyinstaller.exe fieldsnek.spec"
        '';
      };
      devShells.maturin = pkgs.mkShell {
        name = "fieldsnek-maturin";
        CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER = "${mingwCC}/bin/x86_64-w64-mingw32-gcc";
        RUST_BACKTRACE = "1";
        RUST_SRC_PATH = "${rustToolchain}/lib/rustlib/src/rust/library";
        buildInputs =
          commonPythonInputs
          ++ (with pkgs; [
            maturin
            openssl
            pkg-config
            mingwCC
            rustToolchain
            zlib
          ]);
        shellHook = ''
          echo "FieldSnek maturin/Rust dev env"
          echo "  Rust    : $(rustc --version)"
          echo "  Cargo   : $(cargo --version)"
          echo "  Maturin : $(maturin --version)"
          echo "  Python  : $(python3 --version)"
          echo "  uv      : $(uv --version)"
          echo "  Targets : $(rustup target list --installed 2>/dev/null | tr '\n' ' ')"
          if [ ! -d .venv-maturin ]; then
            echo "  Creating maturin venv with uv..."
            uv venv .venv-maturin
          fi
          source .venv-maturin/bin/activate
          echo ""
          echo "  Linux build  : maturin develop"
          echo "  Windows build: cargo build --target x86_64-pc-windows-gnu"
          echo "  PyO3 check   : python3 -c 'import fieldsnek; print(fieldsnek.__doc__)'"
        '';
      };
    });
}
