# ESP32 M5Stack NanoC6 Deployment Guide

## Overview

This guide covers the deployment process for ESP32 M5Stack NanoC6 devices, specifically for the bedroom_east_heatpump
hardware upgrade from ESP01 to ESP32-C6.

## Hardware Specifications

- **Board**: ESP32-C6-DevKitC-1 compatible (M5Stack NanoC6)
- **Flash Memory**: 4MB (significant upgrade from ESP01's 1MB)
- **Framework**: ESP-IDF
- **UART Pins**: GPIO1 (TX), GPIO2 (RX) for heat pump communication
- **USB Connection**: `/dev/tty.debug-console` (or similar USB serial port)

## Pre-Deployment Verification

### 1. Configuration Validation

The configuration has been verified and includes:

```yaml
# bedroom_east_heatpump.yaml
substitutions:
  name: bedroom-east-heatpump
  friendly_name: East Bedroom HeatPump
  model: MFZ-KA09NA
  remote_temp_sensor: sensor.eastbedroom_htg_temperature

packages:
  wifi: !include common/wifi.yaml
  ipv6: !include common/ipv6.yaml
  sensors: !include common/sensors.yaml
  heatpump-esp32-nanoc6: !include common/heatpump-esp32-nanoc6.yaml
  climate: !include common/heatpump-climate.yaml
```

### 2. Build Verification

✅ **Build Status**: Successfully compiled

- **Platform**: ESP32-C6 recognized correctly
- **Framework**: ESP-IDF working properly

- **Memory Usage**:
  - RAM: 12.2% (40,124 bytes used of 327,680 bytes)
  - Flash: 63.2% (1,158,937 bytes used of 1,835,008 bytes)
- **Binary Generated**: `firmware.factory.bin` ready for flashing

### 3. Security Validation

✅ **Security Status**: All validations passed

- No exposed credentials detected
- 1Password integration working
- Pre-commit hooks active

## Initial Serial Flashing Process

Since this is a new ESP32 device replacing an ESP01, initial flashing must be done via USB serial connection.

### 1. Hardware Connection

1. Connect the M5Stack NanoC6 to your computer via USB-C cable
2. Verify the device appears as `/dev/tty.debug-console` (or similar)
3. Ensure heat pump CN105 connector is properly wired:
   - GPIO1 → CN105 TX
   - GPIO2 → CN105 RX
   - Ground connection established

### 2. Initial Flash Command

```bash
# Navigate to project directory
cd /Users/geoff/src/personal/esphome-config

# Flash the firmware via USB serial
mise exec -- esphome run bedroom_east_heatpump.yaml --device /dev/tty.debug-console
```

**Alternative using task system:**

```bash
# If task system supports serial flashing
mise exec -- task upload -- bedroom_east_heatpump --device /dev/tty.usbmodem2101
```

### 3. First Boot Verification

After successful flashing:

1. **Monitor Serial Output**:

   ```bash
   mise exec -- esphome logs bedroom_east_heatpump.yaml --device /dev/tty.usbmodem2102
   ```

2. **Expected Boot Sequence**:
   - ESP32-C6 initialization
   - WiFi connection attempt
   - Heat pump CN105 communication establishment
   - Home Assistant API connection
   - Web server startup on port 80

3. **Network Verification**:
   - Device should connect to WiFi network
   - Check Home Assistant for new device discovery
   - Verify web interface accessible at device IP

## OTA Deployment for Future Updates

Once the device is successfully flashed and connected to WiFi, all future updates can be done over-the-air.

### 1. Standard OTA Update

```bash
# For future updates after initial flash
mise exec -- task upload -- bedroom_east_heatpump
```

### 2. OTA Update Process

The system will:

1. Run security validation automatically
2. Compile firmware if needed
3. Connect to device over WiFi
4. Upload new firmware via OTA
5. Device will reboot with new firmware

### 3. OTA Troubleshooting

If OTA fails:

- Verify device is online and reachable
- Check WiFi connectivity
- Ensure OTA password is correct in secrets.yaml
- Fall back to serial flashing if necessary

## Device Configuration Details

### 1. Heat Pump Integration

- **Protocol**: CN105 communication via UART
- **External Component**: MitsubishiCN105ESPHome v1.4.1
- **Remote Temperature**: Uses Home Assistant sensor `sensor.eastbedroom_htg_temperature`
- **Climate Entity**: Exposed as "East Bedroom HeatPump" in Home Assistant

### 2. Network Configuration

- **WiFi**: Full configuration with web server
- **IPv6**: Enabled for future-proofing
- **mDNS**: Device discoverable as `bedroom-east-heatpump.local`
- **API**: Encrypted communication with Home Assistant
- **Web Server**: Available on port 80 for direct access

### 3. Monitoring and Diagnostics

Built-in sensors include:

- WiFi signal strength
- Device uptime
- Heat pump status and diagnostics
- Compressor frequency (if supported by unit)
- Energy usage tracking (if supported)

## Deployment Checklist

### Pre-Deployment

- [ ] ESP32 M5Stack NanoC6 hardware ready
- [ ] USB-C cable connected
- [ ] Heat pump CN105 wiring completed
- [ ] Configuration files validated
- [ ] Security validation passed
- [ ] Firmware compiled successfully

### Initial Flash

- [ ] Device detected at `/dev/tty.debug-console`
- [ ] Serial flash command executed
- [ ] Boot sequence monitored
- [ ] WiFi connection established
- [ ] Home Assistant discovery confirmed

### Post-Deployment

- [ ] Heat pump communication verified
- [ ] Climate entity functional in Home Assistant
- [ ] Remote temperature sensor working
- [ ] Web interface accessible
- [ ] OTA updates tested
- [ ] Device monitoring active

## Troubleshooting

### Common Issues

1. **Device Not Detected**
   - Check USB-C cable connection
   - Verify driver installation for ESP32-C6
   - Try different USB port

2. **Flash Failure**
   - Ensure device is in download mode
   - Check for sufficient power supply
   - Verify correct device path

3. **WiFi Connection Issues**
   - Verify WiFi credentials in secrets.yaml
   - Check network accessibility
   - Monitor serial output for connection attempts

4. **Heat Pump Communication Issues**
   - Verify CN105 wiring (GPIO1/GPIO2)
   - Check UART configuration in common/heatpump-esp32-nanoc6.yaml
   - Monitor logs for CN105 communication errors

### Recovery Procedures

If the device becomes unresponsive:

1. Use serial connection to reflash firmware
2. Check for fallback hotspot: "East Bedroom HeatPump ESP"
3. Access recovery interface at <http://192.168.4.1>
4. Reconfigure WiFi settings if needed

## Hardware Migration Notes

### From ESP01 to ESP32-C6

**Advantages of ESP32-C6:**

- 4MB flash vs 1MB (no more two-stage deployment needed)
- More GPIO pins available
- Better processing power
- Native USB support
- Improved WiFi performance

**Configuration Changes:**

- Single-stage deployment (no minimal/full split needed)
- Full feature set available immediately
- Enhanced logging and debugging capabilities
- IPv6 support enabled

**Wiring Considerations:**

- CN105 connections remain the same (TX/RX pins)
- Power requirements may differ (check specifications)
- Physical mounting may need adjustment

## Security Considerations

- All credentials managed through 1Password integration
- OTA password rotation supported
- API encryption enabled
- No hardcoded secrets in configuration files
- Pre-commit hooks prevent credential exposure

## Support and Maintenance

For ongoing support:

- Monitor device health through Home Assistant
- Regular OTA updates for security and features
- Backup configuration files before major changes
- Document any custom modifications

---

**Last Updated**: 2025-01-06
**Device**: bedroom_east_heatpump (ESP32 M5Stack NanoC6)
**Configuration Version**: ESP32-C6 with CN105 heat pump integration
