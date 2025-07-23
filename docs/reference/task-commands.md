# Task Commands Reference

This reference provides a complete list of all available Task runner commands for the ESPHome configuration project.

## Quick Reference

```bash
# List all available tasks
task -l

# Get help for a specific task
task --help <task-name>
```

## Build Commands

### Single Device Build
```bash
# Build firmware for a specific device
task build -- <device-name>

# Examples
task build -- den_multisensor
task build -- attic_sensor
```

### Bulk Build Operations
```bash
# Build firmware for all devices
task build-all

# Clean build files for a device
task clean -- <device-name>

# Clean all build files
task clean-all
```

## Deployment Commands

### Single Device Deployment
```bash
# Upload firmware to a device (includes build)
task upload -- <device-name>

# Examples
task upload -- den_multisensor
task upload -- bedroom_east_multisensor
```

### Two-Stage Deployment (ESP01 Devices)
```bash
# Two-stage deployment for memory-constrained devices
task upload-two-stage -- <device-name>

# Examples
task upload-two-stage -- attic_sensor
task upload-two-stage -- bedroom_east_heatpump
```

### Bulk Deployment Operations
```bash
# Upload to all devices using two-stage process
task upload-all-two-stage

# Upload to all standard devices (non-ESP01)
task upload-all
```

## Security Commands

### Basic Security Operations
```bash
# Essential security validation
task security-validate

# Comprehensive security scan
task security-scan

# Set up security framework
task security-setup
```

### Advanced Security Operations
```bash
# Validate 1Password integration
task security-validate-1password

# Rotate credentials
task security-rotate-credentials

# Track credential rotation
task security-track-rotation

# Create security backup
task security-backup

# List security backups
task security-backup-list

# Restore from backup
task security-backup-restore -- <backup-id>
```

## Development Commands

### Development Environment
```bash
# Set up development environment
task dev-setup

# Generate development secrets
task dev-secrets

# Set up development credentials
task dev-credentials
```

### Testing Commands
```bash
# Run security framework tests
task test-security

# Run all tests
task test-all

# Run specific test suite
task test -- <test-name>
```

## Credential Management

### Secret Generation
```bash
# Generate secrets from 1Password
task secrets

# Validate secrets format
task secrets-validate

# Generate development secrets
task secrets-dev
```

### Credential Operations
```bash
# Rotate all credentials
task rotate-credentials

# Backup current credentials
task backup-credentials

# Restore credentials from backup
task restore-credentials -- <backup-id>
```

## Maintenance Commands

### Project Maintenance

```bash
# Update project dependencies
task update-deps

# Clean temporary files
task clean-temp

# Validate project configuration
task validate-config
```

### Tool Management

```bash
# Update development tools
task update-tools

# Check tool versions
task check-tools

# Install missing tools
task install-tools
```

## Device-Specific Commands

### ESP01 Device Commands

```bash
# Deploy minimal firmware first, then full
task upload-two-stage -- <esp01-device>

# Examples for ESP01 devices
task upload-two-stage -- attic_sensor
task upload-two-stage -- bedroom_east_heatpump
task upload-two-stage -- denheatpump
```

### ESP32/ESP8266 Device Commands

```bash
# Direct deployment for capable devices
task upload -- <device-name>

# Examples for ESP32/ESP8266 devices
task upload -- den_multisensor
task upload -- bedroom_east_multisensor
task upload -- particle_man
```

## Recovery Commands

### Device Recovery

```bash
# Recover specific device
task recover-device -- <device-name>

# Recover all offline devices
task recover-all

# Emergency recovery mode
task emergency-recovery -- <device-name>
```

### Network Recovery

```bash
# Set up recovery network
task setup-recovery-network

# Deploy via recovery network
task deploy-recovery -- <device-name>
```

## Monitoring Commands

### Device Status

```bash
# Check device connectivity
task check-devices

# Monitor device health
task monitor-devices

# Get device information
task device-info -- <device-name>
```

### System Status

```bash
# Check system health
task health-check

# Validate all configurations
task validate-all

# System diagnostics
task diagnostics
```

## Advanced Usage

### Command Chaining

```bash
# Chain multiple operations
task security-validate && task build-all && task upload-all-two-stage

# Conditional execution
task build -- device_name && task upload -- device_name
```

### Environment Variables

```bash
# Set log level
ESPHOME_LOGS_LEVEL=DEBUG task upload -- device_name

# Use specific 1Password account
OP_ACCOUNT=work task security-validate

# Development mode
DEV_MODE=true task dev-setup
```

### Parallel Operations

```bash
# Build multiple devices in parallel (if supported)
task build -- device1 & task build -- device2 & wait

# Note: Use with caution to avoid resource conflicts
```

## Task Categories

### Essential Daily Tasks

```bash
task security-validate    # Before any deployment
task upload -- device     # Deploy single device
task upload-all-two-stage  # Deploy all devices
task security-scan        # Regular security check
```

### Weekly Maintenance Tasks

```bash
task update-deps          # Update dependencies
task backup-credentials   # Backup current state
task health-check         # System health validation
task clean-temp           # Clean temporary files
```

### Emergency Tasks

```bash
task emergency-recovery   # Device recovery
task security-backup     # Emergency backup
task restore-credentials # Restore from backup
task diagnostics         # System diagnostics
```

## Task Configuration

### Taskfile Location

The task definitions are in [`Taskfile.yml`](../Taskfile.yml) in the project root.

### Custom Task Variables

```bash
# Override default device
DEVICE=custom_device task upload

# Use different esphome binary
ESPHOME_BIN=/custom/path/esphome task build -- device
```

### Task Dependencies

Many tasks have automatic dependencies:

- `upload` tasks automatically run `build` first
- `security-validate` runs before deployment tasks
- `dev-setup` includes credential generation

## Integration with Memory Bank

For detailed task procedures and workflows, see [Common Tasks](.kilocode/rules/memory-bank/tasks.md) in the Memory Bank.

### Task Categories in Memory Bank

- **[Device Management Tasks](.kilocode/rules/memory-bank/tasks.md#device-management-tasks)**
- **[Security Management Tasks](.kilocode/rules/memory-bank/tasks.md#security-management-tasks)**
- **[Development Environment Tasks](.kilocode/rules/memory-bank/tasks.md#development-environment-tasks)**
- **[Maintenance Tasks](.kilocode/rules/memory-bank/tasks.md#maintenance-tasks)**

## Troubleshooting Task Issues

### Common Task Failures

```bash
# Task not found
task -l  # List available tasks

# Permission denied
chmod +x Taskfile.yml

# Missing dependencies
task install-tools
```

### Debug Mode

```bash
# Verbose task execution
task --verbose <task-name>

# Dry run (if supported)
task --dry-run <task-name>
```

### Environment Issues

```bash
# Check environment
task check-tools

# Verify mise environment
mise doctor

# Check Python environment
python3 --version
```

## Related Documentation

- **[Quick Start Guide](../getting-started/quick-start.md)** - Essential commands for getting started
- **[Development Setup](../getting-started/development-setup.md)** - Setting up the task environment
- **[Common Tasks](.kilocode/rules/memory-bank/tasks.md)** - Detailed task procedures in Memory Bank
- **[Troubleshooting](troubleshooting.md)** - General troubleshooting guide

---

*For detailed task implementation and workflows, see [Common Tasks](.kilocode/rules/memory-bank/tasks.md) in the Memory Bank.*
