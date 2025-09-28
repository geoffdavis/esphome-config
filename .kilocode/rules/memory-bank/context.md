# Current Project Context

## Project State Overview

The ESPHome configuration project is in a mature, production-ready state with a comprehensive Python security
framework, automated deployment processes, and a unified documentation system. The system manages dozens of IoT
devices across multiple hardware platforms with centralized credential management and robust security practices.
Recent focus has been on ESP32-C6 platform migration for heat pump controllers, Python 3.13.5 upgrade with
pyproject.toml migration, and Bluetooth proxy integration for enhanced Home Assistant connectivity.

## Recent Major Developments

### Python 3.13.5 and pyproject.toml Migration

- **Status**: Complete and Production-Ready
- **Achievement**: Successfully migrated from requirements.txt to pyproject.toml with Python 3.13.5
- **Impact**: Modern Python dependency management, improved development environment consistency
- **Key Files**: [`pyproject.toml`](pyproject.toml), [`.mise.toml`](.mise.toml) with Python 3.13.5
- **Tools Added**: UV package manager for faster dependency resolution

### ESP32-C6 Heat Pump Platform Expansion

- **Status**: Complete and Production-Ready
- **Achievement**: Successfully migrated both bedroom heat pumps to ESP32-C6 platform
- **Devices**: [`bedroom-east-heatpump.yaml`](bedroom-east-heatpump.yaml), [`bedroom-west-heatpump.yaml`](bedroom-west-heatpump.yaml)
- **Impact**: Eliminated memory constraints, enabled single-stage deployment, improved performance and reliability
- **Key Components**: [`common/heatpump-esp32-nanoc6.yaml`](common/heatpump-esp32-nanoc6.yaml)
- **Documentation**: [`docs/device-management/esp32-nanoc6-deployment-guide.md`](docs/device-management/esp32-nanoc6-deployment-guide.md)

### Bluetooth Proxy Integration

- **Status**: Available and Tested
- **Achievement**: Added Bluetooth LE proxy support for ESP32 devices
- **Impact**: Enhanced Home Assistant device tracking and presence detection
- **Key Components**: [`common/bluetooth-proxy.yaml`](common/bluetooth-proxy.yaml)
- **Features**: Active connections enabled by default, configurable max connections
- **Limitations**: Not compatible with ESP32-C6 heat pump units due to flash constraints

### Comprehensive Documentation System

- **Status**: Complete and Active
- **Achievement**: Unified documentation structure with Memory Bank integration
- **Impact**: Improved user experience, eliminated documentation duplication, clear information hierarchy
- **Key Structure**: [`docs/`](docs/) directory with topic-based organization linking to Memory Bank
- **Documentation**: [`docs/README.md`](docs/README.md), [`docs/DOCUMENTATION_MAINTENANCE.md`](docs/DOCUMENTATION_MAINTENANCE.md)

### Python Security Framework Enhancement

- **Status**: Complete and Enhanced
- **Achievement**: Mature Python security framework with comprehensive testing
- **Impact**: Improved error handling, comprehensive testing, and better 1Password integration
- **Key Files**: [`scripts/security_lib.py`](scripts/security_lib.py), [`scripts/validate_secrets.py`](scripts/validate_secrets.py)
- **Documentation**: [`docs/security/overview.md`](docs/security/overview.md), [`docs/security/migration-notes.md`](docs/security/migration-notes.md)

### Advanced Credential Management System

- **Status**: Production-ready with rotation capabilities
- **Features**: Automated credential rotation, transition mode deployment, backup/restore
- **Key Scripts**: [`scripts/rotate_credentials.py`](scripts/rotate_credentials.py), [`scripts/deploy_with_rotation.py`](scripts/deploy_with_rotation.py), [`scripts/track_secret_rotation.py`](scripts/track_secret_rotation.py)
- **Documentation**: [`docs/status/CREDENTIAL_ROTATION_GUIDE.md`](docs/status/CREDENTIAL_ROTATION_GUIDE.md)

### Device Recovery Framework

- **Status**: Active with comprehensive procedures
- **Purpose**: Handle device recovery scenarios including ESP01 bricking incidents
- **Tools**: [`scripts/recover_device.py`](scripts/recover_device.py), recovery network procedures
- **Documentation**: [`docs/status/ESP01_RECOVERY_PLAN.md`](docs/status/ESP01_RECOVERY_PLAN.md), [`docs/status/ESP01_PHYSICAL_RECOVERY_GUIDE.md`](docs/status/ESP01_PHYSICAL_RECOVERY_GUIDE.md)

### Comprehensive Testing Implementation

- **Status**: Active and Expanded
- **Coverage**: Full unit test suite for security framework components with mock support
- **Framework**: Python unittest with comprehensive test utilities
- **Integration**: Pre-commit hooks run tests automatically
- **Key Files**: [`tests/test_security_lib.py`](tests/test_security_lib.py), [`tests/test_config.py`](tests/test_config.py), [`tests/run_tests.py`](tests/run_tests.py)

### Two-Stage Deployment System

- **Status**: Production-ready with rotation support
- **Purpose**: Handles ESP01 devices with 1MB flash memory constraints
- **Process**: Minimal firmware → Full firmware deployment with credential transition support
- **Automation**: Integrated into Task runner workflows with rotation-aware deployment

## Current Focus Areas

### Platform Migration and Modernization

- **Active**: ESP32-C6 platform adoption for heat pump controllers
- **Achievement**: Both bedroom heat pumps successfully migrated
- **Benefits**: Single-stage deployment, enhanced features, better performance
- **Future**: Consider additional ESP01 to ESP32 migrations where beneficial

### Development Environment Modernization

- **Active**: Python 3.13.5 with modern dependency management
- **Tools**: UV package manager, pyproject.toml configuration
- **Environment**: Mise-managed tool versions with Python virtual environments
- **Automation**: Task runner for all common operations

### Bluetooth and Connectivity Enhancement

- **Active**: Bluetooth LE proxy integration for enhanced Home Assistant connectivity
- **Features**: Active connections, configurable connection limits
- **Integration**: ESP32 devices can serve as Bluetooth proxies
- **Limitations**: Not suitable for memory-constrained devices

### Documentation and Knowledge Management

- **Active**: Unified documentation system with Memory Bank integration
- **Structure**: Topic-based organization with user-friendly guides
- **Integration**: Links to authoritative Memory Bank content without duplication
- **Maintenance**: Automated documentation maintenance guidelines and procedures

### Security and Credential Management

- **Active**: Continuous monitoring for exposed credentials
- **Tools**: Pre-commit hooks with detect-secrets and custom validation
- **1Password Integration**: Fully automated credential retrieval and rotation
- **Validation**: Real-time format checking and security scanning

### Device Fleet Management

- **Scale**: Multiple ESP32, ESP8266, and ESP01 devices
- **Deployment**: Automated bulk operations with offline device handling
- **Monitoring**: Built-in health sensors and connectivity tracking
- **Recovery**: Comprehensive recovery procedures with detailed guides

## Active Device Types

### Environmental Sensors

- **BME280**: Temperature, humidity, pressure monitoring
- **DHT**: Basic temperature and humidity sensors
- **TEMT6000**: Ambient light sensing
- **PIR**: Motion detection
- **Air Quality**: Particulate matter with AQI calculation

### Control Devices

- **Heat Pumps**: Multi-platform climate controllers (ESP01 and ESP32-C6) with specialized packages
- **Smart Outlets**: TopGreener and Sonoff variants
- **LED Controllers**: Music-reactive systems with FFT processing
- **Multi-sensors**: Combined environmental monitoring devices

### Platform Distribution

- **ESP32**: Full-featured devices with ample resources, including ESP32-C6 for heat pump controllers
- **ESP32-C6**: RISC-V based ESP32 variant with enhanced features (M5Stack NanoC6)
- **ESP8266**: Standard IoT devices (NodeMCU, D1 Mini)
- **ESP01**: Memory-constrained devices requiring two-stage deployment

### Bluetooth Integration

- **Bluetooth Proxy**: ESP32 devices serving as BLE proxies for Home Assistant
- **BLE Tracker**: Enhanced device tracking and presence detection
- **Active Connections**: Support for multiple simultaneous Bluetooth connections

## Current Challenges and Solutions

### Memory Constraints

- **Challenge**: ESP01 devices with 1MB flash cannot fit full firmware
- **Solution**: Two-stage deployment system working effectively
- **Status**: Automated through Task runner, handles offline devices gracefully
- **Migration Path**: ESP32-C6 platform available for devices requiring more features

### Platform Compatibility

- **Challenge**: Bluetooth proxy not compatible with ESP32-C6 heat pump units
- **Solution**: Selective feature inclusion based on device capabilities
- **Status**: Clear documentation of platform limitations and capabilities

### Credential Security

- **Challenge**: Preventing credential exposure in version control
- **Solution**: Comprehensive Python security framework with multiple validation layers
- **Status**: Zero exposed credentials, automated scanning active

### Device Recovery

- **Challenge**: Preventing devices from becoming inaccessible
- **Solution**: Fallback hotspot system in all configurations
- **Status**: Proven effective, prevents device bricking

## Development Workflow Status

### Quality Assurance Pipeline

- **Pre-commit Hooks**: Active and comprehensive
- **Security Scanning**: Multi-layer validation (detect-secrets, custom checks)
- **YAML Validation**: Automated linting with relaxed configuration
- **Python Testing**: Full unit test coverage with CI integration

### Deployment Process

- **Single Device**: `task upload -- device_name`
- **Two-Stage**: `task upload-two-stage -- device_name`
- **Bulk Operations**: `task upload-all-two-stage`
- **Security Integration**: Automatic validation before all deployments

### Credential Management

- **Generation**: Automated from 1Password vaults
- **Validation**: Real-time format and security checking
- **Rotation**: Supported with transition modes
- **Development**: Safe test credentials for development work

## Integration Status

### Home Assistant

- **Connection**: Encrypted API communication with all devices
- **Discovery**: Automatic entity registration working
- **Monitoring**: Real-time sensor data and device status
- **Control**: Climate controls and switches fully functional
- **Bluetooth**: BLE proxy integration for enhanced device tracking

### 1Password

- **Authentication**: Environment-based account configuration
- **Vault Structure**: Organized across Automation and Shared vaults
- **Automation**: CLI-based credential retrieval and updates
- **Backup**: Automatic credential history in 1Password

### Development Tools

- **Mise**: Tool version management active with Python 3.13.5
- **Task**: Workflow automation comprehensive
- **UV**: Modern Python package management
- **Renovate**: Dependency updates automated
- **Git**: Security hooks and validation active

## Maintenance Activities

### Regular Operations

- **Security Validation**: Runs automatically on every commit
- **Credential Rotation**: Supported with documented procedures
- **Device Updates**: OTA updates working reliably
- **Backup Management**: Automated backup creation and restoration

### Monitoring and Health

- **Device Status**: WiFi signal strength and uptime tracking
- **Security Health**: Continuous credential exposure monitoring
- **Build Status**: Compilation and deployment success tracking
- **Test Results**: Security framework validation results

## Next Steps and Priorities

### Immediate Focus

- **Platform Optimization**: Continue ESP32-C6 platform refinement and optimization
- **Bluetooth Integration**: Expand Bluetooth proxy deployment to suitable ESP32 devices
- **Documentation Maintenance**: Keep unified documentation current with Memory Bank integration
- **Testing**: Maintain comprehensive test coverage for security framework
- **Monitoring**: Continue device health and security monitoring

### Future Enhancements

- **Platform Migration Strategy**: Develop systematic approach for additional ESP01 to ESP32 migrations
- **Bluetooth Expansion**: Evaluate Bluetooth proxy deployment across suitable devices
- **Documentation Automation**: Further automate documentation maintenance and validation
- **Device Templates**: Expand common component library with ESP32-C6 and Bluetooth variants
- **Monitoring**: Enhanced device health and performance tracking
- **Security**: Continue improving credential management and validation

## Known Issues and Workarounds

### ESP01 Memory Limitations

- **Issue**: 1MB flash requires careful firmware management
- **Workaround**: Two-stage deployment system handles this automatically
- **Status**: Working solution, no manual intervention required
- **Migration Path**: ESP32-C6 platform available for feature-rich deployments

### Bluetooth Proxy Compatibility

- **Issue**: Bluetooth proxy not compatible with ESP32-C6 heat pump units due to flash constraints
- **Workaround**: Selective feature inclusion based on device capabilities
- **Status**: Documented limitation, clear guidance provided

### Offline Device Handling

- **Issue**: Devices may be unreachable during deployment
- **Workaround**: Graceful skipping with clear status reporting
- **Status**: Automated handling in place, no manual intervention needed

### Development Environment Setup

- **Issue**: Initial setup requires multiple tools and configurations
- **Workaround**: Comprehensive setup scripts and documentation
- **Status**: Well-documented process, setup scripts available

## Project Health Indicators

### Security Posture

- ✅ Zero exposed credentials in version control
- ✅ Automated security scanning active
- ✅ Comprehensive credential validation
- ✅ 1Password integration working

### Operational Status

- ✅ All device types deploying successfully
- ✅ Two-stage deployment working for ESP01 devices
- ✅ ESP32-C6 platform migration successful
- ✅ Bulk operations handling offline devices gracefully
- ✅ Recovery mechanisms preventing device bricking

### Development Workflow

- ✅ Single-command deployment for all device types
- ✅ Modern Python 3.13.5 development environment
- ✅ Comprehensive documentation and troubleshooting guides
- ✅ Safe development environment with test credentials
- ✅ Automated quality assurance pipeline

### Platform Capabilities

- ✅ ESP32-C6 platform fully operational
- ✅ Bluetooth proxy integration available
- ✅ Single-stage deployment for capable devices
- ✅ Memory-constrained device support maintained
