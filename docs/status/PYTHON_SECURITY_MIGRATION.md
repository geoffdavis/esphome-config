# Python Security Scripts Migration

This document describes the migration of ESPHome security shell scripts to Python for better maintainability and testing.

## Overview

The essential security shell scripts have been converted to Python to provide:

- Better error handling and logging
- Easier testing with unit tests
- More robust file handling and pattern matching
- Better integration with existing Python ecosystem (ESPHome uses Python)
- Cleaner configuration management

## Converted Scripts

### 1. Setup Security Script
- **From**: `scripts/setup-security.sh`
- **To**: `scripts/setup_security.py`
- **Purpose**: Main security setup script that installs and configures git-secrets, pre-commit, and essential hooks

### 2. ESPHome Credential Check
- **From**: `.githooks/esphome-credential-check.sh`
- **To**: `.githooks/esphome_credential_check.py`
- **Purpose**: Validates YAML files for hardcoded credentials and known exposed secrets
- **Status**: Available for manual use only (removed from CI pipeline due to redundancy)

### 3. Git-Secrets Scan Wrapper
- **From**: `.githooks/git-secrets-scan.sh`
- **To**: `.githooks/git_secrets_scan.py`
- **Purpose**: Python wrapper for git-secrets scanning with graceful fallback

## Key Features

### Enhanced Error Handling
- Proper exception handling with meaningful error messages
- Graceful degradation when optional tools are not available
- Better exit codes and status reporting

### Improved Pattern Matching
- More robust regex pattern matching
- Better handling of edge cases
- Cleaner separation of concerns

### Testing Support
- Unit tests for credential detection patterns
- Test coverage for known exposed credentials
- Automated test runner

## Usage

### Running Setup
```bash
# Python version (recommended)
python3 scripts/setup_security.py

# Or make it executable and run directly
./scripts/setup_security.py
```

### Running Tests
```bash
# Run all security script tests
task test-security

# Or run directly
python3 tests/run_tests.py
```

### Manual Credential Check
```bash
# Check specific files
./.githooks/esphome_credential_check.py device1.yaml device2.yaml

# Check all YAML files
find . -name "*.yaml" -not -path "./.esphome/*" -exec ./.githooks/esphome_credential_check.py {} +
```

## Integration

### Taskfile.yml Integration
The Python scripts are integrated into the existing Taskfile.yml:

- `security-validate`: Uses Python credential checker
- `test-security`: Runs Python unit tests
- All existing tasks continue to work with Python scripts

### Pre-commit Integration
The `.pre-commit-config.yaml` has been updated to use Python scripts:

```yaml
- repo: local
  hooks:
    - id: esphome-credential-check
      name: ESPHome credential validation
      entry: .githooks/esphome_credential_check.py
      language: script
      files: \.(yaml|yml)$
      pass_filenames: true

    - id: git-secrets-scan
      name: Git-secrets credential scan
      entry: .githooks/git_secrets_scan.py
      language: script
      files: \.(yaml|yml|sh|py|js|ts|json|md)$
      pass_filenames: true
```

## Testing

### Unit Tests
Located in `tests/test_esphome_credential_check.py`:

- Tests for API key detection
- Tests for OTA password detection
- Tests for fallback password detection
- Tests for known exposed credentials
- Tests for valid !secret references
- Tests for multiple file handling

### Running Tests
```bash
# Via Taskfile
task test-security

# Direct execution
python3 tests/run_tests.py

# Individual test file
python3 -m unittest tests.test_esphome_credential_check
```

## Dependencies

### Required
- Python 3.6+
- Standard library modules only (no external dependencies for core functionality)

### Optional
- `git-secrets` (for git-secrets integration)
- `pre-commit` (for pre-commit hooks)
- `detect-secrets` (for secrets baseline)

## Migration Benefits

### Maintainability
- Cleaner, more readable code structure
- Better separation of concerns
- Easier to extend and modify

### Testing
- Comprehensive unit test coverage
- Automated testing in CI/CD pipelines
- Better validation of security patterns

### Error Handling
- More informative error messages
- Better handling of edge cases
- Graceful degradation when tools are missing

### Integration
- Better integration with Python-based ESPHome ecosystem
- Consistent with project's primary language
- Easier to extend with additional Python-based security tools

## Backward Compatibility

The original shell scripts are preserved for reference but are no longer used by default. The Python scripts maintain the same command-line interface and exit codes for seamless integration.

## Future Enhancements

Potential improvements for the Python implementation:

1. **Configuration File Support**: YAML/JSON configuration for patterns and settings
2. **Plugin Architecture**: Extensible pattern detection system
3. **Enhanced Reporting**: JSON/XML output formats for CI/CD integration
4. **Performance Optimization**: Parallel file processing for large repositories
5. **Advanced Pattern Detection**: Machine learning-based credential detection

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure scripts are executable (`chmod +x`)
2. **Import Errors**: Check Python path and module locations
3. **Missing Dependencies**: Install optional tools as needed

### Debug Mode
Set environment variable for verbose output:
```bash
export DEBUG=1
python3 scripts/setup_security.py
```

## Support

For issues or questions about the Python security scripts:

1. Check the unit tests for expected behavior
2. Review the original shell scripts for reference
3. Run tests to validate functionality
4. Check integration with existing workflow

The Python implementation maintains the same practical, single-user focused approach while providing better maintainability and testing capabilities.
