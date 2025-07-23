# Security Framework Overview

This project uses a comprehensive Python-based security framework to protect ESPHome configurations and prevent credential exposure.

## Quick Security Setup

```bash
# Set up security framework
python3 scripts/setup_security.py

# Validate current configuration
task security-validate

# Run comprehensive security scan
task security-scan
```

## Security Architecture

For complete security architecture details, see [System Architecture - Security Architecture](.kilocode/rules/memory-bank/architecture.md#security-architecture).

### Core Components

1. **Python Security Library** ([`scripts/security_lib.py`](../scripts/security_lib.py))
   - Unified security operations
   - Credential validation and generation
   - 1Password integration
   - Secure file handling

2. **Validation Pipeline**
   - Pre-commit hooks for automatic validation
   - Multi-layer credential detection
   - ESPHome-specific pattern matching
   - Known exposed credential detection

3. **Credential Management**
   - 1Password integration for secure storage
   - Automated credential rotation
   - Development environment support
   - Backup and restore capabilities

## Security Features

### Credential Protection
- **API Encryption Keys**: 44-character base64 strings automatically detected
- **OTA Passwords**: 32-character hex strings validated
- **Fallback Hotspot Passwords**: 12-character alphanumeric passwords secured
- **WiFi Credentials**: Protected from hardcoding in configurations

### Automated Validation
- **Pre-commit Hooks**: Prevent credential exposure before commits
- **Security Scanning**: Continuous monitoring for exposed credentials
- **Format Validation**: Ensure credentials meet ESPHome requirements
- **1Password Integration**: Validate vault structure and access

### Development Safety
- **Development Credentials**: Safe test credentials for development work
- **Environment Isolation**: Separate development and production environments
- **Testing Framework**: Comprehensive unit tests for security components

## Common Security Tasks

### Daily Operations
```bash
# Validate secrets and configuration
python3 scripts/validate_secrets.py

# Check 1Password integration
python3 scripts/validate_1password_structure.py

# Run all security tests
task test-security
```

### Credential Management
For detailed credential management procedures, see [Credential Management Tasks](.kilocode/rules/memory-bank/tasks.md#credential-management-tasks).

```bash
# Rotate credentials
python3 scripts/rotate_credentials.py

# Track rotation history
python3 scripts/track_secret_rotation.py status

# Create backup
python3 scripts/backup_secrets.py create
```

### Emergency Procedures
```bash
# Emergency credential rotation
python3 scripts/rotate_credentials.py --emergency

# Deploy with credential rotation
python3 scripts/deploy_with_rotation.py --all

# Recover compromised device
python3 scripts/recover_device.py <device_name>
```

## Integration with Deployment

Security validation is automatically integrated into deployment workflows:

```bash
# These commands include automatic security validation
task upload -- device_name
task upload-all-two-stage
task build-all
```

## 1Password Configuration

### Required Vault Structure

**Automation Vault** - ESPHome Item:
- `api_key`: ESPHome API encryption key (44-char base64)
- `ota_password`: OTA update password (32-char hex)
- `fallback_password`: Fallback hotspot password (12+ char alphanumeric)

**Shared Vault** - Home IoT Item:
- `network name`: WiFi SSID
- `wireless network password`: WiFi password
- `domain name`: Local domain

### Environment Configuration
```bash
# .env file (create this)
OP_ACCOUNT=your-1password-account
```

## Security Patterns

### Detected Patterns
The security framework automatically detects:
- ESPHome API keys: `[A-Za-z0-9+/]{43}=`
- OTA passwords: `\b[a-fA-F0-9]{32}\b`
- Fallback passwords: `\b[A-Za-z0-9]{12}\b`
- Known exposed credentials from this repository

### Allowed Patterns
- ESPHome secret references: `!secret credential_name`
- 1Password CLI commands: `op read "op://vault/item/field"`
- Documentation placeholders: `EXAMPLE_*`, `YOUR_*_HERE`

## Best Practices

### Configuration Files
```yaml
# ✅ Correct - Use secret references
api:
  encryption:
    key: !secret api_key

# ❌ Incorrect - Hardcoded credentials
api:
  encryption:
    key: "actual-api-key-here"  # pragma: allowlist secret
```

### Scripts and Automation
```bash
# ✅ Correct - Use 1Password CLI
API_KEY=$(op read "op://Automation/ESPHome/api_key")

# ❌ Incorrect - Hardcoded credentials
API_KEY="hardcoded-key-here"
```

## Troubleshooting

For security-specific troubleshooting, see [Security Troubleshooting](troubleshooting.md).

### Common Issues
- **1Password CLI Issues**: Authentication and access problems
- **Credential Validation Failures**: Format and security validation errors
- **Pre-commit Hook Failures**: Hook configuration and execution issues

### Debug Mode
```bash
# Enable verbose logging
export ESPHOME_LOGS_LEVEL=DEBUG

# Run with verbose output
python3 scripts/validate_secrets.py --verbose
```

## Related Documentation

- **[Credential Rotation Guide](credential-rotation.md)** - Step-by-step rotation procedures
- **[Security Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Migration Notes](migration-notes.md)** - Historical migration information
- **[Security Framework Details](.kilocode/rules/memory-bank/architecture.md#security-architecture)** - Complete technical architecture

---

*For comprehensive security implementation details, see the [Memory Bank Security Architecture](.kilocode/rules/memory-bank/architecture.md#security-architecture).*
