# ESPHome Device Configurations

ESPHome configs for the devices in the house: Mitsubishi heat pumps (CN105),
the doorbell, smart plugs, and a few one-offs.

## Layout

| Path | What's there |
| --- | --- |
| `*.yaml` | One file per device. ESP-01 (1MB) devices have a `-minimal.yaml` and a `-full.yaml` (see below). |
| `common/` | Shared packages: board definitions, wifi/api/ota, heat pump, outlet types. |
| `include/` | C++ helpers used by lambdas (`aqipm.h` for the particle sensor's AQI). |
| `fonts/` | Fonts for devices with displays. |
| `archive/` | Retired configs kept for reference. Not validated or updated. |
| `scripts/`, `tests/` | Secrets generation and credential tooling, and its tests. |

## Setup

The dev shell (nix flake, loaded by direnv) provides Python, uv, Node, and
pre-commit, and syncs `.venv` with the ESPHome version pinned in
`pyproject.toml`.

```bash
direnv allow
task secrets        # writes secrets.yaml from 1Password
```

`secrets.yaml` is gitignored; `secrets.yaml.example` lists the keys.

## Validate, build, flash

```bash
esphome config doorbell.yaml       # validate one device
task build -- doorbell             # compile
task upload -- doorbell            # compile and flash over the network
```

ESP-01 devices have too little flash for an OTA of the full firmware over
itself, so they go in two stages: flash the minimal firmware, then the full
one.

```bash
task upload-two-stage -- tg_lrtv
```

A device that can't be reached over the network has to be flashed over
serial (USB, or the UART header on ESP-01 based plugs):

```bash
esphome run tg_lrtv-minimal.yaml --device /dev/tty.usbserial-XXXX
```

## OTA encryption migration

OTA uploads are encrypted with the API key. Devices on firmware older than
ESPHome 2026.9.0 can't do that, so `common/wifi.yaml`,
`common/wifi-minimal.yaml`, and `denheatpump-recovery.yaml` still set
`allow_plaintext_upload: true` and the OTA password for their first upload.
Remove both once every device has been flashed with the current config; the
plaintext fallback goes away in ESPHome 2027.3.0.

## CI and dependencies

- **ESPHome Validate** runs `esphome config` on every device file against
  placeholder secrets.
- **Essential Security Checks** runs pre-commit and secret scanning.
- **Renovate** keeps ESPHome, the CN105 component, GitHub Actions, and the
  pre-commit hooks current.
