# ESPHome Security Implementation

This document describes the streamlined security implementation for this single-user ESPHome repository, focused on preventing accidental credential exposure.

## Quick Start

### Setup

Run the setup script to install and configure security tools:

```bash
./scripts/setup-security.sh
```

This will:
- Install git-secrets and pre-commit
- Configure ESPHome-specific credential patterns
- Set up essential validation hooks
- Run initial security scans

### Manual Setup

If you prefer manual setup:

```bash
# Install dependencies
brew install git-secrets  # macOS
pip install pre-commit detect-secrets

# Configure git-secrets
git secrets --install
git secrets --register-aws

# Install pre-commit hooks
pre-commit install
```

## Security Features

### 1. Pre-commit Hooks

Essential hooks that run before each commit:
- **detect-secrets**: Scans for hardcoded secrets
- **yamllint**: Validates YAML structure
- **esphome-credential-check**: ESPHome-specific credential validation
- **git-secrets-scan**: Git-secrets integration

### 2. ESPHome Credential Detection

Automatically detects and prevents:
- **API Encryption Keys**: 44-character base64 strings
- **OTA Passwords**: 32-character hex strings
- **Fallback Hotspot Passwords**: 12-character alphanumeric
- **Known Exposed Credentials**: Previously leaked values
- **WiFi Credentials**: Hardcoded passwords and SSIDs

### 3. Git-secrets Integration

Configured patterns for:
- ESPHome-specific credential formats
- Generic high-entropy strings
- Known exposed credentials from this repository
- Common secret patterns (API keys, tokens, etc.)

### 4. GitHub Actions

Automated security scanning on:
- Push to main/develop branches
- Pull requests
- Scheduled weekly scans

## Usage

### Running Security Checks

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run git-secrets scan
git secrets --scan

# Run basic security validation (via Taskfile)
task security-validate

# Run comprehensive security scan
task security-scan
```

### Integration with Existing Workflow

Security validation is integrated into existing tasks:

```bash
# Upload with security validation
task upload -- device_name

# Upload all devices (includes security checks)
task upload-all-two-stage

# Generate secrets (basic validation)
task secrets
```

## Security Patterns

### Detected Patterns

```regex
# API Encryption Keys (44-character base64)
[A-Za-z0-9+/]{43}=

# OTA Passwords (32-character hex)
\b[a-fA-F0-9]{32}\b

# Fallback Hotspot Passwords (12-character alphanumeric)
\b[A-Za-z0-9]{12}\b

# Known Exposed Credentials (specific to this repo)
rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=
5929ccc1f08289c79aca50ebe0a9b7eb
1SXRpeXi7AdU
```

### Allowed Patterns

```regex
# ESPHome secret references
!secret\s+[A-Za-z0-9_]+

# 1Password CLI commands in scripts
op\s+read\s+["\']?op://[^"'\s]+["\']?

# Documentation placeholders
EXAMPLE_[A-Z_]+
YOUR_[A-Z_]+_HERE
test_[a-z_]+
```

## Best Practices

### For ESPHome Configurations

1. **Always use `!secret` references** for sensitive data:
   ```yaml
   # ✅ Correct
   api:
     encryption:
       key: !secret api_key

   # ❌ Incorrect
   api:
     encryption:
       key: "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="  # pragma: allowlist secret
   ```

2. **Enable API encryption** with proper key management
3. **Set OTA passwords** for secure updates
4. **Secure fallback hotspots** with strong passwords

### For Scripts and Automation

1. **Use 1Password CLI** for credential retrieval:
   ```bash
   # ✅ Correct
   API_KEY=$(op read "op://Automation/ESPHome/api_key" --account="$OP_ACCOUNT")

   # ❌ Incorrect
   API_KEY="rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk="  # pragma: allowlist secret
   ```

2. **Never commit secrets.yaml** (already in .gitignore)
3. **Run security validation** before deployment

## Troubleshooting

### Pre-commit Hook Failures

```bash
# Update hooks
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### Git-secrets Issues

```bash
# Reinstall git-secrets patterns
git secrets --install --force
git secrets --register-aws

# Check current patterns
git secrets --list
```

### False Positives

Add allowed patterns to git-secrets:

```bash
git secrets --add --allowed 'your_allowed_pattern_here'
```

## Files and Structure

### Security Files Created

- [`.pre-commit-config.yaml`](.pre-commit-config.yaml) - Pre-commit configuration
- [`.gitsecrets`](.gitsecrets) - Git-secrets patterns
- [`scripts/setup-security.sh`](scripts/setup-security.sh) - Setup script
- [`.githooks/`](.githooks/) - Essential validation scripts
- [`.gitignore`](.gitignore) - Enhanced with security patterns

### GitHub Actions

- [`.github/workflows/security-scan.yml`](.github/workflows/security-scan.yml) - Security scanning
- [`.github/workflows/dependency-security.yml`](.github/workflows/dependency-security.yml) - Dependency scanning

## Maintenance

### Regular Tasks

1. **Update dependencies** monthly:
   ```bash
   pre-commit autoupdate
   brew upgrade git-secrets  # macOS
   ```

2. **Review security patterns** as needed
3. **Test hook functionality** after updates

### Adding New Patterns

1. Update [`.gitsecrets`](.gitsecrets) with new patterns
2. Test patterns with sample data
3. Re-run setup script: `./scripts/setup-security.sh`

## Security Considerations

This streamlined implementation provides essential protection for a single-user repository:

- ✅ Prevents accidental credential exposure
- ✅ Integrates seamlessly with existing workflow
- ✅ Minimal maintenance overhead
- ✅ Focused on actual security needs
- ✅ No complex enterprise processes

The security hooks catch common mistakes but should be combined with good security practices and awareness.
