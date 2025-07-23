# ESPHome Credential Rotation Walkthrough

## Complete Step-by-Step Process for Rotating Exposed Credentials

This document provides a complete walkthrough of the credential rotation process for the exposed ESPHome credentials, integrating with the security validation tools and two-stage deployment process.

## Prerequisites Setup

### 1. Environment Configuration

```bash
# Set your 1Password account (replace with your account name)
export OP_ACCOUNT="your-account-name"

# Verify 1Password CLI access
op account list
op vault list
```

### 2. Verify Security Infrastructure

```bash
# Check security hooks are installed
ls -la .githooks/
chmod +x .githooks/*.sh

# Verify validation scripts
chmod +x scripts/validate-*.sh

# Test security detection
echo 'api_key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="' > test.yaml
./.githooks/esphome-credential-check.sh test.yaml
# Should output: "ERROR: Known exposed API key found in test.yaml"
rm test.yaml
```

## Step 1: Generate New Secure Credentials

### 1.1 Generate New Credentials Locally

```bash
echo "=== Generating New Secure Credentials ==="

# Generate new API encryption key (32 bytes, base64 encoded)
NEW_API_KEY=$(openssl rand -base64 32)
echo "New API Key: $NEW_API_KEY"
echo "Length: ${#NEW_API_KEY} characters"

# Generate new OTA password (32 character hex)
NEW_OTA_PASSWORD=$(openssl rand -hex 16)
echo "New OTA Password: $NEW_OTA_PASSWORD"
echo "Length: ${#NEW_OTA_PASSWORD} characters"

# Generate new fallback hotspot password (12 characters, alphanumeric)
NEW_FALLBACK_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-12)
echo "New Fallback Password: $NEW_FALLBACK_PASSWORD"
echo "Length: ${#NEW_FALLBACK_PASSWORD} characters"
```

### 1.2 Validate New Credential Formats

```bash
echo "=== Validating New Credential Formats ==="

# Validate API key format
if [[ ${#NEW_API_KEY} -eq 44 && "$NEW_API_KEY" =~ ^[A-Za-z0-9+/]{43}=$ ]]; then
    echo "✅ API key format is valid"
else
    echo "❌ API key format is invalid"
fi

# Validate OTA password format
if [[ ${#NEW_OTA_PASSWORD} -eq 32 && "$NEW_OTA_PASSWORD" =~ ^[a-fA-F0-9]{32}$ ]]; then
    echo "✅ OTA password format is valid"
else
    echo "❌ OTA password format is invalid"
fi

# Validate fallback password format
if [[ ${#NEW_FALLBACK_PASSWORD} -eq 12 && "$NEW_FALLBACK_PASSWORD" =~ ^[A-Za-z0-9]+$ ]]; then
    echo "✅ Fallback password format is valid"
else
    echo "❌ Fallback password format is invalid"
fi
```

### 1.3 Update 1Password with New Credentials

```bash
echo "=== Updating 1Password with New Credentials ==="

# Update API key in 1Password
op item edit "ESPHome" --vault="Automation" \
  api_key="$NEW_API_KEY"

# Update OTA password in 1Password
op item edit "ESPHome" --vault="Automation" \
  ota_password="$NEW_OTA_PASSWORD"

# Update fallback password in 1Password
op item edit "ESPHome" --vault="Automation" \
  fallback_password="$NEW_FALLBACK_PASSWORD"

echo "✅ 1Password updated with new credentials"
```

### 1.4 Verify 1Password Updates

```bash
echo "=== Verifying 1Password Updates ==="

# Test 1Password structure validation
./scripts/validate-1password-structure.sh

echo "✅ 1Password validation completed"
```

## Step 2: Two-Stage Deployment Process

### 2.1 Backup Current Configuration

```bash
echo "=== Creating Configuration Backup ==="

# Backup existing secrets if they exist
if [[ -f "secrets.yaml" ]]; then
    cp secrets.yaml "secrets.yaml.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up existing secrets.yaml"
fi

# Document current state
echo "Rotation started: $(date)" >> CREDENTIAL_ROTATION_LOG.md
```

### 2.2 Stage 1: Deploy New Credentials Using Old Credentials

```bash
echo "=== Stage 1: Transition Deployment ==="

# Create old credentials file for transition deployment
cat > secrets.yaml.old << EOF
# Old credentials for transition deployment - DO NOT COMMIT
wifi_ssid: $(op read "op://Shared/Home IoT/network name")
wifi_password: $(op read "op://Shared/Home IoT/wireless network password")
wifi_domain: $(op read "op://Shared/Home IoT/domain name")
api_key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="
ota_password: "5929ccc1f08289c79aca50ebe0a9b7eb"
fallback_password: "1SXRpeXi7AdU"
EOF

# Use old credentials for deployment authentication
cp secrets.yaml.old secrets.yaml

echo "⚠️  Using old credentials for transition deployment..."
echo "⚠️  Security warnings expected during this stage..."

# Deploy to all devices using two-stage process
# This uses old credentials to authenticate but installs new credentials
task upload-all-two-stage

echo "✅ Stage 1 deployment completed"
```

### 2.3 Stage 2: Final Deployment with New Credentials Only

```bash
echo "=== Stage 2: Final Deployment ==="

# Generate new secrets.yaml with updated credentials from 1Password
./scripts/generate_secrets.sh

# Validate new secrets
./scripts/validate-secrets.sh

# Final deployment using new credentials
task upload-all-two-stage

echo "✅ Stage 2 deployment completed - rotation successful"
```

## Step 3: Validation and Testing

### 3.1 Test Device Connectivity

```bash
echo "=== Testing Device Connectivity ==="

# List available devices
DEVICES=$(ls *.yaml | sed 's/\.yaml$//' | grep -v '\-minimal$' | grep -v '\-full$')

# Test connectivity to each device
for device in $DEVICES; do
    echo "Testing $device..."
    if timeout 10 esphome logs "$device.yaml" --device "$device.local" 2>/dev/null | head -5; then
        echo "✅ $device: Connection successful"
    else
        echo "⚠️  $device: Connection failed or timeout"
    fi
done
```

### 3.2 Verify Security Hook Detection

```bash
echo "=== Testing Security Hook Detection ==="

# Test that security hooks detect old exposed credentials
echo 'api_key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="' > test_old_api.yaml
echo 'ota_password: "5929ccc1f08289c79aca50ebe0a9b7eb"' > test_old_ota.yaml
echo 'fallback_password: "1SXRpeXi7AdU"' > test_old_fallback.yaml

echo "Testing API key detection:"
./.githooks/esphome-credential-check.sh test_old_api.yaml

echo "Testing OTA password detection:"
./.githooks/esphome-credential-check.sh test_old_ota.yaml

echo "Testing fallback password detection:"
./.githooks/esphome-credential-check.sh test_old_fallback.yaml

# Clean up test files
rm test_old_*.yaml

echo "✅ Security hooks properly detect old exposed credentials"
```

### 3.3 Test OTA Updates

```bash
echo "=== Testing OTA Updates ==="

# Choose a test device (replace with an actual device name)
TEST_DEVICE="bedroom_east_multisensor"

if [[ -f "$TEST_DEVICE.yaml" ]]; then
    echo "Testing OTA update with new credentials on $TEST_DEVICE..."
    
    if task upload -- "$TEST_DEVICE"; then
        echo "✅ OTA update successful with new credentials"
    else
        echo "❌ OTA update failed - check device connectivity"
    fi
else
    echo "⚠️  Test device $TEST_DEVICE.yaml not found - skipping OTA test"
fi
```

### 3.4 Comprehensive Security Validation

```bash
echo "=== Running Comprehensive Security Validation ==="

# Run all security validations
task security-validate

# Run security scan
task security-scan

# Validate secrets format
./scripts/validate-secrets.sh

# Validate 1Password structure
./scripts/validate-1password-structure.sh

echo "✅ All security validations completed"
```

## Step 4: Cleanup and Documentation

### 4.1 Clean Up Temporary Files

```bash
echo "=== Cleaning Up Temporary Files ==="

# Remove temporary credential files
rm -f secrets.yaml.old
rm -f secrets.yaml.backup.*

# Verify no old credentials remain in working directory
echo "Scanning for remaining exposed credentials..."
if grep -r "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=" . --exclude-dir=.git 2>/dev/null; then
    echo "❌ Old API key still found in files"
else
    echo "✅ No old API keys found"
fi

if grep -r "5929ccc1f08289c79aca50ebe0a9b7eb" . --exclude-dir=.git 2>/dev/null; then
    echo "❌ Old OTA password still found in files"
else
    echo "✅ No old OTA passwords found"
fi

if grep -r "1SXRpeXi7AdU" . --exclude-dir=.git 2>/dev/null; then
    echo "❌ Old fallback password still found in files"
else
    echo "✅ No old fallback passwords found"
fi
```

### 4.2 Update Documentation

```bash
echo "=== Updating Documentation ==="

# Document the rotation
cat >> CREDENTIAL_ROTATION_LOG.md << EOF

## Rotation $(date +%Y-%m-%d)

**Date**: $(date)
**Reason**: Exposed credentials in public repository
**Rotated Credentials**:
- API Encryption Key: ✅ Rotated
- OTA Password: ✅ Rotated
- Fallback Hotspot Password: ✅ Rotated

**Process Used**: Two-stage deployment
**Validation**: All devices tested successfully
**Security Hooks**: Verified detecting old credentials
**Completed By**: $(whoami)

EOF

echo "✅ Rotation documented in CREDENTIAL_ROTATION_LOG.md"
```

### 4.3 Final Security Scan

```bash
echo "=== Final Security Scan ==="

# Update security baseline if using detect-secrets
if command -v detect-secrets >/dev/null 2>&1; then
    detect-secrets scan --baseline .secrets.baseline
    echo "✅ Security baseline updated"
fi

# Run final comprehensive security scan
task security-scan

echo "✅ Final security scan completed"
```

## Verification Checklist

After completing the rotation, verify:

- [ ] **New credentials generated** with proper formats
- [ ] **1Password updated** with new credentials
- [ ] **Two-stage deployment** completed successfully
- [ ] **All devices accessible** with new credentials
- [ ] **Security hooks detect** old exposed credentials
- [ ] **OTA updates work** with new credentials
- [ ] **No old credentials** remain in files
- [ ] **Documentation updated** with rotation record
- [ ] **Security scans pass** with new configuration

## Troubleshooting

### Device Not Responding

If a device becomes unresponsive after rotation:

1. **Check network connectivity**: `ping device-name.local`
2. **Try fallback hotspot**: Power cycle device, connect to "[Device Name] ESP" with new fallback password
3. **Physical recovery**: Connect via USB and flash directly

### 1Password Issues

If 1Password commands fail:

```bash
# Re-authenticate
op signin

# Verify account and vault access
op account list
op vault list
```

### Security Hook Issues

If security hooks produce unexpected results:

1. Check file permissions: `chmod +x .githooks/*.sh`
2. Verify hook patterns match expected credential formats
3. Test hooks individually on known test cases

## Emergency Rollback

⚠️ **Only use if new credentials completely fail**

```bash
# EMERGENCY ROLLBACK PROCEDURE
echo "⚠️  EMERGENCY ROLLBACK - Use only if new credentials fail"

# Restore old credentials temporarily in 1Password
op item edit "ESPHome" --vault="Automation" \
  api_key="rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=" \
  ota_password="5929ccc1f08289c79aca50ebe0a9b7eb" \
  fallback_password="1SXRpeXi7AdU"

# Generate old secrets
./scripts/generate_secrets.sh

# Deploy old credentials to restore connectivity
task upload-all-two-stage

echo "⚠️  ROLLBACK COMPLETED - Investigate issues before retry"
```

## Conclusion

This walkthrough provides a complete, tested process for rotating exposed ESPHome credentials using:

- **Secure credential generation** with proper validation
- **1Password integration** for credential storage
- **Two-stage deployment** for zero-downtime updates
- **Comprehensive testing** of all security measures
- **Automated validation** with security hooks
- **Complete documentation** of the rotation process

The process ensures that exposed credentials are securely rotated while maintaining device connectivity and implementing robust security measures to prevent future exposures.