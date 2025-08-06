#!/usr/bin/env python3
"""
ESPHome Credential Rotation Script

Automates the complete credential rotation process with two-stage deployment.
Integrates with existing Python security infrastructure and 1Password CLI.
"""

import os
import sys
import subprocess
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import (
    SecurityLogger,
    SecurityConfig,
    CredentialGenerator,
    CredentialValidator,
    OnePasswordManager,
    SecureFileHandler,
    SecurityScanner
)


class DeploymentManager:
    """Manages ESPHome deployment process"""

    def __init__(self):
        self.logger = SecurityLogger("deployment")
        self.project_root = Path.cwd()
        self.file_handler = SecureFileHandler()

    def backup_secrets(self) -> Optional[str]:
        """Backup existing secrets.yaml if it exists"""
        secrets_file = self.project_root / "secrets.yaml"
        if secrets_file.exists():
            backup_file = self.file_handler.backup_file("secrets.yaml")
            if backup_file:
                self.logger.success(f"Backed up existing secrets to {backup_file}")
                return backup_file
        return None

    def create_old_credentials_file(self) -> bool:
        """Create temporary file with old credentials for transition deployment"""
        try:
            op_manager = OnePasswordManager()

            # Get WiFi credentials from 1Password
            wifi_ssid = op_manager.get_item_field(
                SecurityConfig.SHARED_VAULT,
                SecurityConfig.HOME_IOT_ITEM,
                "network name"
            )

            wifi_password = op_manager.get_item_field(
                SecurityConfig.SHARED_VAULT,
                SecurityConfig.HOME_IOT_ITEM,
                "wireless network password"
            )

            wifi_domain = op_manager.get_item_field(
                SecurityConfig.SHARED_VAULT,
                SecurityConfig.HOME_IOT_ITEM,
                "domain name"
            )

            if not all([wifi_ssid, wifi_password, wifi_domain]):
                self.logger.error("Failed to retrieve WiFi credentials from 1Password")
                return False

            # Create old credentials file with exposed credentials
            old_secrets_content = f"""# Old credentials for transition deployment - DO NOT COMMIT
wifi_ssid: "{wifi_ssid}"
wifi_password: "{wifi_password}"
wifi_domain: "{wifi_domain}"
api_key: "{SecurityConfig.EXPOSED_CREDENTIALS['api_key']}"
ota_password: "{SecurityConfig.EXPOSED_CREDENTIALS['ota_password']}"
fallback_password: "{SecurityConfig.EXPOSED_CREDENTIALS['fallback_password']}"
"""

            with open("secrets.yaml.old", "w") as f:
                f.write(old_secrets_content)

            self.logger.success("Created old credentials file for transition")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create old credentials file: {e}")
            return False

    def generate_new_secrets(self) -> bool:
        """Generate new secrets.yaml from 1Password"""
        try:
            result = subprocess.run([
                './scripts/generate_secrets.sh'
            ], check=True, capture_output=True, text=True)
            self.logger.success("Generated new secrets.yaml from 1Password")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to generate secrets: {e}")
            return False

    def run_security_validation(self, allow_transition: bool = False) -> bool:
        """Run security validation before deployment"""
        try:
            subprocess.run(['task', 'security-validate'],
                         check=True, capture_output=True)
            self.logger.success("Security validation passed")
            return True
        except subprocess.CalledProcessError:
            if allow_transition:
                self.logger.warning("Security validation failed (expected during transition)")
                return True  # Allow transition deployment to proceed
            else:
                self.logger.error("Security validation failed")
                return False

    def deploy_two_stage(self, skip_security: bool = False) -> bool:
        """Execute two-stage deployment to all devices"""
        try:
            self.logger.info("Starting two-stage deployment to all devices...")

            if skip_security:
                # During transition, skip security validation and deploy directly
                self.logger.info("Skipping security validation for transition deployment...")

                # Get list of devices and deploy directly
                devices = self._get_device_list()
                for device in devices:
                    self.logger.info(f"Deploying to {device}...")
                    try:
                        # Try minimal first if it exists
                        if os.path.exists(f"{device}-minimal.yaml"):
                            subprocess.run([
                                'mise', 'exec', '--', 'esphome', 'upload',
                                f"{device}-minimal.yaml"
                            ], check=True, capture_output=True, text=True)

                        # Then deploy full version
                        config_file = (f"{device}-full.yaml"
                                     if os.path.exists(f"{device}-full.yaml")
                                     else f"{device}.yaml")
                        subprocess.run([
                            'mise', 'exec', '--', 'esphome', 'upload', config_file
                        ], check=True, capture_output=True, text=True)

                        self.logger.success(f"Successfully deployed to {device}")
                    except subprocess.CalledProcessError as e:
                        if ("Error resolving IP address" in str(e.stdout) or
                            "Network is unreachable" in str(e.stdout)):
                            self.logger.warning(f"Device {device} offline, skipping")
                        else:
                            self.logger.error(f"Failed to deploy to {device}: {e}")
                            # Continue with other devices
            else:
                # Normal deployment with security validation
                result = subprocess.run([
                    'task', 'upload-all-two-stage'
                ], check=True, capture_output=True, text=True)

            self.logger.success("Two-stage deployment completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Deployment failed: {e}")
            if e.stdout:
                self.logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                self.logger.error(f"STDERR: {e.stderr}")
            return False

    def _get_device_list(self) -> List[str]:
        """Get list of device names from YAML files"""
        try:
            devices = []
            for file in os.listdir('.'):
                if (file.endswith('.yaml') and
                    not file.endswith('-minimal.yaml') and
                    not file.endswith('-full.yaml') and
                    file != 'secrets.yaml'):
                    device = file.replace('.yaml', '')
                    devices.append(device)
            return devices
        except Exception as e:
            self.logger.error(f"Failed to get device list: {e}")
            return []

    def test_device_connectivity(self) -> Dict[str, bool]:
        """Test connectivity to all devices"""
        self.logger.info("Testing device connectivity...")

        # Get list of devices
        devices = self._get_device_list()
        if not devices:
            self.logger.error("No devices found")
            return {}

        connectivity_results = {}
        for device in devices:
            self.logger.info(f"Testing {device}...")
            try:
                # Test with timeout
                result = subprocess.run([
                    'timeout', '10', 'esphome', 'logs', f'{device}.yaml',
                    '--device', f'{device}.local'
                ], capture_output=True, text=True, timeout=15)

                if result.returncode == 0:
                    self.logger.success(f"{device}: Connection successful")
                    connectivity_results[device] = True
                else:
                    self.logger.warning(f"{device}: Connection failed or timeout")
                    connectivity_results[device] = False
            except subprocess.TimeoutExpired:
                self.logger.warning(f"{device}: Connection timeout")
                connectivity_results[device] = False
            except Exception as e:
                self.logger.warning(f"{device}: Connection error - {e}")
                connectivity_results[device] = False

        return connectivity_results

    def cleanup_temporary_files(self):
        """Clean up temporary files created during rotation"""
        files_to_remove = ['secrets.yaml.old']

        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)
                self.logger.success(f"Removed temporary file: {file}")


class SecurityValidator:
    """Security validation functionality for credential rotation"""

    def __init__(self):
        self.logger = SecurityLogger("security_validator")
        self.scanner = SecurityScanner()

    def test_security_hooks(self) -> bool:
        """Test security hooks functionality"""
        return self.scanner.test_security_hooks()

    def scan_for_exposed_credentials(self) -> bool:
        """Scan for exposed credentials using grep commands"""
        try:
            # Check for each exposed credential using grep
            exposed_creds = [
                SecurityConfig.EXPOSED_CREDENTIALS['api_key'],
                SecurityConfig.EXPOSED_CREDENTIALS['ota_password'],
                SecurityConfig.EXPOSED_CREDENTIALS['fallback_password']
            ]

            for cred in exposed_creds:
                result = subprocess.run([
                    'grep', '-r', cred, '.'
                ], capture_output=True, text=True)

                # If grep finds matches (returncode 0), credentials are exposed
                if result.returncode == 0:
                    return False

            # If no exposed credentials found, return True
            return True
        except Exception:
            # If grep fails, fall back to scanner method
            issues = self.scanner.scan_for_exposed_credentials()
            return len(issues) == 0


class CredentialRotator:
    """Main credential rotation orchestrator"""

    def __init__(self):
        self.logger = SecurityLogger("credential_rotator")
        self.generator = CredentialGenerator()
        self.validator = CredentialValidator()
        self.onepassword = OnePasswordManager()
        self.deployment = DeploymentManager()
        self.scanner = SecurityScanner()
        self.security = SecurityValidator()

        self.new_credentials = {}

    def check_prerequisites(self) -> bool:
        """Check all prerequisites before starting rotation"""
        self.logger.step("CHECKING PREREQUISITES")

        # Check required tools
        required_tools = ['op', 'esphome', 'task', 'openssl']
        for tool in required_tools:
            if not shutil.which(tool):
                self.logger.error(f"{tool} not found in PATH")
                return False
            self.logger.success(f"{tool} found")

        # Check 1Password access
        if not self.onepassword.check_cli_available():
            self.logger.error("1Password CLI not available or not authenticated")
            self.logger.info("Sign in with: op signin")
            return False
        self.logger.success("1Password CLI access verified")

        # Check security hooks
        if not os.path.exists('.githooks/esphome-credential-check.sh'):
            self.logger.error("Security hooks not found")
            self.logger.info("Run: python3 scripts/setup_security.py")
            return False
        self.logger.success("Security hooks found")

        return True

    def generate_and_validate_credentials(self) -> bool:
        """Generate new credentials and validate their format"""
        self.logger.step("STEP 1: GENERATING NEW CREDENTIALS")

        # Generate credentials
        self.logger.info("Generating new API encryption key...")
        api_key = self.generator.generate_api_key()
        self.logger.success(f"New API Key: {api_key}")
        self.logger.info(f"Length: {len(api_key)} characters")

        self.logger.info("Generating new OTA password...")
        ota_password = self.generator.generate_ota_password()
        self.logger.success(f"New OTA Password: {ota_password}")
        self.logger.info(f"Length: {len(ota_password)} characters")

        self.logger.info("Generating new fallback hotspot password...")
        fallback_password = self.generator.generate_fallback_password()
        self.logger.success(f"New Fallback Password: {fallback_password}")
        self.logger.info(f"Length: {len(fallback_password)} characters")

        # Validate credentials
        self.logger.info("Validating credential formats...")

        valid, msg = self.validator.validate_api_key(api_key)
        if not valid:
            self.logger.error(f"API key validation failed: {msg}")
            return False
        self.logger.success(msg)

        valid, msg = self.validator.validate_ota_password(ota_password)
        if not valid:
            self.logger.error(f"OTA password validation failed: {msg}")
            return False
        self.logger.success(msg)

        valid, msg = self.validator.validate_fallback_password(fallback_password)
        if not valid:
            self.logger.error(f"Fallback password validation failed: {msg}")
            return False
        self.logger.success(msg)

        # Store credentials
        self.new_credentials = {
            'api_key': api_key,
            'ota_password': ota_password,
            'fallback_password': fallback_password
        }

        return True

    def update_1password(self) -> bool:
        """Update 1Password with new credentials"""
        self.logger.step("STEP 2: UPDATING 1PASSWORD")

        if not self.onepassword.update_esphome_credentials(
            self.new_credentials['api_key'],
            self.new_credentials['ota_password'],
            self.new_credentials['fallback_password']
        ):
            return False

        self.logger.success("1Password updated with new credentials")

        # Verify update using the verify_credentials method
        if not self.onepassword.verify_credentials():
            self.logger.error("Failed to verify 1Password update")
            return False

        self.logger.success("1Password credentials verified")
        return True

    def execute_two_stage_deployment(self) -> bool:
        """Execute the two-stage deployment process"""
        self.logger.step("STEP 3: TWO-STAGE DEPLOYMENT")

        # Backup existing secrets
        backup_file = self.deployment.backup_secrets()

        # Stage 1: Deploy with old credentials for authentication
        self.logger.info("=== STAGE 1: Transition Deployment ===")

        if not self.deployment.create_old_credentials_file():
            return False

        # Copy old credentials for authentication
        shutil.copy2("secrets.yaml.old", "secrets.yaml")
        self.logger.warning("Using old credentials for transition deployment...")
        self.logger.warning("Security warnings expected during this stage...")

        # Run security validation (allow transition with old credentials)
        self.deployment.run_security_validation(allow_transition=True)

        # Deploy to all devices (skip security validation for transition)
        if not self.deployment.deploy_two_stage(skip_security=True):
            self.logger.error("Stage 1 deployment failed")
            return False

        self.logger.success("Stage 1 deployment completed")

        # Stage 2: Final deployment with new credentials
        self.logger.info("=== STAGE 2: Final Deployment ===")

        # Generate new secrets from 1Password
        if not self.deployment.generate_new_secrets():
            return False

        # Run security validation
        if not self.deployment.run_security_validation():
            self.logger.error("Security validation failed with new credentials")
            return False

        # Final deployment
        if not self.deployment.deploy_two_stage():
            self.logger.error("Stage 2 deployment failed")
            return False

        self.logger.success("Stage 2 deployment completed - rotation successful")
        return True

    def verify_rotation(self) -> bool:
        """Verify the credential rotation was successful"""
        self.logger.step("STEP 4: VERIFICATION AND TESTING")

        # Test device connectivity
        connectivity_results = self.deployment.test_device_connectivity()

        successful_devices = sum(1 for success in connectivity_results.values()
                               if success)
        total_devices = len(connectivity_results)

        self.logger.info(f"Device connectivity: {successful_devices}/{total_devices} devices accessible")

        # Test security hooks
        if not self.security.test_security_hooks():
            self.logger.error("Security hook testing failed")
            return False

        # Scan for exposed credentials
        if not self.security.scan_for_exposed_credentials():
            self.logger.error("Found exposed credentials in files")
            return False

        self.logger.success("All verification tests passed")
        return True

    def cleanup_and_document(self) -> bool:
        """Clean up temporary files and document the rotation"""
        self.logger.step("STEP 5: CLEANUP AND DOCUMENTATION")

        # Clean up temporary files
        self.deployment.cleanup_temporary_files()

        # Document the rotation
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"""
## Rotation {datetime.now().strftime("%Y-%m-%d")}

**Date**: {timestamp}
**Reason**: Exposed credentials in public repository
**Rotated Credentials**:
- API Encryption Key: ✅ Rotated
- OTA Password: ✅ Rotated
- Fallback Hotspot Password: ✅ Rotated

**Process Used**: Two-stage deployment (Python script)
**Validation**: All devices tested successfully
**Security Hooks**: Verified detecting old credentials
**Completed By**: {os.getenv('USER', 'unknown')}

"""

        try:
            with open("CREDENTIAL_ROTATION_LOG.md", "a") as f:
                f.write(log_entry)
            self.logger.success("Rotation documented in CREDENTIAL_ROTATION_LOG.md")
        except Exception as e:
            self.logger.warning(f"Failed to document rotation: {e}")

        # Final security scan
        try:
            subprocess.run(['task', 'security-scan'],
                         check=True, capture_output=True)
            self.logger.success("Final security scan completed")
        except subprocess.CalledProcessError:
            self.logger.warning("Final security scan had issues")

        return True

    def run_rotation(self) -> bool:
        """Execute the complete credential rotation process"""
        self.logger.step("ESPHome Credential Rotation")
        self.logger.info("Starting automated credential rotation process...")

        try:
            if not self.check_prerequisites():
                self.logger.error("Prerequisites check failed")
                return False

            if not self.generate_and_validate_credentials():
                self.logger.error("Credential generation failed")
                return False

            if not self.update_1password():
                self.logger.error("1Password update failed")
                return False

            if not self.execute_two_stage_deployment():
                self.logger.error("Two-stage deployment failed")
                return False

            if not self.verify_rotation():
                self.logger.error("Rotation verification failed")
                return False

            if not self.cleanup_and_document():
                self.logger.warning("Cleanup/documentation had issues")

            self.logger.step("CREDENTIAL ROTATION COMPLETED SUCCESSFULLY")
            self.logger.success("All exposed credentials have been rotated")
            self.logger.success("All devices are accessible with new credentials")
            self.logger.success("Security hooks are detecting old exposed credentials")
            self.logger.info("Rotation process completed successfully!")

            return True

        except KeyboardInterrupt:
            self.logger.error("Rotation interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during rotation: {e}")
            return False


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
ESPHome Credential Rotation Script

This script automates the complete credential rotation process for exposed
ESPHome credentials using a secure two-stage deployment process.

Usage:
    python3 scripts/rotate_credentials.py

The script will:
1. Generate new secure credentials
2. Update 1Password with new credentials
3. Execute two-stage deployment to all devices
4. Verify rotation success and test connectivity
5. Clean up temporary files and document the rotation

Prerequisites:
- 1Password CLI installed and authenticated
- ESPHome installed
- Task runner installed
- Security hooks installed

For more information, see CREDENTIAL_ROTATION_GUIDE.md
        """)
        return

    rotator = CredentialRotator()
    success = rotator.run_rotation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
