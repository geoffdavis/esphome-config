# Credential Rotation Guide

This guide provides comprehensive procedures for rotating ESPHome credentials using the automated Python security framework.

## When to Rotate Credentials

### Immediate Rotation Required

- **Credential Exposure**: Any credential found in public repositories or logs
- **Security Breach**: Suspected unauthorized access to devices or systems
- **Team Changes**: When team members with credential access leave

### Scheduled Rotation

- **API Keys**: Every 90 days
- **OTA Passwords**: Every 90 days
- **Fallback Passwords**: Every 180 days
- **WiFi Credentials**: As needed or after exposure

## Quick Rotation Process

For detailed rotation procedures, see [Credential Rotation Tasks](.kilocode/rules/memory-bank/tasks.md#credential-rotation).

### Automated Rotation

```bash
# Run automated credential rotation
python3 scripts/rotate_credentials.py

# Deploy with rotation support (handles transition)
python3 scripts/deploy_with_rotation.py --all

# Track rotation completion
python3 scripts/track_secret_rotation.py add
```

### Manual Verification

```bash
# Validate new credentials
task security-validate

# Test device connectivity
ping device-name.local

# Verify Home Assistant integration
# Check devices appear and respond in HA
```

## Rotation Process Overview

The rotation process uses a **two-stage deployment** to ensure zero-downtime updates:

1. **Stage 1**: Deploy new credentials using old credentials for authentication
2. **Stage 2**: Final deployment using only new credentials

### Stage 1: Transition Deployment

```bash
# Generate new credentials in 1Password
python3 scripts/rotate_credentials.py

# Deploy using transition mode (old + new credentials)
python3 scripts/deploy_with_rotation.py --stage transition
```

### Stage 2: Final Deployment

```bash
# Switch to new credentials only
python3 scripts/deploy_with_rotation.py --stage final

# Verify all devices accessible
python3 scripts/deploy_with_rotation.py --verify
```

## Credential Types

### API Encryption Keys

- **Format**: 44-character base64 string ending with `=`
- **Purpose**: Encrypts communication between Home Assistant and devices
- **Generation**: `openssl rand -base64 32`

### OTA Passwords

- **Format**: 32-character hexadecimal string
- **Purpose**: Secures over-the-air firmware updates
- **Generation**: `openssl rand -hex 16`

### Fallback Hotspot Passwords

- **Format**: 12+ character alphanumeric string
- **Purpose**: Device recovery access when WiFi fails
- **Generation**: `openssl rand -base64 12 | tr -d "=+/" | cut -c1-12`

## Device-Specific Considerations

### ESP01 Devices (Memory Constrained)

ESP01 devices require special handling due to 1MB flash memory limitations:

```bash
# Use two-stage deployment for ESP01 devices
task upload-two-stage -- device_name

# Or use rotation-aware deployment
python3 scripts/deploy_with_rotation.py --device device_name --two-stage
```

### ESP32/ESP8266 Devices

Standard devices can handle direct credential updates:

```bash
# Direct deployment for capable devices
task upload -- device_name

# Or use rotation deployment
python3 scripts/deploy_with_rotation.py --device device_name
```

## Backup and Recovery

### Create Backup Before Rotation

```bash
# Create backup of current credentials
python3 scripts/backup_secrets.py create

# List available backups
python3 scripts/backup_secrets.py list
```

### Emergency Rollback
If rotation fails and devices become inaccessible:

```bash
# Restore from backup
python3 scripts/backup_secrets.py restore <backup_id>

# Deploy restored credentials
python3 scripts/deploy_with_rotation.py --emergency
```

## Troubleshooting Rotation Issues

### Device Not Responding After Rotation

**1. Check Network Connectivity**

```bash
# Test basic connectivity
ping device-name.local

# Check device appears in network
nmap -sn 192.168.1.0/24 | grep device-name
```

**2. Try Fallback Hotspot Access**

- Power cycle the device to trigger fallback mode
- Look for WiFi network: `[Device Name] ESP`
- Connect using **old** fallback password initially
- Access device at `http://192.168.4.1`
- Upload new firmware via web interface

**3. Physical Recovery (ESP01 devices)**
For completely unresponsive ESP01 devices, see [Recovery Procedures](../device-management/recovery-procedures.md#esp01-physical-recovery).

### 1Password Integration Issues

**Authentication Problems**

```bash
# Re-authenticate with 1Password
op signin

# Verify account access
op account list

# Test credential retrieval
op read "op://Automation/ESPHome/api_key"
```

**Vault Structure Issues**

```bash
# Validate 1Password structure
python3 scripts/validate_1password_structure.py

# Check required items exist
op item get "ESPHome" --vault="Automation"
op item get "Home IoT" --vault="Shared"
```

### Deployment Failures

**Offline Devices**

```bash
# Deploy only to online devices
python3 scripts/deploy_with_rotation.py --online-only

# Handle offline devices separately when they come online
python3 scripts/deploy_with_rotation.py --device offline_device_name
```

**Partial Deployment Success**

```bash
# Check deployment status
python3 scripts/deploy_with_rotation.py --status

# Retry failed devices
python3 scripts/deploy_with_rotation.py --retry-failed
```

## Security Validation

### Pre-Rotation Checks

```bash
# Validate current security state
task security-validate

# Check for exposed credentials
task security-scan

# Verify 1Password access
python3 scripts/validate_1password_structure.py
```

### Post-Rotation Validation

```bash
# Verify new credentials are active
task security-validate

# Test device connectivity
python3 scripts/deploy_with_rotation.py --verify

# Check security hooks detect old credentials
echo 'api_key: "old-exposed-key"' | .githooks/esphome_credential_check.py  # pragma: allowlist secret
```

## Rotation Tracking

### Track Rotation Events

```bash
# Add rotation entry
python3 scripts/track_secret_rotation.py add

# View rotation history
python3 scripts/track_secret_rotation.py status

# Generate rotation report
python3 scripts/track_secret_rotation.py report
```

### Documentation Updates
After successful rotation:

1. Update any documentation referencing old credentials
2. Update security baseline if using detect-secrets
3. Document any issues encountered for future reference
4. Verify all team members are aware of the rotation

## Integration with Existing Workflows

### Task Runner Integration

```bash
# Security validation runs automatically with these tasks
task upload -- device_name
task upload-all-two-stage
task build-all
```

### Pre-commit Hook Integration
The rotation process integrates with pre-commit hooks to prevent old credential exposure:

```bash
# Hooks automatically detect old exposed credentials
git commit -m "Update configuration"
# Will fail if old credentials are detected
```

## Best Practices

### Planning

- **Schedule rotations** during maintenance windows
- **Notify team members** before rotation
- **Test rotation process** in development environment first
- **Have rollback plan** ready

### Execution

- **Create backups** before starting rotation
- **Monitor device connectivity** throughout process
- **Verify each stage** before proceeding
- **Document any issues** encountered

### Post-Rotation

- **Verify all devices** are accessible and functional
- **Update documentation** as needed
- **Schedule next rotation** based on policy
- **Review and improve** rotation procedures

## Related Documentation

- **[Security Overview](overview.md)** - Complete security framework information
- **[Security Troubleshooting](troubleshooting.md)** - Common security issues
- **[Recovery Procedures](../device-management/recovery-procedures.md)** - Device recovery methods
- **[Credential Management Tasks](.kilocode/rules/memory-bank/tasks.md#credential-rotation)** - Detailed technical procedures

---

*For comprehensive credential rotation implementation details, see [Credential Management Tasks](.kilocode/rules/memory-bank/tasks.md#credential-rotation) in the Memory Bank.*
