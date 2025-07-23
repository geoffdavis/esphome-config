# ESP01 Device Recovery Plan

## CRITICAL ISSUE IDENTIFIED

The ESP01 devices were bricked during credential deployment because the minimal firmware (`wifi-minimal.yaml`) lacked fallback hotspot capability. When minimal firmware was deployed first, devices lost their recovery mechanism.

## WiFi Credentials the Bricked Devices Are Using

The ESP01 devices with minimal firmware are configured to connect to:

- **SSID**: `PorkNoT`
- **Password**: `Internet0fBlinds.`
- **Domain**: `.NoT.Home.GeoffDavis.COM`

## Recovery Method 1: Temporary Recovery Network (RECOMMENDED)

### Setup Recovery WiFi Network:
1. Create a WiFi hotspot/access point with these **EXACT** credentials:
   - **Network Name**: `PorkNoT`
   - **Password**: `Internet0fBlinds.`

2. **Wait for devices to connect** - they should appear on the network

3. **Access devices via**:
   - Web interface: `http://<device-ip>`
   - ESPHome OTA for firmware updates

### Recovery Deployment Steps:
1. Once devices are connected to recovery network
2. Deploy fixed minimal firmware (now includes fallback hotspot)
3. Deploy full firmware with new credentials
4. Verify devices work on production network

## Recovery Method 2: Physical Recovery (If Network Setup Not Possible)

### ESP01 Physical Recovery Process:
For each bricked device:

1. **Power OFF** the device
2. **Connect GPIO0 to GND** (enter flash mode)
3. **Power ON** the device
4. **Flash recovery firmware** using esptool:
   ```bash
   esptool.py --port /dev/ttyUSB0 --baud 115200 erase_flash
   esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash 0x0 <device>-recovery.bin
   ```
5. **Disconnect GPIO0** from GND
6. **Power cycle** the device
7. Look for recovery hotspot: `"<Device Name> Recovery"`

## Affected ESP01 Devices

The following ESP01 devices are likely bricked:
- `attic_sensor`
- `bedroom_east_heatpump`
- `bedroom_west_heatpump`
- `denheatpump`
- `hodad_outlet`
- `mpmd_light_topgreener`
- `pruscilla_light_topgreener`
- `tg_dishwasher`
- `tg_lrtv`
- `voronica_outlet`

## Root Cause Fix Applied

✅ **Fixed `common/wifi-minimal.yaml`** to include:
- Fallback hotspot configuration
- Captive portal for recovery
- API and web server access
- This prevents future device bricking

## Next Steps

1. **Set up recovery network** with credentials above
2. **Wait for devices to connect**
3. **Deploy fixed firmware** using recovery deployment script
4. **Validate all devices** are accessible with new credentials

## Recovery Deployment Script

Use `scripts/deploy_with_rotation.py` once devices are accessible:
```bash
python3 scripts/deploy_with_rotation.py --device <device_name>
```

The script will:
1. Deploy fixed minimal firmware (with fallback hotspot)
2. Deploy full firmware with new credentials
3. Verify connectivity

## Prevention

The minimal firmware configuration has been permanently fixed to always include fallback hotspot capability, preventing this issue from recurring.
