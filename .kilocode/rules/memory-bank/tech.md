# Technology Stack

## Core Technologies

### ESPHome Framework

- **Version**: Latest (managed via requirements.txt)
- **Purpose**: Primary IoT device firmware framework
- **Language**: YAML configuration with C++ extensions
- **Features**:
  - Over-the-air updates
  - Home Assistant integration
  - Web server interface
  - Sensor and actuator support

### Hardware Platforms

- **ESP32**: Full-featured microcontroller with WiFi/Bluetooth
- **ESP32-C6**: RISC-V based ESP32 variant with enhanced features (M5Stack NanoC6)
  - **Board**: esp32-c6-devkitc-1 compatible
  - **Flash**: 4MB (significant upgrade from ESP01's 1MB)
  - **Framework**: ESP-IDF
  - **Features**: Native USB, improved WiFi performance, more GPIO pins
- **ESP8266**: WiFi-enabled microcontroller (NodeMCU, D1 Mini variants)
- **ESP01**: Memory-constrained ESP8266 variant (1MB flash)

### Programming Languages

- **Python 3.11**: Security framework and automation scripts
- **YAML**: Device configuration and shared components
- **C++**: Custom components and sensor libraries
- **Bash**: Legacy scripts and system integration

## Development Environment

### Tool Version Management

**Mise** ([`.mise.toml`](.mise.toml))

```toml
[tools]
python = "3.11"
task = "latest"
nodejs = "22.13.0"

[env]
_.python.venv = { path = ".venv", create = true }
```

### Task Automation

**Task Runner** ([`Taskfile.yml`](Taskfile.yml))

- Build automation for device firmware
- Security validation workflows
- Deployment orchestration
- Development environment setup

### Dependency Management

- **Python**: [`requirements.txt`](requirements.txt) - ESPHome core
- **Node.js**: [`package.json`](package.json) - Renovate for dependency updates
- **System**: Mise manages tool versions consistently

## Security Framework

### Python Security Library

**Core Components** ([`scripts/security_lib.py`](scripts/security_lib.py)):

- `SecurityLogger`: Colored logging with structured output
- `CredentialGenerator`: Secure credential generation
- `CredentialValidator`: Format and security validation
- `OnePasswordManager`: 1Password CLI integration
- `SecureFileHandler`: Safe file operations
- `SecurityScanner`: Exposed credential detection

### Security Scripts

| Script | Purpose | Technology |
|--------|---------|------------|
| [`validate_secrets.py`](scripts/validate_secrets.py) | Credential validation | Python 3.11 |
| [`validate_1password_structure.py`](scripts/validate_1password_structure.py) | 1Password integration | Python 3.11 |
| [`setup_security.py`](scripts/setup_security.py) | Security tool installation | Python 3.11 |
| [`rotate_credentials.py`](scripts/rotate_credentials.py) | Automated credential rotation | Python 3.11 |
| [`deploy_with_rotation.py`](scripts/deploy_with_rotation.py) | Deployment with rotation | Python 3.11 |
| [`recover_device.py`](scripts/recover_device.py) | Device recovery procedures | Python 3.11 |
| [`track_secret_rotation.py`](scripts/track_secret_rotation.py) | Rotation history tracking | Python 3.11 |
| [`backup_secrets.py`](scripts/backup_secrets.py) | Backup management | Python 3.11 |
| [`setup_dev_secrets.py`](scripts/setup_dev_secrets.py) | Development environment | Python 3.11 |

### Testing Framework

**Unit Testing** ([`tests/`](tests/)):

- **Framework**: Python unittest
- **Coverage**: Security library components
- **Mocking**: 1Password CLI and file system operations
- **Runner**: [`run_tests.py`](tests/run_tests.py) with environment validation

## Quality Assurance

### Pre-commit Hooks

**Configuration** ([`.pre-commit-config.yaml`](.pre-commit-config.yaml)):

- **detect-secrets**: Exposed credential detection
- **yamllint**: YAML format validation
- **Python security validation**: Custom ESPHome checks
- **Standard hooks**: File size, merge conflicts, trailing whitespace

### Code Quality Tools

- **YAML Linting**: yamllint with relaxed configuration
- **Python Testing**: unittest with mock support
- **Security Scanning**: Multi-layer credential detection
- **Git Integration**: Pre-commit and git-secrets

## External Integrations

### 1Password

- **CLI Version**: Latest (installed via security setup)
- **Authentication**: Account-based with environment variables
- **Vault Structure**:
  - Automation vault (ESPHome credentials)
  - Shared vault (WiFi and network credentials)
- **Field Mapping**: Structured credential organization

### Home Assistant

- **Integration**: ESPHome native integration
- **Communication**: Encrypted API with rotating keys
- **Discovery**: Automatic entity registration
- **Protocol**: TCP/IP over WiFi with fallback hotspot

### Development Tools

- **Git**: Version control with security hooks
- **Renovate**: Automated dependency updates
- **1Password CLI**: Secure credential management
- **ESPHome CLI**: Device compilation and deployment

## Custom Components

### Music-Reactive LEDs

**Location**: [`custom_components/esphome-music-leds/`](custom_components/esphome-music-leds/)

- **Language**: C++ with Python ESPHome integration
- **Features**: FFT processing, visual effects, Gaussian filtering
- **Files**:
  - [`__init__.py`](custom_components/esphome-music-leds/__init__.py): ESPHome component definition
  - [`esphome_music_leds.cpp/.h`](custom_components/esphome-music-leds/esphome_music_leds.h): Main component
  - [`FFT.cpp/.h`](custom_components/esphome-music-leds/FFT.h): Fast Fourier Transform
  - [`VisualEffect.cpp/.h`](custom_components/esphome-music-leds/VisualEffect.h): LED effects

### Air Quality Index Calculation

**Location**: [`include/aqipm.h`](include/aqipm.h)

- **Language**: C++
- **Purpose**: Calculate AQI from particulate matter readings
- **Standards**: EPA AQI calculation for PM2.5 and PM10
- **Integration**: Used in air quality sensor devices

## Configuration Architecture

### YAML Structure

- **Device Files**: Individual device configurations
- **Common Components**: Shared templates and packages
- **Substitutions**: Device-specific parameter injection
- **Includes**: Hierarchical configuration composition

### Package System

**Full Packages** ([`common/packages-full.yaml`](common/packages-full.yaml)):

- Complete feature set for capable devices
- Full WiFi configuration with web server
- All sensors and monitoring capabilities

**Minimal Packages** ([`common/packages-minimal.yaml`](common/packages-minimal.yaml)):

- Reduced feature set for memory-constrained devices
- Basic connectivity with recovery capabilities
- Essential sensors only

## Deployment Technologies

### Two-Stage Deployment

**Stage 1 - Minimal**:

- Basic WiFi connectivity
- OTA capability
- Recovery hotspot
- Minimal memory footprint

**Stage 2 - Full**:

- Complete feature set
- Web server interface
- All configured sensors
- IPv6 support

### Build Process

1. **Validation**: Security checks and credential validation
2. **Compilation**: ESPHome firmware generation
3. **Upload**: OTA or serial deployment
4. **Verification**: Device connectivity and functionality

## Environment Configuration

### Development Setup

```bash
# Tool installation
mise install

# Security framework setup
python3 scripts/setup_security.py

# Development credentials
python3 scripts/setup_dev_secrets.py
```

### Environment Variables

- **OP_ACCOUNT**: 1Password account identifier
- **ESPHOME_LOGS_LEVEL**: Logging verbosity (INFO, DEBUG)
- **Python Virtual Environment**: Managed by Mise

### File Structure

```text
├── .mise.toml              # Tool version management
├── Taskfile.yml            # Build automation
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
├── .pre-commit-config.yaml # Quality assurance
├── .gitignore             # Version control exclusions
└── .env                   # Environment configuration
```

## Performance Considerations

### Memory Management

- **ESP01 Constraints**: 1MB flash, limited RAM
- **Two-stage deployment**: Minimal → Full upgrade path
- **Component optimization**: Selective feature inclusion

### Network Efficiency

- **OTA Updates**: Differential firmware updates
- **API Communication**: Encrypted but lightweight
- **Fallback Mechanisms**: Hotspot recovery without full reset

### Build Optimization

- **Parallel Builds**: Task-based concurrent compilation
- **Incremental Updates**: Only changed devices
- **Offline Handling**: Graceful skipping of unreachable devices

## Security Technologies

### Cryptographic Standards

- **API Keys**: 32-byte base64-encoded (256-bit)
- **OTA Passwords**: 32-character hexadecimal (128-bit)
- **Fallback Passwords**: 12+ character alphanumeric
- **WiFi Security**: WPA2/WPA3 with strong passwords

### Validation Patterns

- **Regex Validation**: Format compliance checking
- **Exposed Credential Detection**: Known compromise identification
- **1Password Integration**: Secure storage validation
- **Pre-commit Scanning**: Continuous security monitoring

## Monitoring and Observability

### Built-in Sensors

- **WiFi Signal Strength**: Connection quality monitoring
- **Uptime Tracking**: Device reliability metrics
- **Connection Status**: Network connectivity indicators
- **Device Health**: Temperature and performance monitoring

### Logging

- **ESPHome Logs**: Device-level debugging and monitoring
- **Security Logs**: Credential validation and rotation tracking
- **Build Logs**: Compilation and deployment status
- **Test Logs**: Security framework validation results
