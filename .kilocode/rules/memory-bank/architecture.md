# System Architecture

## Overview

The ESPHome configuration system follows a hierarchical, component-based architecture that enables scalable device management, secure credential handling, and flexible deployment strategies. The system is designed around three core principles: modularity, security, and maintainability.

## Core Architecture Patterns

### 1. Hierarchical Configuration System

```
Device Configuration (e.g., den_multisensor.yaml)
├── Substitutions (device-specific parameters)
├── Packages (shared component includes)
│   ├── Hardware Platform (esp32, esp8266, esp01)
│   ├── Connectivity (wifi.yaml, wifi-minimal.yaml)
│   ├── Common Services (sensors.yaml, ipv6.yaml)
│   └── Specialized Components (sensor/bme280.yaml)
└── Device-Specific Overrides
```

### 2. Package-Based Component System

The [`common/`](common/) directory contains reusable components organized by function:

- **Platform Packages**: [`esp01.yaml`](common/esp01.yaml), [`nodemcuv2.yaml`](common/nodemcuv2.yaml), [`esp32_device_base.yaml`](common/esp32_device_base.yaml)
- **Connectivity Packages**: [`wifi.yaml`](common/wifi.yaml), [`wifi-minimal.yaml`](common/wifi-minimal.yaml), [`ipv6.yaml`](common/ipv6.yaml)
- **Sensor Packages**: [`sensor/bme280.yaml`](common/sensor/bme280.yaml), [`sensor/dht.yaml`](common/sensor/dht.yaml), [`sensor/pir.yaml`](common/sensor/pir.yaml)
- **Device-Specific Packages**: [`heatpump-esp01.yaml`](common/heatpump-esp01.yaml), [`outlet-topgreener.yaml`](common/outlet-topgreener.yaml)

### 3. Two-Stage Deployment Architecture

For memory-constrained ESP01 devices (1MB flash):

```
Stage 1: Minimal Deployment
├── Device-minimal.yaml (e.g., attic_sensor-minimal.yaml)
├── wifi-minimal.yaml (basic connectivity)
├── esp01.yaml (platform configuration)
└── Essential services only

Stage 2: Full Deployment
├── Device-full.yaml (e.g., attic_sensor-full.yaml)
├── wifi.yaml (full connectivity features)
├── All sensors and components
└── Web server and advanced features
```

## Security Architecture

### 1. Credential Management Layer

```
1Password Vaults
├── Automation Vault
│   └── ESPHome Item
│       ├── api_key (44-char base64)
│       ├── ota_password (32-char hex)
│       └── fallback_password (12+ char alphanumeric)
└── Shared Vault
    └── Home IoT Item
        ├── network name (WiFi SSID)
        ├── wireless network password
        └── domain name
```

### 2. Python Security Framework

Located in [`scripts/`](scripts/) directory:

- **Core Library**: [`security_lib.py`](scripts/security_lib.py) - Shared security utilities
- **Validation**: [`validate_secrets.py`](scripts/validate_secrets.py) - Credential format validation
- **1Password Integration**: [`validate_1password_structure.py`](scripts/validate_1password_structure.py)
- **Credential Rotation**: [`rotate_credentials.py`](scripts/rotate_credentials.py)
- **Deployment with Rotation**: [`deploy_with_rotation.py`](scripts/deploy_with_rotation.py)
- **Device Recovery**: [`recover_device.py`](scripts/recover_device.py)
- **Rotation Tracking**: [`track_secret_rotation.py`](scripts/track_secret_rotation.py)
- **Backup Management**: [`backup_secrets.py`](scripts/backup_secrets.py)
- **Development Support**: [`setup_dev_secrets.py`](scripts/setup_dev_secrets.py)

### 3. Security Validation Pipeline

```
Pre-commit Hooks
├── detect-secrets (exposed credential detection)
├── yamllint (YAML format validation)
├── esphome-secrets-validation (Python-based validation)
├── esphome-1password-validation (1Password structure check)
└── python-security-tests (unit test execution)
```

## Device Architecture Patterns

### 1. Standard ESP32/ESP8266 Devices

Example: [`den_multisensor.yaml`](den_multisensor.yaml)

```yaml
substitutions:
  name: den-multisensor
  friendly_name: Den Multisensor
  # Hardware-specific pin assignments

packages:
  nodemcuv2: !include common/nodemcuv2.yaml
  wifi: !include common/wifi.yaml
  ipv6: !include common/ipv6.yaml
  sensors: !include common/sensors.yaml
  sensor_bme280: !include common/sensor/bme280.yaml
  # Additional sensor packages as needed
```

### 2. Memory-Constrained ESP01 Devices

Minimal Configuration: [`attic_sensor-minimal.yaml`](attic_sensor-minimal.yaml)
```yaml
packages:
  wifi: !include common/wifi-minimal.yaml  # Reduced feature set
  esp01: !include common/esp01.yaml        # Platform-specific settings
```

Full Configuration: [`attic_sensor-full.yaml`](attic_sensor-full.yaml)
```yaml
packages:
  wifi: !include common/wifi.yaml          # Full feature set
  ipv6: !include common/ipv6.yaml
  sensors: !include common/sensors.yaml
  sensor_dht: !include common/sensor/dht.yaml
  esp01: !include common/esp01.yaml
```

### 3. Specialized Device Types

**Heat Pump Controllers**: Use ESP01 with specialized climate control packages
- [`common/heatpump-esp01.yaml`](common/heatpump-esp01.yaml)
- [`common/heatpump-climate.yaml`](common/heatpump-climate.yaml)
- [`common/heatpump-fanspeeds.yaml`](common/heatpump-fanspeeds.yaml)

**Smart Outlets**: TopGreener and Sonoff variants
- [`common/outlet-topgreener.yaml`](common/outlet-topgreener.yaml)
- [`common/sonoff_s31.yaml`](common/sonoff_s31.yaml)

**Audio-Reactive LEDs**: Custom FFT processing
- [`custom_components/esphome-music-leds/`](custom_components/esphome-music-leds/)

## Build and Deployment Architecture

### 1. Task-Based Automation

[`Taskfile.yml`](Taskfile.yml) provides standardized workflows:

```yaml
Security Integration:
├── security-validate (essential pre-deployment checks)
├── security-scan (comprehensive security scanning)
└── security-setup (framework initialization)

Device Operations:
├── build (compile firmware for single device)
├── upload (deploy firmware with security validation)
├── upload-two-stage (ESP01 deployment process)
└── upload-all-two-stage (bulk deployment)
```

### 2. Development Environment

**Tool Management**: [`mise.toml`](.mise.toml)
- Python 3.11 (security framework)
- Task (automation runner)
- Node.js 22.13.0 (Renovate dependency updates)

**Dependency Management**:
- [`requirements.txt`](requirements.txt): ESPHome core
- [`package.json`](package.json): Renovate for automated updates

### 3. Quality Assurance Pipeline

**Pre-commit Integration**: [`.pre-commit-config.yaml`](.pre-commit-config.yaml)
- Secret detection with detect-secrets
- YAML linting with yamllint
- Python security framework validation
- Custom ESPHome credential checking

**Testing Framework**: [`tests/`](tests/)
- [`test_security_lib.py`](tests/test_security_lib.py): Core library tests
- [`run_tests.py`](tests/run_tests.py): Test runner with environment checking
- Mock-based testing for 1Password integration

## Data Flow Architecture

### 1. Credential Flow

```
1Password Vaults → generate_secrets.sh → secrets.yaml → Device Configurations
                ↓
Security Validation → Pre-commit Hooks → Deployment Pipeline
```

### 2. Device Communication Flow

```
ESPHome Device ←→ Home Assistant
     ↓              ↑
API Encryption   Entity Discovery
(api_key)        (automatic)
     ↓              ↑
OTA Updates      State Sync
(ota_password)   (real-time)
```

### 3. Recovery Flow

```
Device Boot → WiFi Connection Attempt
     ↓
Connection Failed → Fallback Hotspot
     ↓
Captive Portal → Web Interface → Manual Configuration
```

## File Organization Patterns

### 1. Root Level Structure

```
├── Device Configurations (*.yaml)
├── common/ (shared components)
├── scripts/ (security framework)
├── tests/ (validation tests)
├── custom_components/ (ESPHome extensions)
├── include/ (C++ headers)
├── fonts/ (display resources)
└── packages/ (deployment packages)
```

### 2. Common Components Hierarchy

```
common/
├── Platform Definitions
│   ├── esp01.yaml, esp32_device_base.yaml
│   └── nodemcuv2.yaml, wemosd1mini.yaml
├── Connectivity
│   ├── wifi.yaml, wifi-minimal.yaml
│   └── ipv6.yaml
├── Sensors (sensor/)
│   ├── bme280.yaml, dht.yaml, dht22.yaml
│   ├── pir.yaml, temt6000.yaml
│   └── uptime.config.yaml, wifi_signal.config.yaml
└── Device-Specific
    ├── heatpump-*.yaml
    └── outlet-*.yaml
```

## Integration Architecture

### 1. Home Assistant Integration

- **API Communication**: Encrypted with rotating API keys
- **Entity Discovery**: Automatic device and sensor registration
- **State Management**: Real-time bidirectional communication
- **Service Integration**: Climate controls, switches, sensors

### 2. 1Password Integration

- **Credential Storage**: Structured vault organization
- **Automated Retrieval**: CLI-based secret fetching
- **Rotation Support**: Coordinated credential updates
- **Audit Trail**: Change tracking and history

### 3. Development Tool Integration

- **Mise**: Environment and tool version management
- **Task**: Workflow automation and standardization
- **Pre-commit**: Quality gates and security validation
- **Renovate**: Automated dependency updates

## Scalability Considerations

### 1. Device Management

- **Template-Based Configuration**: Reduces duplication and maintenance overhead
- **Bulk Operations**: Automated deployment across multiple devices
- **Offline Handling**: Graceful handling of unreachable devices
- **Recovery Mechanisms**: Fallback hotspots prevent device bricking

### 2. Security Scalability

- **Centralized Credential Management**: Single source of truth in 1Password
- **Automated Validation**: Prevents credential exposure at scale
- **Rotation Automation**: Coordinated updates across all devices
- **Development Safety**: Isolated test environments

### 3. Maintenance Scalability

- **Shared Components**: Changes propagate to all using devices
- **Automated Testing**: Continuous validation of security framework
- **Documentation Integration**: Self-documenting configuration patterns
- **Version Management**: Consistent tool versions across environments
