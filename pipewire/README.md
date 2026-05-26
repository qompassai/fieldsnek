# FieldSnek PipeWire Configuration

These config fragments improve voice recognition quality on Linux by routing
FieldSnek's microphone input through an echo-cancelled, noise-reduced virtual
source managed by WirePlumber.

## Installation

Copy both files to your PipeWire config directory:

```bash
mkdir -p ~/.config/pipewire/pipewire.conf.d
cp 51-fieldsnek-echo-cancel.conf ~/.config/pipewire/pipewire.conf.d/
systemctl --user restart pipewire pipewire-pulse
```

After restarting, a new virtual audio source named **"FieldSnek Echo Cancel"**
will appear in your audio device list.

Set it as the capture source for FieldSnek:

```bash
# In your shell or .env file:
export FIELDSNEK_PIPEWIRE_NODE="FieldSnek Echo Cancel"
```

Or configure it in the FieldSnek Settings screen under "PipeWire Source Node".

## What it does

- **Echo cancellation** — removes speaker bleed from the mic (important when
  your PC is playing audio while you dictate an address)
- **Noise suppression** — applies RNNoise LADSPA filter if installed
  (`pacman -S ladspa-rnnoise` on Arch, `apt install ladspa-rnnoise` on Debian)
- **Voice activity detection** — Whisper's built-in VAD handles silence, but
  a clean signal speeds up and improves accuracy

## Without this config

FieldSnek falls back to the system default microphone automatically.
Voice recognition still works, just without the audio cleanup stage.
