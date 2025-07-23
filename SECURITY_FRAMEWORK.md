# ESPHome Python Security Framework

A comprehensive, unified security framework for ESPHome configurations that replaces the previous mixed bash/Python approach with a cohesive Python-based solution.

## Overview

This framework provides:
- **Unified Security Library**: Shared components for credential validation, 1Password integration, and security scanning
- **Comprehensive Scripts**: Python scripts for all security operations
- **Automated Testing**: Full unit test coverage with mock support
- **Integration Points**: Task runner and pre-commit hook integration
- **Development Support**: Safe development credentials and testing utilities

## Quick Start

### 1. Initial Setup

```bash
# Set up the security framework
python3 scripts/setup_security.py

# Set up development environment (optional)
python3 scripts/setup_dev_secrets.py
```

### 2. Basic Usage

```bash
# Validate secrets and configuration
task security-validate

# Run comprehensive security scan
task security-scan

# Run unit tests
task test-security
```

## Architecture

### Core Components

#### Security Library (`scripts/security_lib.py`)
The foundation of the framework providing:

- **SecurityLogger**: Consistent logging across all scripts
- **CredentialGenerator**: Secure credential generation
- **CredentialValidator**: Format and security validation
- **OnePasswordManager**: 1Password CLI integration
- **SecureFileHandler**: Safe file operations
- **SecurityScanner**: Exposed credential detection

#### Security Scripts

| Script | Purpose | Replaces |
|--------|---------|----------|
| [`validate_secrets.py`](scripts/validate_secrets.py) | Validate secrets format and security | `validate-secrets.sh` |
| [`validate_1password_structure.py`](scripts/validate_1password_structure.py) | Validate 1Password setup | `validate-1password-structure.sh` |
| [`setup_security.py`](scripts/setup_security.py) | Install and configure security tools | `setup-security.sh` |
| [`rotate_credentials.py`](scripts/rotate_credentials.py) | Automated credential rotation | Enhanced version |
| [`track_secret_rotation.py`](scripts/track_secret_rotation.py) | Track rotation history | New functionality |
| [`setup_dev_secrets.py`](scripts/setup_dev_secrets.py) | Development environment setup | New functionality |
| [`backup_secrets.py`](scripts/backup_secrets.py) | Backup and restore secrets | New functionality |

### Environment Configuration

The framework uses environment variables for configuration:

```bash
# .env file (create this)
OP_ACCOUNT=your-1password-account
```

## Usage Guide

### Daily Operations

#### Validate Configuration
```bash
# Quick validation
python3 scripts/validate_secrets.py

# Comprehensive validation
task security-validate
```

#### Security Scanning
```bash
# Full security scan
task security-scan

# Individual components
python3 scripts/validate_1password_structure.py
```

### Credential Management

#### Credential Rotation
```bash
# Automated rotation process
python3 scripts/rotate_credentials.py

# Track rotation history
python3 scripts/track_secret_rotation.py status
```

#### Backup and Restore
```bash
# Create backup
task security-backup

# List backups
task security-backup-list

# Restore backup
task security-backup-restore -- backup_20240101_120000
```

### Development Workflow

#### Development Setup
```bash
# Set up development environment
python3 scripts/setup_dev_secrets.py

# Use development secrets
cp dev/secrets.yaml secrets.yaml
```

#### Testing
```bash
# Run all tests
python3 tests/run_tests.py

# Run specific test module
python3 tests/run_tests.py --test test_security_lib

# Check test environment
python3 tests/run_tests.py --check-env
```

## Task Integration

The framework integrates with the Task runner:

### Security Tasks
```bash
task security-setup              # Set up security tools
task security-validate           # Essential validation
task security-scan              # Comprehensive scan
task security-validate-1password # 1Password validation
task security-rotate-credentials # Credential rotation
task security-track-rotation    # Rotation tracking
task security-backup           # Create backup
task security-backup-list      # List backups
task security-backup-restore   # Restore backup
```

### Development Tasks
```bash
task dev-setup                  # Development environment
task dev-secrets               # Generate dev secrets
task test-security             # Run unit tests
```

## Pre-commit Integration

The framework provides pre-commit hooks:

```yaml
# Automatic validation on commit
- id: esphome-secrets-validation
- id: esphome-1password-validation
- id: python-security-tests
```

### Manual Hook Execution
```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run esphome-secrets-validation
```

## Configuration

### 1Password Setup

Required 1Password structure:

**Automation Vault**
- Item: "ESPHome"
  - `api_key`: ESPHome API encryption key
  - `ota_password`: OTA update password
  - `fallback_password`: Fallback hotspot password

**Shared Vault**
- Item: "Home IoT"
  - `network name`: WiFi SSID
  - `wireless network password`: WiFi password
  - `domain name`: Local domain

### Environment Variables

```bash
# Required
OP_ACCOUNT=your-1password-account

# Optional
ESPHOME_LOGS_LEVEL=INFO
```

### File Structure

```
├── scripts/
│   ├── security_lib.py              # Core security library
│   ├── validate_secrets.py          # Secrets validation
│   ├── validate_1password_structure.py # 1Password validation
│   ├── setup_security.py            # Security setup
│   ├── rotate_credentials.py        # Credential rotation
│   ├── track_secret_rotation.py     # Rotation tracking
│   ├── setup_dev_secrets.py         # Development setup
│   └── backup_secrets.py            # Backup management
├── tests/
│   ├── test_security_lib.py         # Library tests
│   ├── test_scripts.py              # Script tests
│   ├── test_config.py               # Test utilities
│   └── run_tests.py                 # Test runner
├── dev/                             # Development files
│   ├── secrets.yaml                 # Development secrets
│   └── README.md                    # Development guide
└── backups/                         # Security backups
    └── README.md                    # Backup guide
```

## Security Features

### Credential Validation
- **Format Validation**: Ensures credentials meet ESPHome requirements
- **Exposed Credential Detection**: Identifies known compromised credentials
- **1Password Integration**: Validates 1Password structure and access

### Security Scanning
- **Multi-layer Scanning**: git-secrets, detect-secrets, custom validation
- **File Type Coverage**: YAML, Python, shell scripts, configuration files
- **Continuous Integration**: Pre-commit and Task integration

### Backup and Recovery
- **Automated Backups**: Scheduled and manual backup creation
- **Integrity Verification**: Hash-based backup validation
- **Selective Restoration**: Granular restore capabilities

## Troubleshooting

### Common Issues

#### 1Password CLI Issues
```bash
# Check CLI availability
op account list

# Sign in if needed
op signin

# Verify account access
python3 scripts/validate_1password_structure.py
```

#### Credential Validation Failures
```bash
# Check credential format
python3 scripts/validate_secrets.py

# Generate new credentials
python3 scripts/rotate_credentials.py
```

#### Test Failures
```bash
# Check test environment
python3 tests/run_tests.py --check-env

# Run specific failing test
python3 tests/run_tests.py --test test_security_lib.TestCredentialValidator
```

### Debug Mode

Enable verbose logging:
```bash
# Set environment variable
export ESPHOME_LOGS_LEVEL=DEBUG

# Or use verbose flags
python3 scripts/validate_secrets.py --verbose
```

## Migration from Bash Scripts

### Automatic Migration
The Python scripts are drop-in replacements:

```bash
# Old bash approach
./scripts/validate-secrets.sh

# New Python approach
python3 scripts/validate_secrets.py
```

### Task Integration
Tasks automatically use the new Python scripts:

```bash
# These now use Python scripts internally
task security-validate
task security-scan
```

### Pre-commit Hooks
Pre-commit hooks have been updated to use Python scripts while maintaining backward compatibility.

## Contributing

### Development Setup
```bash
# Set up development environment
python3 scripts/setup_dev_secrets.py

# Run tests
python3 tests/run_tests.py

# Check code style
pre-commit run --all-files
```

### Adding New Features
1. Update the security library if needed
2. Create or modify scripts
3. Add comprehensive tests
4. Update documentation
5. Test integration points

### Testing Guidelines
- All new functionality must have unit tests
- Use the test configuration utilities in `tests/test_config.py`
- Mock external dependencies (1Password CLI, file system)
- Test both success and failure scenarios

## Security Considerations

### Credential Handling
- Never log actual credential values
- Use secure temporary files
- Clean up sensitive data after use
- Validate all inputs

### 1Password Integration
- Use environment variables for account configuration
- Implement proper error handling for CLI failures
- Validate vault and item access before operations

### File Operations
- Use secure file permissions
- Backup before modifications
- Validate file integrity
- Handle concurrent access safely

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run diagnostic commands
3. Review log output
4. Check test results

The framework provides comprehensive logging and error reporting to help diagnose issues quickly.