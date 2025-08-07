# ESP01 Physical Recovery Guide

## CRITICAL SITUATION CONFIRMED

The ESP01 devices are completely bricked and require **PHYSICAL RECOVERY**.
Here's what happened:

1. ✅ **Minimal firmware deployed successfully** (using old wifi-minimal.yaml
   without fallback hotspot)
2. ❌ **Devices became inaccessible** (no fallback hotspot for recovery)
3. ❌ **Full firmware deployment failed** (devices unreachable)
4. ❌ **Devices not visible in UniFi or broadcasting hotspots** (completely
   bricked)

## Affected ESP01 Devices

The following devices need physical recovery:

- `attic_sensor` (ESP01)
- `bedroom_east_heatpump` (ESP01)
- `bedroom_west_heatpump` (ESP01)
- `denheatpump` (ESP01)
- `hodad_outlet` (ESP01)
- `mpmd_light_topgreener` (ESP01)
- `pruscilla_light_topgreener` (ESP01)
- `tg_dishwasher` (ESP01)
- `tg_lrtv` (ESP01)
- `voronica_outlet` (ESP01)

## Physical Recovery Process

### Required Equipment

- USB-to-Serial adapter (FTDI or similar)
- Jumper wires
- Computer with esptool installed

### Recovery Steps for Each Device

#### 1. Physical Connection

```text
ESP01 Pin Layout:
┌─────────────┐
│ RST    VCC  │
│ EN     GPIO0│
│ GPIO2  GND  │
│ TXD    RXD  │
└─────────────┘

Connections to USB-Serial:
- VCC → 3.3V
- GND → GND
- TXD → RX
- RXD → TX
- GPIO0 → GND (for flash mode)
```

#### 2. Enter Flash Mode

1. **Connect GPIO0 to GND** (enter flash mode)
2. **Power on** the device (or press reset if available)
3. **Verify connection**: `esptool.py --port /dev/ttyUSB0 chip_id`

#### 3. Flash Recovery Firmware

```bash
# Erase existing firmware
esptool.py --port /dev/ttyUSB0 --baud 115200 erase_flash

# Flash new firmware with fallback hotspot
esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash 0x0 <device>-recovery.bin
```

#### 4. Exit Flash Mode

1. **Disconnect GPIO0 from GND**
2. **Power cycle** the device
3. **Look for recovery hotspot**: `"<Device Name> Recovery"`

### Alternative: Use ESPHome Web Flasher

If available, use the ESPHome web flasher tool for easier recovery.

## Recovery Firmware Creation

For each device, create recovery firmware with fallback hotspot:

```bash
# Compile recovery firmware (using fixed wifi-minimal.yaml)
mise exec -- esphome compile <device>-minimal.yaml

# The .bin file will be in:
# .esphome/build/<device>/.pioenvs/esp01_1m/firmware.bin
```

## Post-Recovery Steps

Once devices are recovered and broadcasting hotspots:

1. **Connect to recovery hotspot**
2. **Access web interface** (usually 192.168.4.1)
3. **Configure WiFi** to connect to PorkNoT network
4. **Deploy full firmware** with new credentials

## Prevention

✅ **Fixed wifi-minimal.yaml** now includes fallback hotspot to prevent future bricking.

## Recovery Script Usage

After physical recovery, use the automated script:

```bash
python3 scripts/recovery_deployment.py <device_name>
```

## Important Notes

- **ESP01 devices are particularly vulnerable** due to limited GPIO pins
- **Physical access is required** - no remote recovery possible
- **Each device must be recovered individually**
- **Take photos of original wiring** before disconnecting devices

## Success Indicators

After recovery:

- ✅ Device appears in UniFi controller
- ✅ Device responds to ping at `<device>.local`
- ✅ Web interface accessible
- ✅ ESPHome logs show successful connection
