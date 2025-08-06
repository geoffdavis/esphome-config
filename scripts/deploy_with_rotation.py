#!/usr/bin/env python3
"""
ESPHome Deployment with Credential Rotation Support

This script handles two-stage deployment during credential rotation by:
1. Using old_ota_password for initial authentication when needed
2. Deploying with new credentials
3. Automatically switching between credential sets as needed
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import (
    SecurityLogger,
    SecureFileHandler
)


class RotationDeployer:
    """Handles deployment during credential rotation"""

    def __init__(self):
        self.logger = SecurityLogger("deploy_rotation")
        self.file_handler = SecureFileHandler()

    def create_auth_secrets(self):
        """Create temporary secrets file with old OTA password for authentication"""
        secrets = self.file_handler.read_secrets_file()
        if not secrets:
            self.logger.error("Could not read current secrets.yaml")
            return None

        if 'old_ota_password' not in secrets:
            self.logger.error("old_ota_password not found in secrets.yaml")
            return None

        # Create auth version with old OTA password
        auth_secrets = secrets.copy()
        auth_secrets['ota_password'] = secrets['old_ota_password']

        # Write to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        try:
            self.file_handler.write_yaml_file(temp_file.name, auth_secrets)
            self.logger.info(f"Created auth secrets with old OTA password: {secrets['old_ota_password'][:8]}...")
            return temp_file.name
        except Exception as e:
            self.logger.error(f"Failed to create auth secrets file: {e}")
            return None

    def backup_current_secrets(self):
        """Backup current secrets.yaml"""
        if os.path.exists("secrets.yaml"):
            backup_path = "secrets.yaml.deploy_backup"
            shutil.copy2("secrets.yaml", backup_path)
            self.logger.info(f"Backed up secrets.yaml to {backup_path}")
            return backup_path
        return None

    def restore_secrets(self, backup_path):
        """Restore secrets.yaml from backup"""
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, "secrets.yaml")
            os.remove(backup_path)
            self.logger.info("Restored original secrets.yaml")

    def get_config_file(self, device, config_file=None):
        """Get the appropriate config file for a device"""
        if config_file:
            return config_file
        elif os.path.exists(f"{device}-full.yaml"):
            return f"{device}-full.yaml"
        else:
            return f"{device}.yaml"

    def run_esphome_command(self, command, device, config_file=None):
        """Run ESPHome command with error handling"""
        config = self.get_config_file(device, config_file)
        cmd = ["esphome", command, config]

        self.logger.info(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.logger.success(f"ESPHome {command} successful")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                # Check for specific error patterns
                error_output = result.stderr + result.stdout

                if "Error resolving IP address" in error_output or "Network is unreachable" in error_output:
                    self.logger.warning(f"Device {device} is offline, skipping")
                    return False
                elif "Authentication failed" in error_output or "Invalid password" in error_output:
                    self.logger.error(f"Authentication failed for {device}")
                    return False
                else:
                    self.logger.error(f"ESPHome {command} failed:")
                    print(error_output)
                    return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"ESPHome {command} timed out after 5 minutes")
            return False
        except Exception as e:
            self.logger.error(f"Failed to run ESPHome {command}: {e}")
            return False

    def deploy_device(self, device):
        """Deploy to a single device with credential rotation support"""
        self.logger.info(f"Starting deployment to {device}")

        # Backup current secrets
        backup_path = self.backup_current_secrets()

        try:
            # Step 1: Upload minimal firmware first (if it exists) to establish connectivity
            if os.path.exists(f"{device}-minimal.yaml"):
                self.logger.info("Step 1: Compiling and uploading minimal firmware first")
                if not self.run_esphome_command("compile", device, f"{device}-minimal.yaml"):
                    self.logger.error(f"Failed to compile minimal firmware for {device}")
                    return False

                if not self.run_esphome_command("upload", device, f"{device}-minimal.yaml"):
                    self.logger.info("Minimal upload failed, trying with old credentials")

                    # Try with old credentials for authentication
                    auth_secrets_path = self.create_auth_secrets()
                    if not auth_secrets_path:
                        return False

                    try:
                        # Replace secrets.yaml temporarily
                        shutil.copy2(auth_secrets_path, "secrets.yaml")

                        # Try minimal upload with old credentials
                        if not self.run_esphome_command("upload", device, f"{device}-minimal.yaml"):
                            self.logger.error(f"Failed to upload minimal firmware to {device} with old credentials")
                            return False

                    finally:
                        # Clean up auth secrets
                        os.remove(auth_secrets_path)
                        # Restore original secrets for full deployment
                        if backup_path:
                            shutil.copy2(backup_path, "secrets.yaml")

                self.logger.success("Minimal firmware uploaded successfully")

            # Step 2: Compile and upload full firmware with new credentials
            self.logger.info("Step 2: Compiling and uploading full firmware")
            if not self.run_esphome_command("compile", device):
                self.logger.error(f"Failed to compile full firmware for {device}")
                return False

            if not self.run_esphome_command("upload", device):
                # If full upload fails, try with old credentials for auth
                self.logger.info("Full upload failed, trying with old credentials for authentication")

                auth_secrets_path = self.create_auth_secrets()
                if not auth_secrets_path:
                    return False

                try:
                    # Replace secrets.yaml temporarily for authentication
                    shutil.copy2(auth_secrets_path, "secrets.yaml")

                    # Try upload with old credentials
                    if not self.run_esphome_command("upload", device):
                        self.logger.error(f"Failed to upload full firmware to {device}")
                        return False

                finally:
                    # Clean up
                    os.remove(auth_secrets_path)

            self.logger.success(f"Successfully deployed to {device}")
            return True

        finally:
            # Always restore original secrets
            self.restore_secrets(backup_path)

    def deploy_all_devices(self):
        """Deploy to all devices"""
        # Get list of actual ESPHome device YAML files
        try:
            import glob

            # Find all .yaml files
            yaml_files = glob.glob("*.yaml")

            # Filter out non-device files
            excluded_patterns = [
                'secrets', 'common', 'package', 'requirements', 'renovate',
                'Taskfile', 'README', 'SECURITY', 'MIGRATION', 'CREDENTIAL',
                'PYTHON_SECURITY', 'FRAMEWORK', 'deployment'
            ]

            device_files = []
            for file in yaml_files:
                # Skip files that match excluded patterns
                if any(pattern in file for pattern in excluded_patterns):
                    continue
                # Skip backup files
                if '.backup' in file or '.old' in file or '.example' in file:
                    continue
                device_files.append(file)

            if not device_files:
                self.logger.error("No device YAML files found")
                return False

            # Parse device names
            devices = set()
            for file in device_files:
                device = file.replace('.yaml', '').replace('-full', '').replace('-minimal', '')
                devices.add(device)

            devices = sorted(list(devices))
            self.logger.info(f"Found {len(devices)} devices: {', '.join(devices)}")

            success_count = 0
            for device in devices:
                if self.deploy_device(device):
                    success_count += 1
                else:
                    self.logger.warning(f"Deployment to {device} failed or skipped")

            self.logger.info(f"Deployment complete: {success_count}/{len(devices)} devices successful")
            return success_count == len(devices)

        except Exception as e:
            self.logger.error(f"Failed to get device list: {e}")
            return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("""
ESPHome Deployment with Credential Rotation Support

Usage:
    python3 scripts/deploy_with_rotation.py <device_name>
    python3 scripts/deploy_with_rotation.py --all

This script handles deployment during credential rotation by:
1. Reading both 'ota_password' and 'old_ota_password' from secrets.yaml
2. Attempting deployment with current credentials first
3. Falling back to old credentials for authentication if needed
4. Always deploying new credentials to the device

Examples:
    python3 scripts/deploy_with_rotation.py washer
    python3 scripts/deploy_with_rotation.py --all

Requirements:
    - secrets.yaml must contain both 'ota_password' and 'old_ota_password' fields
    - ESPHome must be available in PATH
        """)
        sys.exit(1)

    deployer = RotationDeployer()

    if sys.argv[1] == "--all":
        success = deployer.deploy_all_devices()
    else:
        device = sys.argv[1]
        success = deployer.deploy_device(device)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
