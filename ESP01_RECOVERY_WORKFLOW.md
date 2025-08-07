# ESP01 Physical Recovery Workflow for denheatpump

## Overview

This document provides the complete step-by-step workflow for recovering bricked ESP01 devices using direct serial connection, starting with `denheatpump`.

## Required Equipment

- **USB-to-Serial adapter** (FTDI or similar) - MUST be 3.3V compatible
- **Jumper wires**
- **Computer** with this project's mise environment (esptool is included)
- **Physical access** to the ESP01 device

## Software Prerequisites

esptool is available through the project's mise environment. To verify:

```bash
# Check esptool is available
mise exec -- python3 -m esptool version
# Should show: esptool.py v4.9.0
```

If you need to install esptool separately:

```bash
# Install esptool via pip (if not using mise)
pip install esptool

# Or install via homebrew on macOS
brew install esptool
```

## Hardware Pin Layout Reference

### ESP01 Pin Layout

```text
ESP01 Pin Layout:
┌─────────────┐
│ RST    VCC  │
│ EN     GPIO0│
│ GPIO2  GND  │
│ TXD    RXD  │
└─────────────┘
```

### USB to TTL Serial Adapter Pinout

```text
USB to TTL Serial Adapter:
- RED wire    → 3.3V Power (VCC)
- BLACK wire  → Ground (GND)
- WHITE wire  → RX into USB port (receives data from ESP01 TX)
- GREEN wire  → TX out of USB port (transmits data to ESP01 RX)
```

### Complete Wiring Connections

```text
ESP01 Pin    →    USB-TTL Adapter Wire
─────────────────────────────────────────
VCC          →    RED (3.3V - NOT 5V!)
GND          →    BLACK (Ground)
TXD          →    WHITE (RX into adapter)
RXD          →    GREEN (TX from adapter)
GPIO0        →    BLACK (GND for flash mode only)
```

**CRITICAL SAFETY NOTE**: The RED wire must connect to 3.3V output on the adapter. Using 5V will permanently damage the ESP01!

## Recovery Process

### Step 1: Set Up Serial Connection Hardware

1. **CRITICAL**: Ensure USB-to-Serial adapter is set to 3.3V (NOT 5V)
2. **Wire the connections** using the specific wire colors:
   - **RED wire** (3.3V) → ESP01 VCC pin
   - **BLACK wire** (GND) → ESP01 GND pin
   - **WHITE wire** (RX) → ESP01 TXD pin
   - **GREEN wire** (TX) → ESP01 RXD pin
3. **Leave GPIO0 disconnected** for now (we'll connect it to BLACK/GND in Step 2)
4. **Double-check voltage**: Verify the adapter is outputting 3.3V, not 5V

### Step 2: Enter Flash Mode

1. **Connect GPIO0 to GND** using a jumper wire (connect GPIO0 pin to the BLACK wire/GND)
2. **Power on** the ESP01 device
3. **Verify connection** works:

   ```bash
   # Find your USB to UART device port
   ls /dev/tty.usbserial-*

   # Check if esptool can communicate (using your specific device)
   mise exec -- python3 -m esptool --port /dev/tty.usbserial-122420 chip_id

   # If your device has a different port number, adjust accordingly:
   # mise exec -- python3 -m esptool --port /dev/tty.usbserial-XXXXXX chip_id
   ```

### Step 3: Erase Existing Firmware

```bash
# Completely erase the corrupted firmware (using your specific USB to UART port)
mise exec -- python3 -m esptool --port /dev/tty.usbserial-122420 --baud 115200 erase_flash
```

### Step 4: Flash Recovery Firmware

```bash
# Flash the recovery firmware with fallback hotspot
mise exec -- python3 -m esptool --port /dev/tty.usbserial-122420 --baud 115200 write_flash 0x0 \
  .esphome/build/denheatpump/.pioenvs/denheatpump/firmware.bin
```

### Step 5: Exit Flash Mode

1. **Disconnect GPIO0 from GND** (remove the jumper wire)
2. **Power cycle** the device (disconnect and reconnect power)
3. **Wait 2-3 minutes** for device to boot and attempt network connection

### Step 6: Check Device Recovery Status

The recovery firmware will automatically try two connection methods:

**Option A: Production Network Connection (Preferred)**

1. **Device tries to connect** to your production NoT network first
2. **If successful**: Device will be immediately accessible at `denheatpump.local`
3. **Skip to Step 8** if device appears online

**Option B: Recovery Hotspot Fallback**

1. **If production network fails**: Device creates `"Den Heatpump Recovery"` hotspot
2. **Connect** to the recovery hotspot using `fallback_password`
3. **Open browser** to `http://192.168.4.1` and configure WiFi manually

### Step 7: Manual WiFi Configuration (Only if Step 6 Option B)

1. **Access web interface** at `http://192.168.4.1`
2. **Enter WiFi credentials** for your production network
3. **Save configuration** - device will restart and connect to main network

### Step 8: Deploy Full Firmware

Once device is back on your main network:

```bash
# Deploy the complete firmware with current credentials
mise exec -- task upload -- denheatpump-full
```

**Note**: The external component issue has been resolved - ESPHome will automatically find a compatible version (like 1.4.1). The security validation has also been fixed to avoid false positives from tool names in configuration files.

**If deployment still fails:**

1. Check the [MitsubishiCN105ESPHome repository](https://github.com/echavet/MitsubishiCN105ESPHome) for available version tags
2. Update line 7 in `common/heatpump-climate.yaml` with a specific version if needed
3. Use the recovery firmware temporarily if full firmware deployment continues to fail

### Step 9: Verify Recovery Success

```bash
# Test network connectivity
ping denheatpump.local

# Check ESPHome logs
esphome logs denheatpump-full.yaml --device denheatpump.local

# Verify web interface
curl http://denheatpump.local
```

## Troubleshooting

### esptool Cannot Connect

- **Check wiring**: Ensure all connections are secure
- **Verify GPIO0 to GND**: Must be connected during flash mode
- **Try different baud rates**: 9600, 57600, 115200
- **Check port**: Use `ls /dev/tty*` to find correct serial port

### No Recovery Hotspot Appears

- **Wait longer**: Can take 2-3 minutes to appear
- **Power cycle**: Disconnect and reconnect power
- **Check firmware flash**: Ensure esptool reported success
- **Verify GPIO0 disconnected**: Must be removed after flashing

### Device Won't Connect to Main WiFi

- **Double-check credentials**: Verify SSID and password in web interface
- **Check network compatibility**: Ensure 2.4GHz network (ESP01 doesn't support 5GHz)
- **Signal strength**: Move device closer to router

### Full Firmware Deployment Fails

- **External component error**: Update `common/heatpump-climate.yaml` line 7:

  ```yaml
  # Use proper version tag format with 'v' prefix:
  - source: github://echavet/MitsubishiCN105ESPHome@v1.4.1
  # Or use main branch for latest:
  - source: github://echavet/MitsubishiCN105ESPHome@main
  ```

- **Check repository**: Visit the GitHub repo to find valid version tags (use 'v' prefix)
- **Alternative**: Use recovery firmware temporarily until external component is fixed

## Files Created

- ✅ Recovery firmware: `denheatpump-recovery.yaml`
- ✅ Compiled binary: `.esphome/build/denheatpump/.pioenvs/denheatpump/firmware.bin`

## Next Steps

After successfully recovering `denheatpump`, repeat this process for other bricked ESP01 devices:

- `attic_sensor`
- `bedroom_east_heatpump`
- `bedroom_west_heatpump`
- `hodad_outlet`
- `mpmd_light_topgreener`
- `pruscilla_light_topgreener`
- `tg_dishwasher`
- `tg_lrtv`
- `voronica_outlet`

## Safety Notes

- **NEVER use 5V** on ESP01 - it will permanently damage the device
- **Always disconnect GPIO0** after flashing - leaving it connected prevents normal boot
- **Take photos** of original wiring before disconnecting devices
- **Work on one device at a time** to avoid confusion

## Recovery Firmware Features

The recovery firmware includes:

- ✅ **Automatic production network connection** - Tries to connect to NoT network first
- ✅ **Intelligent fallback hotspot** - Creates recovery hotspot only if production network fails
- ✅ **Captive portal** for easy manual configuration
- ✅ **Web server** for direct access and configuration
- ✅ **OTA capability** for firmware updates
- ✅ **API access** for ESPHome integration
- ✅ **Extended timeout settings** - 15 minute reboot timeout for connection attempts

This dual-mode approach means:

- **Best case**: Device connects directly to production network and is immediately accessible
- **Fallback case**: Device creates recovery hotspot for manual configuration
- **Future-proof**: Device can always be recovered, even if WiFi credentials change
