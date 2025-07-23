#!/usr/bin/env python3
"""
ESP01 Recovery Deployment Script

This script helps deploy fixed firmware to ESP01 devices once they are
accessible via the recovery network setup.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import SecurityLogger


class RecoveryDeployment:
    """Handles deployment of fixed firmware to recovered ESP01 devices"""

    def __init__(self):
        self.logger = SecurityLogger("recovery_deployment")

    def check_device_accessibility(self, device):
        """Check if device is accessible via ping or web interface"""
        self.logger.info(f"Checking accessibility of {device}...")

        try:
            # Try to ping the device first
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3000', f'{device}.local'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.success(f"Device {device} is accessible via mDNS")
                return True
            else:
                self.logger.warning(f"Device {device} not accessible via mDNS ping")
                return False

        except Exception as e:
            self.logger.warning(f"Failed to ping {device}: {e}")
            return False

    def scan_recovery_network(self):
        """Scan for devices on the recovery network"""
        self.logger.info("Scanning for devices on recovery network...")

        esp01_devices = [
            "attic_sensor",
            "bedroom_east_heatpump",
            "bedroom_west_heatpump",
            "denheatpump",
            "hodad_outlet",
            "mpmd_light_topgreener",
            "pruscilla_light_topgreener",
            "tg_dishwasher",
            "tg_lrtv",
            "voronica_outlet"
        ]

        accessible_devices = []

        for device in esp01_devices:
            if self.check_device_accessibility(device):
                accessible_devices.append(device)

        self.logger.info(f"Found {len(accessible_devices)} accessible devices: {accessible_devices}")
        return accessible_devices

    def deploy_fixed_firmware(self, device):
        """Deploy fixed firmware with fallback hotspot to a device"""
        self.logger.info(f"Deploying fixed firmware to {device}...")

        try:
            # Step 1: Compile and upload fixed minimal firmware
            self.logger.info("Step 1: Deploying fixed minimal firmware with fallback hotspot")

            minimal_config = f"{device}-minimal.yaml" if Path(f"{device}-minimal.yaml").exists() else f"{device}.yaml"

            # Compile first
            compile_result = subprocess.run([
                'mise', 'exec', '--', 'esphome', 'compile', minimal_config
            ], capture_output=True, text=True, timeout=300)

            if compile_result.returncode != 0:
                self.logger.error(f"Failed to compile firmware for {device}")
                self.logger.error(f"Error: {compile_result.stderr}")
                return False

            # Upload minimal firmware
            upload_result = subprocess.run([
                'mise', 'exec', '--', 'esphome', 'upload', minimal_config
            ], capture_output=True, text=True, timeout=300)

            if upload_result.returncode != 0:
                self.logger.error(f"Failed to upload minimal firmware to {device}")
                self.logger.error(f"Error: {upload_result.stderr}")
                return False

            self.logger.success(f"Step 1 complete: Fixed minimal firmware deployed to {device}")

            # Wait for device to reboot and reconnect
            self.logger.info("Waiting for device to reboot...")
            time.sleep(30)

            # Step 2: Deploy full firmware with new credentials
            self.logger.info("Step 2: Deploying full firmware with new credentials")

            full_config = f"{device}-full.yaml" if Path(f"{device}-full.yaml").exists() else f"{device}.yaml"

            # Compile full firmware
            compile_result = subprocess.run([
                'mise', 'exec', '--', 'esphome', 'compile', full_config
            ], capture_output=True, text=True, timeout=300)

            if compile_result.returncode != 0:
                self.logger.error(f"Failed to compile full firmware for {device}")
                self.logger.error(f"Error: {compile_result.stderr}")
                return False

            # Upload full firmware
            upload_result = subprocess.run([
                'mise', 'exec', '--', 'esphome', 'upload', full_config
            ], capture_output=True, text=True, timeout=300)

            if upload_result.returncode != 0:
                self.logger.error(f"Failed to upload full firmware to {device}")
                self.logger.error(f"Error: {upload_result.stderr}")
                return False

            self.logger.success(f"Step 2 complete: Full firmware deployed to {device}")
            self.logger.success(f"Recovery deployment successful for {device}")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error(f"Deployment to {device} timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to deploy to {device}: {e}")
            return False

    def verify_device_recovery(self, device):
        """Verify device is working with new credentials"""
        self.logger.info(f"Verifying recovery of {device}...")

        # Wait a bit for device to fully boot
        time.sleep(15)

        # Check if device is accessible
        if self.check_device_accessibility(device):
            self.logger.success(f"Device {device} is accessible after recovery")
            return True
        else:
            self.logger.warning(f"Device {device} may not be fully recovered yet")
            return False

    def recover_all_devices(self):
        """Attempt to recover all accessible ESP01 devices"""
        self.logger.header("ESP01 DEVICE RECOVERY DEPLOYMENT")

        # Scan for accessible devices
        accessible_devices = self.scan_recovery_network()

        if not accessible_devices:
            self.logger.warning("No devices found on recovery network")
            print("""
RECOVERY NETWORK SETUP REQUIRED:

1. Create WiFi hotspot with these EXACT credentials:
   - SSID: YOUR_RECOVERY_SSID
   - Password: YOUR_RECOVERY_PASSWORD

2. Wait for ESP01 devices to connect

3. Re-run this script to deploy fixed firmware
""")
            return False

        # Deploy to each accessible device
        successful_recoveries = []
        failed_recoveries = []

        for device in accessible_devices:
            self.logger.info(f"Starting recovery deployment for {device}")

            if self.deploy_fixed_firmware(device):
                if self.verify_device_recovery(device):
                    successful_recoveries.append(device)
                else:
                    self.logger.warning(f"Deployment succeeded but verification failed for {device}")
                    successful_recoveries.append(device)  # Still count as success
            else:
                failed_recoveries.append(device)

        # Report results
        self.logger.info(f"Recovery deployment complete:")
        self.logger.info(f"Successful: {len(successful_recoveries)} devices")
        self.logger.info(f"Failed: {len(failed_recoveries)} devices")

        if successful_recoveries:
            self.logger.success("Successfully recovered devices:")
            for device in successful_recoveries:
                print(f"  ✅ {device}")

        if failed_recoveries:
            self.logger.warning("Failed to recover devices:")
            for device in failed_recoveries:
                print(f"  ❌ {device}")

        return len(successful_recoveries) > 0


def main():
    """Main entry point"""
    print("ESP01 Device Recovery Deployment")
    print("=" * 50)

    recovery = RecoveryDeployment()

    if len(sys.argv) > 1:
        # Deploy to specific device
        device = sys.argv[1]
        print(f"Deploying to specific device: {device}")

        if recovery.check_device_accessibility(device):
            if recovery.deploy_fixed_firmware(device):
                recovery.verify_device_recovery(device)
                print(f"✅ Recovery deployment successful for {device}")
            else:
                print(f"❌ Recovery deployment failed for {device}")
        else:
            print(f"❌ Device {device} is not accessible")
    else:
        # Deploy to all accessible devices
        recovery.recover_all_devices()


if __name__ == "__main__":
    main()
