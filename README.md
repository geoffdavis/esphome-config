# ESPHome Device Configurations

ESPHome configs for the devices in the house: Mitsubishi heat pumps (CN105),
the doorbell, smart plugs, an NSPanel, and a few one-offs.

## Layout

| Path | What's there |
| --- | --- |
| `*.yaml` | One file per device. The den heat pump (ESP-01) has a `-minimal.yaml` and a `-full.yaml` for two-stage OTA (see below). |
| `common/` | Shared packages: board definitions, wifi/api/ota, heat pump, outlet types. |
| `components/` | Local external components (`stmpe610` touch controller, used by `desk-panel.yaml`). |
| `include/` | C++ helpers used by lambdas (`aqipm.h` for the particle sensor's AQI). |
| `fonts/` | Fonts for devices with displays. |
| `archive/` | Retired configs kept for reference. Not validated or updated. |
| `scripts/` | `generate_secrets.sh`, which `task secrets` runs. |

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

ESP-01 (1MB) devices take an OTA only when the running image and the new
one fit in 1004KB together (the new image is written above the running one,
up to the start of the filesystem area at 0xFB000; sizes round up to 4KB).

The power plugs (TopGreener and Sonoff S31) fit in one stage: their
packages log at INFO instead of DEBUG and the TopGreeners leave out IPv6,
so the full firmware is about 442KB (S31: about 451KB). Keep each image
under about 500KB to stay single-stage; check the `Flash:` line after a
build.

The den heat pump (`denheatpump-full.yaml`, about 556KB) is still too big,
so it goes in two stages: flash the minimal firmware, then the full one.

```bash
task upload-two-stage -- denheatpump
```

A device that can't be reached over the network has to be flashed over
serial (USB, or the UART header on ESP-01 based plugs):

```bash
esphome run tg_lrtv.yaml --device /dev/tty.usbserial-XXXX
```

## NSPanels (NSPanel Easy)

`kitchen-porch-panel.yaml` and `entry-hall-panel.yaml` are Sonoff NSPanels
running [NSPanel Easy](https://github.com/edwardtfn/NSPanel-Easy) as a
remote package. Everything they share is in `common/nspanel-easy.yaml`; the
device files hold only names and hardware notes. They don't include
`common/wifi.yaml` (the package defines wifi, api and ota), and their pages
and buttons are set from each panel's HA blueprint automation, not here.
Panels sit on VLAN 60, which has no internet, so the display (TFT) file
comes from nas-sdg's mirror via `nextion_update_base_url`
(nix-personal `hosts/nas-sdg/nspanel-tft.nix`). Renovate bumps the package
`ref:`. Full setup: the notes vault's "Set Up an NSPanel with NSPanel Easy".

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
