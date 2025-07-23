#!/usr/bin/env python3
"""
1Password Structure Validation Script

Validates that 1Password vaults and items are properly configured for ESPHome.
Python conversion of validate-1password-structure.sh using the shared security library.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import (
    SecurityLogger,
    SecurityConfig,
    CredentialValidator,
    OnePasswordManager,
    CredentialGenerator,
    check_required_tools
)


class OnePasswordStructureValidator:
    """Main 1Password structure validation class"""

    def __init__(self):
        self.logger = SecurityLogger("validate_1password")
        self.validator = CredentialValidator()
        self.generator = CredentialGenerator()
        self.total_errors = 0

    def check_op_cli(self) -> bool:
        """Check if 1Password CLI is installed"""
        available, missing = check_required_tools(['op'])
        if not available:
            self.logger.error("1Password CLI not found")
            self.logger.info("Install from: https://developer.1password.com/docs/cli/get-started/")
            return False

        self.logger.success("1Password CLI found")
        return True

    def check_account_access(self) -> bool:
        """Check account access"""
        self.logger.info("Checking 1Password account access...")

        try:
            op_manager = OnePasswordManager()
        except ValueError as e:
            self.logger.error(str(e))
            self.logger.info("Set with: export OP_ACCOUNT=your-account-name")
            self.logger.info("Or sign in with: op signin")
            return False

        if not op_manager.check_cli_available():
            self.logger.error(f"Cannot access 1Password account '{op_manager.account}'")
            self.logger.info("Sign in with: op signin")
            self.logger.info("Add account with: op account add --address my.1password.com --email your@email.com")
            return False

        if not op_manager.check_account_access():
            self.logger.error(f"Cannot access 1Password account '{op_manager.account}'")
            self.logger.info("Sign in with: op signin")
            return False

        self.logger.success(f"Account '{op_manager.account}' is accessible")
        return True

    def check_vault_access(self, vault_name: str, vault_description: str) -> bool:
        """Check vault access"""
        self.logger.info(f"Checking access to '{vault_name}' vault...")

        try:
            op_manager = OnePasswordManager()
            if not op_manager.check_vault_access(vault_name):
                self.logger.error(f"Vault '{vault_name}' not found or not accessible")
                self.logger.info("Available vaults:")
                try:
                    result = subprocess.run([
                        'op', 'vault', 'list', f'--account={op_manager.account}'
                    ], check=True, capture_output=True, text=True)
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            self.logger.info(f"  {line}")
                except subprocess.CalledProcessError:
                    self.logger.error("Cannot list vaults")
                return False

            self.logger.success(f"Vault '{vault_name}' ({vault_description}) is accessible")
            return True
        except ValueError:
            return False

    def check_item_structure(self, vault_name: str, item_name: str, expected_fields: list) -> bool:
        """Check item access and structure"""
        self.logger.info(f"Checking '{item_name}' item in '{vault_name}' vault...")

        try:
            op_manager = OnePasswordManager()

            # Check if item exists
            if not op_manager.check_item_access(vault_name, item_name):
                self.logger.error(f"Item '{item_name}' not found in vault '{vault_name}'")
                self.logger.info(f"Available items in '{vault_name}':")
                try:
                    result = subprocess.run([
                        'op', 'item', 'list', f'--vault={vault_name}',
                        f'--account={op_manager.account}'
                    ], check=True, capture_output=True, text=True)
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            self.logger.info(f"  {line}")
                except subprocess.CalledProcessError:
                    self.logger.error("Cannot list items")
                return False

            self.logger.success(f"Item '{item_name}' found in vault '{vault_name}'")

            # Check expected fields
            missing_fields = 0
            for field in expected_fields:
                field = field.strip()
                self.logger.info(f"Checking field '{field}'...")

                value = op_manager.get_item_field(vault_name, item_name, field)
                if value is not None:
                    self.logger.success(f"Field '{field}' exists")
                else:
                    self.logger.error(f"Field '{field}' missing or inaccessible")
                    missing_fields += 1

            return missing_fields == 0
        except ValueError:
            return False

    def validate_field_values(self, vault_name: str, item_name: str) -> bool:
        """Validate field values"""
        self.logger.info(f"Validating field values in '{item_name}'...")

        try:
            op_manager = OnePasswordManager()
            errors = 0

            # Get all ESPHome credentials
            credentials = op_manager.get_esphome_credentials()
            if not credentials:
                self.logger.error("Failed to retrieve ESPHome credentials")
                return False

            # Validate each credential
            for cred_type, cred_value in credentials.items():
                if cred_type == 'api_key':
                    valid, msg = self.validator.validate_api_key(cred_value)
                elif cred_type == 'ota_password':
                    valid, msg = self.validator.validate_ota_password(cred_value)
                elif cred_type == 'fallback_password':
                    valid, msg = self.validator.validate_fallback_password(cred_value)
                else:
                    continue

                if valid:
                    if "exposed credential" not in msg:
                        self.logger.success(f"{cred_type.replace('_', ' ').title()} format is valid and not exposed")
                    else:
                        self.logger.error(f"{cred_type.replace('_', ' ').title()} {msg}")
                        errors += 1
                else:
                    self.logger.error(f"{cred_type.replace('_', ' ').title()} {msg}")
                    errors += 1

            return errors == 0
        except ValueError:
            return False

    def test_credential_generation(self) -> bool:
        """Test credential generation"""
        self.logger.info("Testing credential generation commands...")

        errors = 0

        # Test API key generation
        self.logger.info("Testing API key generation...")
        try:
            test_api_key = self.generator.generate_api_key()
            valid, msg = self.validator.validate_api_key(test_api_key)
            if valid:
                self.logger.success("API key generation works correctly")
            else:
                self.logger.error(f"API key generation failed: {msg}")
                errors += 1
        except Exception as e:
            self.logger.error(f"API key generation failed: {e}")
            errors += 1

        # Test OTA password generation
        self.logger.info("Testing OTA password generation...")
        try:
            test_ota_password = self.generator.generate_ota_password()
            valid, msg = self.validator.validate_ota_password(test_ota_password)
            if valid:
                self.logger.success("OTA password generation works correctly")
            else:
                self.logger.error(f"OTA password generation failed: {msg}")
                errors += 1
        except Exception as e:
            self.logger.error(f"OTA password generation failed: {e}")
            errors += 1

        # Test fallback password generation
        self.logger.info("Testing fallback password generation...")
        try:
            test_fallback_password = self.generator.generate_fallback_password()
            valid, msg = self.validator.validate_fallback_password(test_fallback_password)
            if valid:
                self.logger.success("Fallback password generation works correctly")
            else:
                self.logger.error(f"Fallback password generation failed: {msg}")
                errors += 1
        except Exception as e:
            self.logger.error(f"Fallback password generation failed: {e}")
            errors += 1

        return errors == 0

    def test_secrets_generation(self) -> bool:
        """Test secrets generation script"""
        self.logger.info("Testing secrets generation script...")

        if not os.path.exists("scripts/generate_secrets.sh"):
            self.logger.error("scripts/generate_secrets.sh not found")
            return False

        # Check if script is executable
        script_path = Path("scripts/generate_secrets.sh")
        if not os.access(script_path, os.X_OK):
            self.logger.warning("scripts/generate_secrets.sh is not executable")
            script_path.chmod(0o755)
            self.logger.info("Made scripts/generate_secrets.sh executable")

        # Backup existing secrets if they exist
        backup_created = False
        if os.path.exists("secrets.yaml"):
            import shutil
            shutil.copy2("secrets.yaml", "secrets.yaml.backup.validation")
            self.logger.info("Backed up existing secrets.yaml")
            backup_created = True

        # Test generation
        try:
            result = subprocess.run([
                './scripts/generate_secrets.sh'
            ], check=True, capture_output=True, text=True)
            self.logger.success("Secrets generation script works correctly")
            success = True
        except subprocess.CalledProcessError as e:
            self.logger.error("Secrets generation script failed")
            self.logger.error(f"Error: {e}")
            if e.stdout:
                self.logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                self.logger.error(f"STDERR: {e.stderr}")
            success = False
        finally:
            # Restore backup if it existed
            if backup_created:
                import shutil
                shutil.move("secrets.yaml.backup.validation", "secrets.yaml")
                self.logger.info("Restored original secrets.yaml")

        return success

    def run_validation(self) -> bool:
        """Run complete 1Password structure validation"""
        self.logger.header("1Password Structure Validation")

        # Check 1Password CLI
        if not self.check_op_cli():
            return False

        # Check account access
        if not self.check_account_access():
            self.total_errors += 1

        # Check vault access
        if not self.check_vault_access("Shared", "Home IoT credentials"):
            self.total_errors += 1

        if not self.check_vault_access("Automation", "ESPHome credentials"):
            self.total_errors += 1

        # Check item structures
        home_iot_fields = ["network name", "wireless network password", "domain name"]
        if not self.check_item_structure("Shared", "Home IoT", home_iot_fields):
            self.total_errors += 1

        esphome_fields = ["api_key", "ota_password", "fallback_password"]
        if not self.check_item_structure("Automation", "ESPHome", esphome_fields):
            self.total_errors += 1

        # Validate field values
        if not self.validate_field_values("Automation", "ESPHome"):
            self.total_errors += 1

        # Test credential generation
        if not self.test_credential_generation():
            self.total_errors += 1

        # Test secrets generation script
        if not self.test_secrets_generation():
            self.total_errors += 1

        # Print results
        print()
        print("=" * 50)
        if self.total_errors == 0:
            self.logger.success("All 1Password validations passed!")
            print("=" * 50)
            print()
            print("1Password structure is correctly configured:")
            print("• Account is accessible")
            print("• Vault 'Shared' contains 'Home IoT' item with WiFi credentials")
            print("• Vault 'Automation' contains 'ESPHome' item with device credentials")
            print("• All required fields are present and properly formatted")
            print("• Credential generation commands work correctly")
            print("• Secrets generation script is functional")
            return True
        else:
            self.logger.error(f"1Password validation failed with {self.total_errors} error(s)")
            print("=" * 50)
            print()
            print("To fix issues:")
            print("1. Install 1Password CLI: https://developer.1password.com/docs/cli/get-started/")
            print("2. Sign in: op signin")
            print("3. Create required vaults and items as documented in secrets.yaml.example")
            print("4. Rotate exposed credentials: Follow CREDENTIAL_ROTATION_GUIDE.md")
            print("5. Re-run validation: python3 scripts/validate_1password_structure.py")
            return False


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
1Password Structure Validation Script

This script validates that 1Password vaults and items are properly configured for ESPHome.

Usage:
    python3 scripts/validate_1password_structure.py

The script will:
1. Check if 1Password CLI is installed
2. Verify account access
3. Check vault access (Shared and Automation)
4. Validate item structures and required fields
5. Test credential formats and detect exposed credentials
6. Test credential generation functions
7. Verify secrets generation script functionality

Prerequisites:
- 1Password CLI installed
- OP_ACCOUNT environment variable set
- Proper vault and item structure in 1Password
- Authentication with 1Password CLI (op signin)

For more information, see SECURITY.md
        """)
        return

    validator = OnePasswordStructureValidator()
    success = validator.run_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
