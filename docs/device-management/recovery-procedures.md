# Device Recovery Procedures

This guide provides comprehensive recovery procedures for ESPHome devices that have become unresponsive or bricked.

## Recovery Methods Overview

### Method 1: Fallback Hotspot Recovery (Preferred)
- **Best for**: Devices with fallback hotspot capability
- **Requirements**: Device powers on and creates hotspot
- **Success Rate**: High for properly configured devices

### Method 2: Recovery Network Setup
- **Best for**: ESP01 devices without fallback hotspot
- **Requirements**: Ability to create WiFi network with specific credentials
- **Success Rate**: High if device can connect to WiFi

### Method 3: Physical Recovery
- **Best for**: Completely bricked devices
- **Requirements**: Physical access and USB-to-serial adapter
- **Success Rate**: High but requires hardware access

## Fallback Hotspot Recovery

### Identifying Fallback Mode
When a device cannot connect to WiFi, it should automatically create a fallback hotspot:

**Look for WiFi networks named:**
- `[Device Name] ESP` (e.g., "Den Multisensor ESP")
- `[Device Name] Recovery`

### Recovery Steps
1. **Connect to fallback hotspot**
   - Network name: `[Device Name] ESP`
   - Password: Current fallback password from `secrets.yaml`

2. **Access device web interface**
   - Open browser to `http://192.168.4.1`
   - Device configuration page should load

3. **Reconfigure WiFi**
   - Enter correct WiFi credentials
   - Save configuration
   - Device should restart and connect to main network

4. **Deploy updated firmware**
   ```bash
   # Once device is back online
   task upload -- device_name
   ```

## Recovery Network Setup (ESP01 Devices)

### When to Use
- ESP01 devices that were deployed with minimal firmware lacking fallback hotspot
- Devices that are not broadcasting any hotspot networks
- Devices that appear completely offline

### Required Network Credentials
ESP01 devices may be configured to connect to specific credentials. Check the device configuration or use these common credentials:

```bash
# Common ESP01 recovery network credentials
SSID: "PorkNoT"
Password: "Internet0fBlinds."
Domain: ".NoT.Home.GeoffDavis.COM"
```

### Setup Recovery Network
1. **Create WiFi hotspot** with exact credentials above
   - Use mobile hotspot, router, or dedicated access point
   - **SSID and password must match exactly**

2. **Wait for device connection**
   - Devices should automatically connect within 1-2 minutes
   - Check connected devices list on your hotspot

3. **Access device**
   ```bash
   # Find device IP address
   nmap -sn 192.168.x.0/24  # Replace x with your hotspot subnet

   # Access device web interface
   http://<device-ip>
   ```

4. **Deploy recovery firmware**
   ```bash
   # Use recovery deployment script
   python3 scripts/recover_device.py <device_name>
   ```

## ESP01 Physical Recovery

### When Physical Recovery is Required
- Device does not create fallback hotspot
- Device does not connect to recovery network
- Device appears completely unresponsive
- Firmware corruption suspected

### Required Equipment
- **USB-to-Serial adapter** (FTDI or similar)
- **Jumper wires**
- **Computer** with esptool installed
- **Physical access** to the ESP01 device

### ESP01 Pin Layout
```
ESP01 Pin Layout:
┌─────────────┐
│ RST    VCC  │
│ EN     GPIO0│
│ GPIO2  GND  │
│ TXD    RXD  │
└─────────────┘
```

### Physical Connection
```bash
# Connections to USB-Serial adapter:
VCC   → 3.3V
GND   → GND
TXD   → RX (receive)
RXD   → TX (transmit)
GPIO0 → GND (for flash mode)
```

### Recovery Steps

#### 1. Enter Flash Mode
```bash
# Connect GPIO0 to GND (enter flash mode)
# Power on the device (or press reset if available)
# Verify connection
esptool.py --port /dev/ttyUSB0 chip_id
```

#### 2. Erase and Flash Recovery Firmware
```bash
# Erase existing firmware
esptool.py --port /dev/ttyUSB0 --baud 115200 erase_flash

# Flash recovery firmware
esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash 0x0 device-recovery.bin  # pragma: allowlist secret
```

#### 3. Exit Flash Mode
```bash
# Disconnect GPIO0 from GND
# Power cycle the device
# Look for recovery hotspot: "[Device Name] Recovery"
```

### Creating Recovery Firmware
```bash
# Compile recovery firmware with fallback hotspot
mise exec -- esphome compile <device>-minimal.yaml

# Recovery firmware location:
# .esphome/build/<device>/.pioenvs/esp01_1m/firmware.bin
```

## Device-Specific Recovery

### ESP01 Devices Requiring Special Attention
For detailed ESP01 recovery procedures, see [ESP01 Recovery Tasks](.kilocode/rules/memory-bank/tasks.md#esp01-two-stage-deployment).

**Affected ESP01 devices:**
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

### ESP32/ESP8266 Devices
Standard recovery procedures apply:
1. Try fallback hotspot first
2. Use direct firmware upload if accessible
3. Physical recovery rarely needed

## Automated Recovery Scripts

### Recovery Deployment Script
```bash
# Automated recovery for accessible devices
python3 scripts/recover_device.py <device_name>

# Recovery with specific network
python3 scripts/recover_device.py <device_name> --network recovery

# Emergency recovery mode
python3 scripts/recover_device.py <device_name> --emergency
```

### Recovery Network Deployment
```bash
# Deploy to devices on recovery network
python3 scripts/recovery_deployment.py <device_name>

# Deploy to all devices on recovery network
python3 scripts/recovery_deployment.py --all
```

## Post-Recovery Verification

### Verify Device Functionality
```bash
# Test network connectivity
ping device-name.local

# Test ESPHome API
esphome logs device.yaml --device device-name.local

# Verify web interface
curl http://device-name.local
```

### Deploy Production Firmware
```bash
# For ESP01 devices (two-stage)
task upload-two-stage -- device_name

# For ESP32/ESP8266 devices
task upload -- device_name
```

### Verify Home Assistant Integration
- Check device appears in Home Assistant
- Verify sensors are reporting data
- Test any controls (switches, climate, etc.)

## Prevention Measures

### Fallback Hotspot Configuration
**All devices should include fallback hotspot capability:**

```yaml
# In device configuration
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # Fallback hotspot for recovery
  ap:
    ssid: "${friendly_name} ESP"
    password: !secret fallback_password

# Enable captive portal for easy access
captive_portal:
```

### Regular Health Monitoring
```bash
# Monitor device connectivity
for device in $(ls *.yaml | sed 's/\.yaml$//' | grep -v '\-minimal$' | grep -v '\-full$'); do
    if ping -c 1 "$device.local" >/dev/null 2>&1; then
        echo "✅ $device: Online"
    else
        echo "❌ $device: Offline"
    fi
done
```

## Troubleshooting Recovery Issues

### Fallback Hotspot Not Appearing
**Possible causes:**
- Device not configured with fallback hotspot
- Device completely powered off
- Firmware corruption preventing boot

**Solutions:**
1. Verify device has power and is attempting to boot
2. Wait 2-3 minutes for fallback mode to activate
3. Try power cycling the device
4. Use recovery network method
5. Resort to physical recovery

### Recovery Network Connection Fails
**Possible causes:**
- Incorrect network credentials
- Device configured for different credentials
- Hardware failure

**Solutions:**
1. Verify exact SSID and password match device configuration
2. Try common credential combinations
3. Check device configuration files for expected credentials
4. Use physical recovery method

### Physical Recovery Fails
**Possible causes:**
- Incorrect wiring connections
- Wrong serial port or baud rate
- Hardware failure
- Power supply issues

**Solutions:**
1. Double-check all wiring connections
2. Try different USB-to-serial adapter
3. Verify 3.3V power supply (not 5V)
4. Test with different computer/USB port
5. Consider hardware replacement

## Emergency Procedures

### Multiple Device Failures
If multiple devices fail simultaneously:

1. **Check network infrastructure**
   - Verify WiFi network is operational
   - Check for network configuration changes
   - Verify DNS resolution

2. **Check credential changes**
   - Verify `secrets.yaml` hasn't been corrupted
   - Check if credentials were rotated without proper deployment
   - Validate 1Password access

3. **Systematic recovery**
   ```bash
   # Set up recovery network
   # Deploy recovery firmware to all affected devices
   python3 scripts/recovery_deployment.py --all --emergency
   ```

### Credential Rotation Gone Wrong
If credential rotation left devices inaccessible:

1. **Restore from backup**
   ```bash
   python3 scripts/backup_secrets.py restore <backup_id>
   ```

2. **Deploy restored credentials**
   ```bash
   python3 scripts/deploy_with_rotation.py --emergency
   ```

3. **Investigate and fix rotation issues**
   - Review rotation logs
   - Verify 1Password integration
   - Test rotation process in development environment

## Related Documentation

- **[Device Types](device-types.md)** - Understanding different hardware platforms
- **[Two-Stage Deployment](two-stage-deployment.md)** - ESP01 deployment process
- **[Security Troubleshooting](../security/troubleshooting.md)** - Security-related recovery issues
- **[Device Recovery Tasks](.kilocode/rules/memory-bank/tasks.md#device-recovery)** - Detailed technical procedures

---

*For comprehensive device recovery implementation details, see [Device Recovery Tasks](.kilocode/rules/memory-bank/tasks.md#device-recovery) in the Memory Bank.*
