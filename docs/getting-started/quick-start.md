# Quick Start Guide

Get your ESPHome configuration project up and running in minutes.

## Prerequisites

- macOS or Linux system
- Git installed
- Internet connection for downloading tools

## 1. Initial Setup

### Install Project Tools
```bash
# Install Mise (tool version manager)
curl https://mise.run | sh

# Navigate to project directory
cd /path/to/esphome-config

# Install project-specific tools
mise install
```

### Set Up Security Framework
```bash
# Set up security tools and validation
python3 scripts/setup_security.py

# Set up development environment (optional)
python3 scripts/setup_dev_secrets.py
```

## 2. Configure Credentials

### Option A: Production Setup (1Password)
```bash
# Create .env file for 1Password integration
echo "OP_ACCOUNT=your-1password-account" > .env

# Generate secrets from 1Password
./scripts/generate_secrets.sh
```

### Option B: Development Setup
```bash
# Use development credentials for testing
task dev-setup
cp dev/secrets.yaml secrets.yaml
```

## 3. Validate Setup

```bash
# Run security validation
task security-validate

# Test build system
task build -- den_multisensor
```

## 4. Deploy Your First Device

### For ESP32/ESP8266 Devices
```bash
# Build and upload firmware
task upload -- device_name
```

### For ESP01 Devices (Memory Constrained)
```bash
# Use two-stage deployment
task upload-two-stage -- device_name
```

## 5. Verify Deployment

- Check device appears in Home Assistant
- Verify device responds to ping: `ping device-name.local`
- Access web interface: `http://device-name.local`

## Common Commands

```bash
# List all available tasks
task -l

# Build all devices
task build-all

# Run comprehensive security scan
task security-scan

# Upload to all devices (two-stage)
task upload-all-two-stage
```

## Next Steps

- **[Development Setup](development-setup.md)** - Complete development environment
- **[Deploy Your First Device](first-device.md)** - Detailed device deployment guide
- **[Device Types](../device-management/device-types.md)** - Understanding different hardware platforms

## Troubleshooting

### Common Issues

**1Password CLI not working:**
```bash
# Sign in to 1Password
op signin

# Verify account access
op account list
```

**Security validation failing:**
```bash
# Check for exposed credentials
task security-scan

# Use development credentials for testing
task dev-setup
```

**Device not responding:**
- Check device is powered and connected to WiFi
- Verify network connectivity: `ping device-name.local`
- Try fallback hotspot access (see [Recovery Procedures](../device-management/recovery-procedures.md))

## Architecture Overview

For complete system architecture details, see [System Architecture](.kilocode/rules/memory-bank/architecture.md).

Key components:
- **ESPHome**: Firmware framework for IoT devices
- **1Password**: Secure credential storage
- **Task Runner**: Build and deployment automation
- **Python Security Framework**: Credential validation and rotation

---

*Need more detailed information? Check the [Memory Bank](.kilocode/rules/memory-bank/) for comprehensive technical documentation.*
