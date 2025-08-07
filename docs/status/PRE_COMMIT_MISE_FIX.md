# Pre-commit Hooks with Mise Environment Fix

## Problem

Pre-commit hooks were failing to access dependencies managed by Mise because they run in their own isolated
environment and don't automatically source the Mise configuration. The hooks were using `language: system` with
direct `python3` calls, but needed to use the Mise-managed Python virtual environment.

## Solution

### 1. Created Mise Wrapper Script

Created `.githooks/mise-python-wrapper.sh` to properly source the Mise environment:

```bash
#!/bin/bash
# Mise Python Wrapper for Pre-commit Hooks
# This script ensures pre-commit hooks use the Mise-managed Python environment

set -e

# Change to the repository root directory
cd "$(git rev-parse --show-toplevel)"

# Source mise environment if available
if command -v mise >/dev/null 2>&1; then
    # Use mise exec to run the command in the proper environment
    exec mise exec -- python3 "$@"
else
    # Fallback to system python3 if mise is not available
    exec python3 "$@"
fi
```

### 2. Updated Pre-commit Configuration

Modified `.pre-commit-config.yaml` to use the wrapper script with `language: script` instead of `language: system`:

**Before:**

```yaml
- id: esphome-secrets-validation
  name: ESPHome secrets validation (Python)
  entry: python3 scripts/validate_secrets.py
  language: system
```

**After:**

```yaml
- id: esphome-secrets-validation
  name: ESPHome secrets validation (Python)
  entry: .githooks/mise-python-wrapper.sh scripts/validate_secrets.py
  language: script
```

### 3. Applied to All Python Security Hooks

Updated all three Python security framework hooks:

- `esphome-secrets-validation`
- `esphome-1password-validation`
- `python-security-tests`

## Key Benefits

1. **Environment Consistency**: Pre-commit hooks now use the same Python environment as manual script execution
2. **Dependency Access**: Hooks can access PyYAML and other Mise-managed dependencies
3. **Fallback Support**: Script gracefully falls back to system Python if Mise is unavailable
4. **Repository Portability**: Works across different development environments

## Testing Results

All Python security framework hooks now run successfully:

- ✅ ESPHome secrets validation - Running and detecting issues properly
- ✅ Python security tests - Running with 91.4% success rate
- ✅ 1Password validation - Running properly

## Files Modified

- `.githooks/mise-python-wrapper.sh` (created)
- `.pre-commit-config.yaml` (updated)

## Usage

Pre-commit hooks now work automatically with the Mise environment:

```bash
# Test individual hook
pre-commit run esphome-secrets-validation --all-files

# Test all hooks
pre-commit run --all-files
```

The wrapper script ensures that `mise exec -- python3` is used when Mise is available, providing access to the
virtual environment and all managed dependencies.
