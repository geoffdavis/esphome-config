# ESPHome Device Configurations

This repository contains YAML configuration files for various ESPHome-based
devices in your home automation setup, with a comprehensive Python security
framework and automated deployment system.

## 📚 Documentation

**Complete documentation is available in the [`docs/`](docs/) directory.**

### Quick Links

- **[📖 Complete Documentation](docs/README.md)** - Main documentation index
- **[🚀 Quick Start Guide](docs/getting-started/quick-start.md)** - Get up and
  running in minutes
- **[🔒 Security Overview](docs/security/overview.md)** - Security framework
  and credential management
- **[🔧 Device Management](docs/device-management/recovery-procedures.md)** -
  Device deployment and recovery
- **[📋 Task Commands](docs/reference/task-commands.md)** - Complete command
  reference

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Enter the dev shell (nix + direnv): installs tools and syncs .venv
direnv allow

# Set up security framework
python3 scripts/setup_security.py

# Configure credentials (choose one)
echo "OP_ACCOUNT=your-1password-account" > .env  # Production
task dev-setup                                   # Development
```

### 2. Deploy Your First Device

```bash
# For ESP32/ESP8266 devices
task upload -- device_name

# For ESP01 devices (memory constrained)
task upload-two-stage -- device_name
```

### 3. Validate Security

```bash
# Run security validation
task security-validate

# Run comprehensive security scan
task security-scan
```

## 🏗️ Project Structure

```text
├── docs/                           # 📚 Complete documentation
│   ├── getting-started/           # 🚀 Setup and first steps
│   ├── security/                  # 🔒 Security framework
│   ├── device-management/         # 🔧 Device operations
│   ├── architecture/              # 🏗️ System design
│   └── reference/                 # 📖 Complete reference
├── .kilocode/rules/memory-bank/   # 🧠 Authoritative technical docs
├── common/                        # 📦 Shared device components
├── scripts/                       # 🔧 Python security framework
├── tests/                         # 🧪 Security framework tests
└── *.yaml                         # 📱 Individual device configurations
```

## 🧠 Memory Bank Integration

This project uses a **Memory Bank** system in
[`.kilocode/rules/memory-bank/`](.kilocode/rules/memory-bank/) that contains
authoritative technical information. The documentation in [`docs/`](docs/)
provides user-friendly guides that link to Memory Bank content rather than
duplicating it.

**Key Memory Bank Files:**

- **[System Architecture](.kilocode/rules/memory-bank/architecture.md)** -
  Complete technical architecture
- **[Common Tasks](.kilocode/rules/memory-bank/tasks.md)** - Detailed workflow procedures
- **[Technology Stack](.kilocode/rules/memory-bank/tech.md)** - Tools and dependencies

## 🔒 Security Features

- **Python Security Framework**: Comprehensive credential validation and management
- **1Password Integration**: Secure credential storage and automated retrieval
- **Automated Validation**: Pre-commit hooks prevent credential exposure
- **Credential Rotation**: Automated rotation with zero-downtime deployment
- **Device Recovery**: Fallback hotspots prevent device bricking

## 🔧 Device Support

### Hardware Platforms

- **ESP32**: Full-featured devices with ample resources
- **ESP8266**: Standard IoT devices (NodeMCU, D1 Mini variants)
- **ESP01**: Memory-constrained devices with two-stage deployment

### Device Types

- **Environmental Sensors**: Temperature, humidity, pressure, air quality
- **Control Devices**: Heat pumps, smart outlets, LED controllers
- **Multi-sensors**: Combined environmental monitoring devices

## 📋 Common Commands

```bash
# List all available tasks
task -l

# Build and deploy single device
task upload -- device_name

# Deploy all devices (handles ESP01 two-stage automatically)
task upload-all-two-stage

# Security operations
task security-validate              # Essential validation
task security-scan                 # Comprehensive scan
task security-rotate-credentials   # Rotate credentials

# Development
task dev-setup                     # Development environment
task test-security                 # Run security tests
```

## 🆘 Need Help?

1. **Getting Started**: See [Quick Start Guide](docs/getting-started/quick-start.md)
2. **Security Issues**: Check [Security Troubleshooting](docs/security/troubleshooting.md)
3. **Device Problems**: Review [Recovery Procedures](docs/device-management/recovery-procedures.md)
4. **Complete Reference**: Browse [Complete Documentation](docs/README.md)

## 🔄 Integration Points

- **Home Assistant**: Encrypted API communication with automatic entity discovery
- **1Password**: Secure credential storage with CLI integration
- **Development Tools**: Nix dev shell via direnv for tool management, Task for automation
- **Quality Assurance**: Pre-commit hooks and comprehensive testing

## 📝 Key Features

### Two-Stage Deployment System

Handles ESP01 devices with 1MB flash memory constraints:

1. **Stage 1**: Deploy minimal firmware with essential connectivity
2. **Stage 2**: Deploy full firmware with all features

### Comprehensive Security Framework

- **Credential Validation**: Real-time format and security checking
- **Exposed Credential Detection**: Prevents known compromised credentials
- **Development Safety**: Safe test credentials for development work
- **Automated Rotation**: Coordinated credential updates across all devices

### Robust Device Management

- **Fallback Hotspots**: Prevent device bricking with recovery access
- **Bulk Operations**: Deploy to multiple devices with offline handling
- **Health Monitoring**: Built-in connectivity and performance tracking

## 📖 Documentation Structure

The documentation follows a layered approach:

1. **[Quick Start](docs/getting-started/quick-start.md)** - Essential setup
   and first deployment
2. **[Topic Guides](docs/)** - User-friendly guides for common operations
3. **[Memory Bank](.kilocode/rules/memory-bank/)** - Complete technical documentation
4. **[Reference](docs/reference/)** - Comprehensive command and troubleshooting reference

This structure eliminates duplication while ensuring both accessibility and completeness.

---

## Legacy Documentation

The following files have been consolidated into the new documentation structure:

- `SECURITY_FRAMEWORK.md` → [`docs/security/overview.md`](docs/security/overview.md)
- `CREDENTIAL_ROTATION_GUIDE.md` → [`docs/security/credential-rotation.md`](docs/security/credential-rotation.md)
- `ESP01_RECOVERY_PLAN.md` → [`docs/device-management/recovery-procedures.md`](docs/device-management/recovery-procedures.md)
- Status reports → [`docs/status/`](docs/status/)

**For complete, up-to-date documentation, use the [`docs/`](docs/) directory.**

---

*This ESPHome configuration project provides a secure, scalable, and
maintainable approach to managing IoT devices with comprehensive documentation
and robust automation.*
