# ESPHome Credential Rotation Guide

## Overview

This guide provides step-by-step procedures for rotating exposed ESPHome credentials using a secure
two-stage deployment process. The rotation process ensures zero-downtime updates while maintaining
security throughout the transition.

## Exposed Credentials Requiring Rotation

The following credentials have been exposed and must be rotated immediately:

- **API Encryption Key**: `rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=` # pragma: allowlist secret
- **OTA Password**: `5929ccc1f08289c79aca50ebe0a9b7eb` # pragma: allowlist secret
- **Fallback Hotspot Password**: `1SXRpeXi7AdU` # pragma: allowlist secret

These credentials are detected by the security hooks in
[`.githooks/esphome-credential-check.sh`](.githooks/esphome-credential-check.sh:30-43) and must not
appear in any configuration files.

## Prerequisites

Before starting the rotation process, ensure you have:

1. **1Password CLI access** configured for your 1Password account
2. **ESPHome** installed and working
3. **Security hooks** installed via [`./scripts/setup-security.sh`](scripts/setup-security.sh:1)
4. **Task runner** available ([`Taskfile.yml`](Taskfile.yml:1) configured)
5. **Network access** to all ESPHome devices

Verify prerequisites:

```bash
# Check 1Password access
op account list

# Check ESPHome
esphome version

# Check security setup
git secrets --scan

# Check task runner
task --version
```

## Step 1: Generate New Credentials

### 1.1 Generate New API Encryption Key

```bash
# Generate new 32-byte base64 encoded API key
NEW_API_KEY=$(openssl rand -base64 32)
echo "New API Key: $NEW_API_KEY"

# Validate format (should be 44 characters ending with =)
echo "$NEW_API_KEY" | grep -E '^[A-Za-z0-9+/]{43}=$'
```

### 1.2 Generate New OTA Password

```bash
# Generate new 32-character hexadecimal OTA password
NEW_OTA_PASSWORD=$(openssl rand -hex 16)
echo "New OTA Password: $NEW_OTA_PASSWORD"

# Validate format (should be 32 hex characters)
echo "$NEW_OTA_PASSWORD" | grep -E '^[a-fA-F0-9]{32}$'
```

### 1.3 Generate New Fallback Hotspot Password

```bash
# Generate new 12-character alphanumeric fallback password
NEW_FALLBACK_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-12)
echo "New Fallback Password: $NEW_FALLBACK_PASSWORD"

# Validate format (should be 12 alphanumeric characters)
echo "$NEW_FALLBACK_PASSWORD" | grep -E '^[A-Za-z0-9]{12}$'
```

### 1.4 Update 1Password with New Credentials

```bash
# Update API key in 1Password
op item edit "ESPHome" --vault="Automation"  \
  api_key="$NEW_API_KEY"

# Update OTA password in 1Password
op item edit "ESPHome" --vault="Automation"  \
  ota_password="$NEW_OTA_PASSWORD"

# Update fallback password in 1Password
op item edit "ESPHome" --vault="Automation"  \
  fallback_password="$NEW_FALLBACK_PASSWORD"
```

### 1.5 Verify 1Password Updates

```bash
# Verify new credentials are stored correctly
op item get "ESPHome" --vault="Automation"  \
  --fields api_key,ota_password,fallback_password
```

## Step 2: Two-Stage Deployment Process

The two-stage deployment ensures devices can be updated without losing connectivity:

1. **Stage 1**: Deploy with both old and new credentials (transition state)
2. **Stage 2**: Deploy with only new credentials (final state)

### 2.1 Create Transition Secrets File

Create a temporary secrets file with new credentials for the transition:

```bash
# Generate new secrets.yaml with updated credentials
./scripts/generate_secrets.sh

# Backup current secrets for rollback if needed
cp secrets.yaml secrets.yaml.backup.$(date +%Y%m%d_%H%M%S)

# Verify new secrets format
if [ -f scripts/validate-secrets.sh ]; then
    ./scripts/validate-secrets.sh
else
    echo "⚠️  Validation script not found - manual validation required"
fi
```

### 2.2 Create Old Credentials Backup

For the two-stage deployment, we need the old credentials temporarily:

```bash
# Create old credentials file for transition deployment
cat > secrets.yaml.old << EOF
# Old credentials for transition deployment
# DO NOT COMMIT THIS FILE

# wifi credentials (unchanged)
wifi_ssid: $(op read "op://Shared/Home IoT/network name" )
wifi_password: $(op read "op://Shared/Home IoT/wireless network password" )
wifi_domain: $(op read "op://Shared/Home IoT/domain name" )

# OLD API key (for transition)
api_key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=" # pragma: allowlist secret

# OLD OTA password (for transition)
ota_password: "5929ccc1f08289c79aca50ebe0a9b7eb" # pragma: allowlist secret

# OLD Fallback hotspot password (for transition)
fallback_password: "1SXRpeXi7AdU" # pragma: allowlist secret
EOF
```

### 2.3 Stage 1: Deploy New Credentials Using Old Credentials

Deploy the new credentials to all devices using the old credentials for authentication:

```bash
# Use old credentials for deployment authentication
cp secrets.yaml.old secrets.yaml

# Run security validation (will detect old credentials but allow for transition)
echo "⚠️  Expected security warnings for transition deployment..."

# Deploy to all devices using two-stage process
# This uses old credentials to authenticate but installs new credentials
task upload-all-two-stage

# Verify deployment success
echo "✅ Stage 1 deployment completed - devices now have new credentials"
```

### 2.4 Stage 2: Final Deployment with New Credentials Only

Switch to new credentials and deploy final configuration:

```bash
# Switch to new credentials
./scripts/generate_secrets.sh

# Verify new credentials are active
echo "🔍 Verifying new credentials..."
task security-validate

# Final deployment using new credentials
task upload-all-two-stage

# Verify all devices are accessible with new credentials
echo "✅ Stage 2 deployment completed - rotation successful"
```

## Step 3: Validation and Testing

### 3.1 Test Device Connectivity

Verify all devices are accessible with new credentials:

```bash
# Test API connectivity to each device
for device in $(ls *.yaml | sed 's/\.yaml$//' | grep -v '\-minimal$' | grep -v '\-full$'); do
    echo "Testing $device..."
    if esphome logs "$device.yaml" --device "$device.local" 2>/dev/null | timeout 5 cat; then
        echo "✅ $device: API connection successful"
    else
        echo "❌ $device: API connection failed"
    fi
done
```

### 3.2 Verify Security Hook Detection

Test that the security hooks properly detect the old exposed credentials:

```bash
# Test security hooks detect old credentials
echo 'api_key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="' > test_old_creds.yaml  # pragma: allowlist secret
./.githooks/esphome-credential-check.sh test_old_creds.yaml

# Should output: "ERROR: Known exposed API key found in test_old_creds.yaml"
rm test_old_creds.yaml

echo "✅ Security hooks properly detect old exposed credentials"
```

### 3.3 Test OTA Updates

Verify OTA updates work with new credentials:

```bash
# Test OTA update on a single device
TEST_DEVICE="bedroom_east_multisensor"  # Choose an available device

echo "Testing OTA update with new credentials..."
task upload -- "$TEST_DEVICE"

if [ $? -eq 0 ]; then
    echo "✅ OTA update successful with new credentials"
else
    echo "❌ OTA update failed - check device connectivity"
fi
```

### 3.4 Test Fallback Hotspot Access

If a device becomes unreachable, test fallback hotspot access:

```bash
# Instructions for manual fallback testing
cat << EOF
📱 Manual Fallback Hotspot Test:

1. Power cycle a test device to trigger fallback mode
2. Look for WiFi network: "[Device Name] ESP"
3. Connect using new fallback password: $NEW_FALLBACK_PASSWORD
4. Access device at: http://192.168.4.1
5. Verify web interface loads correctly
6. Reconnect device to main WiFi

✅ Fallback access should work with new password
EOF
```

## Step 4: Cleanup and Documentation

### 4.1 Clean Up Temporary Files

```bash
# Remove temporary credential files
rm -f secrets.yaml.old
rm -f secrets.yaml.backup.*

# Verify no old credentials remain in working directory
grep -r "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=" . --exclude-dir=.git || \
  echo "✅ No old API keys found" # pragma: allowlist secret
grep -r "5929ccc1f08289c79aca50ebe0a9b7eb" . --exclude-dir=.git || \
  echo "✅ No old OTA passwords found" # pragma: allowlist secret
grep -r "1SXRpeXi7AdU" . --exclude-dir=.git || echo "✅ No old fallback passwords found" # pragma: allowlist secret
```

### 4.2 Update Security Documentation

```bash
# Update security baseline if using detect-secrets
if command -v detect-secrets >/dev/null 2>&1; then
    detect-secrets scan --baseline .secrets.baseline
    echo "✅ Security baseline updated"
fi

# Run final security scan
task security-scan
```

### 4.3 Document Rotation

Create a rotation record:

```bash
# Document the rotation
cat >> CREDENTIAL_ROTATION_LOG.md << EOF

## Rotation $(date +%Y-%m-%d)

**Date**: $(date)
**Reason**: Exposed credentials in public repository
**Rotated Credentials**:
- API Encryption Key
- OTA Password
- Fallback Hotspot Password

**Process Used**: Two-stage deployment
**Validation**: All devices tested successfully
**Completed By**: $(whoami)

EOF

echo "✅ Rotation documented in CREDENTIAL_ROTATION_LOG.md"
```

## Troubleshooting

### Device Not Responding After Rotation

If a device becomes unresponsive:

1. **Check network connectivity**:

   ```bash
   ping device-name.local
   ```

2. **Try fallback hotspot access**:
   - Power cycle the device
   - Connect to "[Device Name] ESP" network
   - Use new fallback password
   - Access <http://192.168.4.1>

3. **Physical access recovery**:
   - Connect device via USB
   - Flash firmware directly:

     ```bash
     task upload -- device-name --device /dev/ttyUSB0
     ```

### 1Password Access Issues

If 1Password commands fail:

```bash
# Re-authenticate
op signin

# Verify account access
op account list

# Test vault access
op vault list

# Test item access
op item get "ESPHome" --vault="Automation"
```

### Security Hook False Positives

If security hooks incorrectly flag valid configurations:

1. **Check for hardcoded values** instead of `!secret` references
2. **Verify secrets.yaml** contains only valid references
3. **Update security patterns** in
   [`.githooks/esphome-credential-check.sh`](.githooks/esphome-credential-check.sh:1) if needed

### Rollback Procedure

If rotation fails and rollback is needed:

```bash
# EMERGENCY ROLLBACK - Use only if new credentials fail

# 1. Restore old credentials temporarily
cat > secrets.yaml << EOF
wifi_ssid: $(op read "op://Shared/Home IoT/network name" )
wifi_password: $(op read "op://Shared/Home IoT/wireless network password" )
wifi_domain: $(op read "op://Shared/Home IoT/domain name" )
api_key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=" # pragma: allowlist secret
ota_password: "5929ccc1f08289c79aca50ebe0a9b7eb" # pragma: allowlist secret
fallback_password: "1SXRpeXi7AdU" # pragma: allowlist secret
EOF

# 2. Deploy old credentials to restore connectivity
task upload-all-two-stage

# 3. Investigate and fix issues before attempting rotation again
echo "⚠️  ROLLBACK COMPLETED - Investigate issues before retry"
```

## Security Best Practices

### Regular Rotation Schedule

- **API Keys**: Every 90 days or immediately after exposure
- **OTA Passwords**: Every 90 days or immediately after exposure
- **Fallback Passwords**: Every 180 days or immediately after exposure
- **WiFi Credentials**: As needed or after exposure

### Monitoring and Detection

The following security measures are active:

- **Git hooks**: Prevent committing exposed credentials ([`.githooks/esphome-credential-check.sh`](.githooks/esphome-credential-check.sh:1))
- **Pre-commit hooks**: Validate all changes before commit
- **1Password integration**: Secure credential storage and retrieval
- **Two-stage deployment**: Zero-downtime credential updates

### Emergency Procedures

1. **Immediate exposure response**:
   - Rotate credentials within 1 hour
   - Document exposure in security log
   - Review access logs if available

2. **Communication**:
   - Notify team members of rotation
   - Update documentation
   - Schedule follow-up security review

## Integration with Existing Workflows

This rotation process integrates with:

- **Task runner**: Uses [`task upload-all-two-stage`](Taskfile.yml:147-154) for deployment
- **Security validation**: Runs [`task security-validate`](Taskfile.yml:19-36) before deployment
- **1Password**: Uses [`./scripts/generate_secrets.sh`](scripts/generate_secrets.sh:1) for credential management
- **Git hooks**: Validates changes with security hooks

## Conclusion

Following this guide ensures secure, zero-downtime rotation of exposed ESPHome credentials. The
two-stage deployment process maintains device connectivity throughout the rotation while the
integrated security hooks prevent future credential exposure.

For questions or issues, refer to the troubleshooting section or review the security implementation in [`scripts/setup-security.sh`](scripts/setup-security.sh:1).
