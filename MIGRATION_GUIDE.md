# Migration Guide: Bash to Python Security Framework

This guide helps you migrate from the old bash-based security scripts to the new unified Python security framework.

## Overview

The migration replaces mixed bash/Python scripts with a cohesive Python-based solution that provides:
- Better error handling and logging
- Unified credential validation
- Comprehensive testing
- Enhanced 1Password integration
- Development environment support

## Migration Mapping

### Script Replacements

| Old Bash Script | New Python Script | Status |
|----------------|-------------------|---------|
| `validate-secrets.sh` | [`validate_secrets.py`](scripts/validate_secrets.py) | ✅ Direct replacement |
| `validate-1password-structure.sh` | [`validate_1password_structure.py`](scripts/validate_1password_structure.py) | ✅ Direct replacement |
| `setup-security.sh` | [`setup_security.py`](scripts/setup_security.py) | ✅ Enhanced replacement |
| `rotate_credentials.py` | [`rotate_credentials.py`](scripts/rotate_credentials.py) | ✅ Refactored to use shared library |
| N/A | [`track_secret_rotation.py`](scripts/track_secret_rotation.py) | 🆕 New functionality |
| N/A | [`setup_dev_secrets.py`](scripts/setup_dev_secrets.py) | 🆕 New functionality |
| N/A | [`backup_secrets.py`](scripts/backup_secrets.py) | 🆕 New functionality |

### Task Command Changes

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `task security-validate` | `task security-validate` | ✅ Same command, uses Python internally |
| `task security-scan` | `task security-scan` | ✅ Enhanced with Python validation |
| `./scripts/setup-security.sh` | `task security-setup` | ✅ Now uses Python script |
| `./scripts/validate-secrets.sh` | `python3 scripts/validate_secrets.py` | ✅ Direct Python execution |
| N/A | `task security-rotate-credentials` | 🆕 New task for credential rotation |
| N/A | `task dev-setup` | 🆕 Development environment setup |

## Step-by-Step Migration

### 1. Environment Setup

#### Create Environment Configuration
```bash
# Create .env file for 1Password account configuration
cat > .env << EOF
OP_ACCOUNT=your-1password-account-name
EOF
```

#### Update .gitignore (if needed)
Ensure your `.gitignore` includes:
```
.env
secrets.yaml
*.backup
dev/secrets.yaml
backups/
```

### 2. Install New Security Framework

```bash
# Run the new Python setup script
python3 scripts/setup_security.py

# This replaces the old bash setup script
# ./scripts/setup-security.sh  # OLD - no longer needed
```

### 3. Update Your Workflow

#### Replace Direct Script Calls

**Old approach:**
```bash
./scripts/validate-secrets.sh
./scripts/validate-1password-structure.sh
./scripts/setup-security.sh
```

**New approach:**
```bash
python3 scripts/validate_secrets.py
python3 scripts/validate_1password_structure.py
python3 scripts/setup_security.py
```

#### Use New Task Commands

**Enhanced tasks:**
```bash
# These now use Python scripts internally
task security-validate
task security-scan

# New tasks available
task security-setup
task security-rotate-credentials
task dev-setup
task test-security
```

### 4. Update CI/CD and Automation

#### Pre-commit Hooks
The pre-commit configuration has been updated automatically. The new hooks use Python scripts while maintaining backward compatibility.

**Verify pre-commit setup:**
```bash
pre-commit run --all-files
```

#### GitHub Actions / CI
Update any CI scripts that call the old bash scripts:

**Old:**
```yaml
- name: Validate secrets
  run: ./scripts/validate-secrets.sh
```

**New:**
```yaml
- name: Validate secrets
  run: python3 scripts/validate_secrets.py
```

### 5. Development Environment

#### Set Up Development Credentials
```bash
# New functionality - safe development environment
python3 scripts/setup_dev_secrets.py

# Use development secrets for testing
cp dev/secrets.yaml secrets.yaml  # For development only
```

#### Run Tests
```bash
# New comprehensive testing
python3 tests/run_tests.py

# Or use task
task test-security
```

## Feature Enhancements

### New Capabilities

#### 1. Credential Rotation Tracking
```bash
# Track rotation history
python3 scripts/track_secret_rotation.py status

# Add rotation entry
python3 scripts/track_secret_rotation.py add
```

#### 2. Backup and Restore
```bash
# Create backup
python3 scripts/backup_secrets.py create

# List backups
python3 scripts/backup_secrets.py list

# Restore backup
python3 scripts/backup_secrets.py restore backup_20240101_120000
```

#### 3. Development Environment
```bash
# Set up safe development environment
python3 scripts/setup_dev_secrets.py

# Generate test credentials
python3 scripts/setup_dev_secrets.py --dev-only
```

### Enhanced Error Handling

The Python framework provides:
- **Detailed error messages** with specific remediation steps
- **Colored output** for better readability
- **Structured logging** with different verbosity levels
- **Exit codes** for automation integration

### Improved 1Password Integration

- **Environment-based configuration** (no hardcoded account names)
- **Better error handling** for CLI failures
- **Validation of vault structure** before operations
- **Graceful fallbacks** when 1Password is unavailable

## Validation and Testing

### Verify Migration Success

#### 1. Test Basic Functionality
```bash
# Test secret validation
python3 scripts/validate_secrets.py

# Test 1Password integration
python3 scripts/validate_1password_structure.py

# Test security scanning
task security-scan
```

#### 2. Run Comprehensive Tests
```bash
# Run all unit tests
python3 tests/run_tests.py

# Check test environment
python3 tests/run_tests.py --check-env
```

#### 3. Test Integration Points
```bash
# Test task integration
task security-validate

# Test pre-commit hooks
pre-commit run --all-files
```

### Troubleshooting Migration Issues

#### Common Issues and Solutions

**1. 1Password CLI Issues**
```bash
# Check CLI availability
op account list

# Sign in if needed
op signin

# Verify account configuration
echo $OP_ACCOUNT
```

**2. Python Import Errors**
```bash
# Check Python path
python3 -c "import sys; print(sys.path)"

# Verify script location
ls -la scripts/security_lib.py
```

**3. Permission Issues**
```bash
# Make scripts executable
chmod +x scripts/*.py

# Check file permissions
ls -la scripts/
```

**4. Environment Variable Issues**
```bash
# Check .env file
cat .env

# Verify environment loading
python3 -c "import os; print(os.getenv('OP_ACCOUNT'))"
```

## Rollback Plan

If you need to temporarily rollback to the old bash scripts:

### 1. Disable New Pre-commit Hooks
```bash
# Edit .pre-commit-config.yaml
# Comment out the new Python hooks
# Uncomment the legacy hooks
```

### 2. Use Legacy Task Commands
```bash
# The old scripts are still available
./scripts/validate-secrets.sh
./scripts/validate-1password-structure.sh
./scripts/setup-security.sh
```

### 3. Restore Old Taskfile (if needed)
```bash
# Revert Taskfile.yml changes
git checkout HEAD~1 -- Taskfile.yml
```

## Benefits of Migration

### Immediate Benefits
- **Unified error handling** across all security operations
- **Better logging** with colored output and verbosity control
- **Environment-based configuration** (no hardcoded values)
- **Comprehensive testing** with unit test coverage

### Long-term Benefits
- **Easier maintenance** with shared library components
- **Enhanced functionality** (rotation tracking, backups, dev environment)
- **Better integration** with development workflows
- **Improved security** with exposed credential detection

### Development Benefits
- **Safe development environment** with test credentials
- **Comprehensive testing framework** with mocking support
- **Better debugging** with detailed error messages
- **Consistent code style** across all security scripts

## Next Steps

After successful migration:

1. **Remove old bash scripts** (optional, for cleanup)
2. **Update documentation** to reference new Python scripts
3. **Train team members** on new commands and workflows
4. **Set up monitoring** for security validation in CI/CD
5. **Schedule regular testing** of the security framework

## Support

For migration assistance:

1. **Check the troubleshooting section** above
2. **Run diagnostic commands** to identify issues
3. **Review the comprehensive documentation** in [`SECURITY_FRAMEWORK.md`](SECURITY_FRAMEWORK.md)
4. **Test individual components** to isolate problems

The Python framework provides extensive logging and error reporting to help diagnose migration issues quickly.
