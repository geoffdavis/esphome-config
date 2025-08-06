#!/usr/bin/env python3
"""
ESPHome Secrets Validation Script

Validates secrets.yaml format and 1Password integration.
Python conversion of validate-secrets.sh using the shared security library.
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import (
    SecurityLogger,
    SecurityConfig,
    CredentialValidator,
    OnePasswordManager,
    SecureFileHandler,
    SecurityScanner
)


class SecretsValidator:
    """Main secrets validation class"""

    def __init__(self, transition_mode=False):
        self.logger = SecurityLogger("validate_secrets")
        self.validator = CredentialValidator()
        self.file_handler = SecureFileHandler()
        self.scanner = SecurityScanner()
        self.total_errors = 0
        self.transition_mode = transition_mode

        if self.transition_mode:
            self.logger.warning("Running in TRANSITION MODE - allowing old credentials for deployment")

    def check_secrets_file(self) -> bool:
        """Check if secrets.yaml exists"""
        if not os.path.exists("secrets.yaml"):
            self.logger.error("secrets.yaml not found")
            self.logger.info("Generate it with: ./scripts/generate_secrets.sh")
            return False

        self.logger.success("secrets.yaml found")
        return True

    def validate_credential_formats(self) -> bool:
        """Validate all credential formats in secrets.yaml"""
        secrets = self.file_handler.read_secrets_file()
        if not secrets:
            self.logger.error("Failed to read secrets.yaml")
            return False

        errors = 0

        # Validate API key
        if 'api_key' in secrets:
            valid, msg = self.validator.validate_api_key(secrets['api_key'])
            if valid:
                self.logger.success(msg)
            else:
                if "exposed credential" in msg and self.transition_mode:
                    self.logger.warning(f"API key: {msg} (allowed in transition mode)")
                else:
                    self.logger.error(msg)
                    if "exposed credential" in msg:
                        self.logger.error("API key is the known exposed credential - must be rotated!")
                    else:
                        self.logger.info("Expected: 44 characters, base64 encoded, ending with =")
                        self.logger.info("Generate new: openssl rand -base64 32")
                    errors += 1
        else:
            self.logger.error("API key not found in secrets.yaml")
            errors += 1

        # Validate OTA password
        if 'ota_password' in secrets:
            valid, msg = self.validator.validate_ota_password(secrets['ota_password'])
            if valid:
                self.logger.success(msg)
            else:
                # In transition mode, allow old password formats for authentication
                if self.transition_mode and ("exposed credential" in msg or "must be exactly 32" in msg):
                    self.logger.warning(f"OTA password: {msg} (allowed in transition mode)")
                else:
                    self.logger.error(msg)
                    if "exposed credential" in msg:
                        self.logger.error("OTA password is the known exposed credential - must be rotated!")
                    else:
                        self.logger.info("Expected: 32 characters, hexadecimal only")
                        self.logger.info("Generate new: openssl rand -hex 16")
                    errors += 1
        else:
            self.logger.error("OTA password not found in secrets.yaml")
            errors += 1

        # Validate fallback password
        if 'fallback_password' in secrets:
            valid, msg = self.validator.validate_fallback_password(secrets['fallback_password'])
            if valid:
                self.logger.success(msg)
            else:
                if "exposed credential" in msg and self.transition_mode:
                    self.logger.warning(f"Fallback password: {msg} (allowed in transition mode)")
                else:
                    self.logger.error(msg)
                    if "exposed credential" in msg:
                        self.logger.error("Fallback password is the known exposed credential - must be rotated!")
                    else:
                        self.logger.info("Expected: At least 12 characters, alphanumeric only")
                        self.logger.info("Generate new: openssl rand -base64 12 | tr -d '=+/' | cut -c1-12")
                    errors += 1
        else:
            self.logger.error("Fallback password not found in secrets.yaml")
            errors += 1

        # Validate WiFi credentials
        wifi_ssid = secrets.get('wifi_ssid', '')
        wifi_password = secrets.get('wifi_password', '')
        wifi_domain = secrets.get('wifi_domain', '')

        wifi_valid, wifi_errors = self.validator.validate_wifi_credentials(
            wifi_ssid, wifi_password, wifi_domain
        )

        if wifi_valid:
            self.logger.success("WiFi credentials are valid")
            if wifi_domain:
                self.logger.success("WiFi domain is valid")
            else:
                self.logger.warning("WiFi domain not set (optional)")
        else:
            for error in wifi_errors:
                self.logger.error(error)
            errors += len(wifi_errors)

        return errors == 0

    def validate_1password_integration(self) -> bool:
        """Validate 1Password integration"""
        try:
            op_manager = OnePasswordManager()
        except ValueError as e:
            self.logger.warning(f"1Password configuration issue: {e}")
            return True  # Don't fail validation for missing OP_ACCOUNT

        if not op_manager.check_cli_available():
            self.logger.warning("1Password CLI not found - cannot validate integration")
            return True  # Don't fail validation for missing CLI

        self.logger.info("Validating 1Password integration...")

        # Check account access
        if not op_manager.check_account_access():
            self.logger.error(f"Cannot access 1Password account '{op_manager.account}'")
            self.logger.info("Sign in with: op signin")
            return False

        # Check vault access
        if not op_manager.check_vault_access(SecurityConfig.AUTOMATION_VAULT):
            self.logger.error(f"Cannot access {SecurityConfig.AUTOMATION_VAULT} vault")
            return False

        if not op_manager.check_vault_access(SecurityConfig.SHARED_VAULT):
            self.logger.error(f"Cannot access {SecurityConfig.SHARED_VAULT} vault")
            return False

        # Check item access
        if not op_manager.check_item_access(SecurityConfig.AUTOMATION_VAULT, SecurityConfig.ESPHOME_ITEM):
            self.logger.error(f"Cannot access {SecurityConfig.ESPHOME_ITEM} item in {SecurityConfig.AUTOMATION_VAULT} vault")
            return False

        if not op_manager.check_item_access(SecurityConfig.SHARED_VAULT, SecurityConfig.HOME_IOT_ITEM):
            self.logger.error(f"Cannot access {SecurityConfig.HOME_IOT_ITEM} item in {SecurityConfig.SHARED_VAULT} vault")
            return False

        self.logger.success("1Password integration is working")
        return True

    def scan_for_exposed_credentials(self) -> bool:
        """Scan for exposed credentials in files"""
        self.logger.info("Scanning for exposed credentials in YAML files...")

        # Scan all YAML files except secrets.yaml (which we validate separately)
        issues = []
        yaml_files = []

        for root, dirs, files in os.walk('.'):
            # Skip .esphome and other hidden directories except .githooks
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.githooks']

            for file in files:
                if file.endswith(('.yaml', '.yml')) and file != 'secrets.yaml':
                    yaml_files.append(os.path.join(root, file))

        for file_path in yaml_files:
            file_issues = self.scanner.scan_file_for_credentials(file_path)

            # Filter out expected issues from Taskfile.yml only in transition mode
            if file_path == './Taskfile.yml' and self.transition_mode:
                filtered_issues = []
                for issue in file_issues:
                    # Allow old OTA passwords in Taskfile.yml as they're used for detection
                    # Allow all known transition credentials in Taskfile.yml
                    transition_creds = ["ota_password", "ota_password_2", "ota_password_3", "fallback_password_2"]
                    if not any(cred_type in issue for cred_type in transition_creds):
                        filtered_issues.append(issue)
                file_issues = filtered_issues

            issues.extend(file_issues)

        if not issues:
            self.logger.success("No exposed credentials found in YAML files")
            return True
        else:
            for issue in issues:
                if self.transition_mode and "Taskfile.yml" in issue:
                    self.logger.warning(f"{issue} (allowed in transition mode)")
                else:
                    self.logger.error(issue)

            # In transition mode, don't fail if only Taskfile.yml issues remain
            if self.transition_mode:
                non_taskfile_issues = [i for i in issues if "Taskfile.yml" not in i]
                if not non_taskfile_issues:
                    self.logger.success("Only expected transition credentials found")
                    return True

            self.logger.error(f"Found {len(issues)} exposed credential(s) in YAML files")
            return False

    def run_validation(self) -> bool:
        """Run complete secrets validation"""
        self.logger.header("ESPHome Secrets Validation")

        # Check if secrets file exists
        if not self.check_secrets_file():
            return False

        # Validate credential formats
        if not self.validate_credential_formats():
            self.total_errors += 1

        # Validate 1Password integration
        if not self.validate_1password_integration():
            self.total_errors += 1

        # Scan for exposed credentials
        if not self.scan_for_exposed_credentials():
            self.total_errors += 1

        # Print results
        print()
        print("=" * 50)
        if self.total_errors == 0:
            self.logger.success("All validations passed!")
            print("=" * 50)
            return True
        else:
            self.logger.error(f"Validation failed with {self.total_errors} error(s)")
            print("=" * 50)
            print()
            print("To fix issues:")
            print("1. Rotate exposed credentials: Follow CREDENTIAL_ROTATION_GUIDE.md")
            print("2. Fix format issues: Use the generation commands shown above")
            print("3. Update 1Password: Ensure credentials are stored correctly")
            print("4. Re-run validation: python3 scripts/validate_secrets.py")
            return False

    def validate_secrets_file(self) -> bool:
        """Validate secrets file (alias for run_validation)"""
        return self.run_validation()


def main():
    """Main entry point"""
    transition_mode = False

    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("""
ESPHome Secrets Validation Script

This script validates the secrets.yaml file format and 1Password integration.

Usage:
    python3 scripts/validate_secrets.py [--transition]

Options:
    --transition    Allow old credentials during rotation (transition mode)

The script will:
1. Check if secrets.yaml exists
2. Validate credential formats (API key, OTA password, fallback password)
3. Validate WiFi credentials
4. Test 1Password integration
5. Scan for exposed credentials in YAML files

Prerequisites:
- secrets.yaml file (generate with: ./scripts/generate_secrets.sh)
- 1Password CLI installed and authenticated (optional)
- OP_ACCOUNT environment variable set (if using 1Password)

For more information, see SECURITY.md
            """)
            return
        elif sys.argv[1] == '--transition':
            transition_mode = True

    validator = SecretsValidator(transition_mode=transition_mode)
    success = validator.run_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
