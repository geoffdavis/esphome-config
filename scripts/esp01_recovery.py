#!/usr/bin/env python3
"""
ESP01 Device Recovery Script

This script helps recover ESP01 devices that have been bricked due to 
minimal firmware deployment without fallback hotspot capability.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import SecurityLogger


class ESP01Recovery:
    """Handles recovery of bricked ESP01 devices"""
    
    def __init__(self):
        self.logger = SecurityLogger("esp01_recovery")
        
    def scan_for_recovery_hotspots(self):
        """Scan for any ESP recovery hotspots that might be available"""
        self.logger.info("Scanning for ESP recovery hotspots...")
        
        try:
            # Use system WiFi scanning
            if sys.platform == "darwin":  # macOS
                result = subprocess.run(
                    ["airport", "-s"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    esp_hotspots = []
                    
                    for line in lines:
                        if "ESP" in line or "fallback" in line.lower():
                            esp_hotspots.append(line.strip())
                    
                    if esp_hotspots:
                        self.logger.success(f"Found {len(esp_hotspots)} potential ESP hotspots:")
                        for hotspot in esp_hotspots:
                            print(f"  - {hotspot}")
                        return esp_hotspots
                    else:
                        self.logger.warning("No ESP recovery hotspots found")
                        return []
                        
            else:
                self.logger.warning("WiFi scanning not implemented for this platform")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to scan for hotspots: {e}")
            return []
    
    def list_bricked_devices(self):
        """List devices that are likely bricked based on ESP01 configuration"""
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
        
        self.logger.info("ESP01 devices that may be bricked:")
        for device in esp01_devices:
            print(f"  - {device}")
        
        return esp01_devices
    
    def create_recovery_firmware(self, device):
        """Create recovery firmware with fallback hotspot enabled"""
        self.logger.info(f"Creating recovery firmware for {device}")
        
        recovery_config = f"""
# Recovery firmware for {device}
# This firmware includes fallback hotspot for recovery

substitutions:
  name: {device}
  friendly_name: {device.replace('_', ' ').title()}

esphome:
  name: ${{name}}
  friendly_name: ${{friendly_name}}

esp8266:
  board: esp01_1m

logger:

# WiFi with MANDATORY fallback hotspot
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  domain: !secret wifi_domain
  
  # CRITICAL: Always include fallback hotspot for recovery
  ap:
    ssid: "${{friendly_name}} Recovery"
    password: !secret fallback_password

# Enable captive portal for recovery access
captive_portal:

# Enable OTA for recovery
ota:
  platform: esphome
  password: !secret old_ota_password

# Enable API for recovery
api:
  encryption:
    key: !secret api_key

# Enable web server for recovery
web_server:
  port: 80
  version: 3
"""
        
        recovery_file = f"{device}-recovery.yaml"
        with open(recovery_file, 'w') as f:
            f.write(recovery_config)
        
        self.logger.success(f"Created recovery firmware: {recovery_file}")
        return recovery_file
    
    def flash_recovery_firmware(self, device):
        """Flash recovery firmware to device (requires physical access)"""
        self.logger.warning("Physical recovery required!")
        print(f"""
PHYSICAL RECOVERY REQUIRED FOR {device.upper()}:

1. POWER OFF the device
2. Connect GPIO0 to GND (enter flash mode)
3. POWER ON the device
4. Use esptool to flash recovery firmware:
   
   esptool.py --port /dev/ttyUSB0 --baud 115200 erase_flash
   esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash 0x0 {device}-recovery.bin

5. DISCONNECT GPIO0 from GND
6. POWER CYCLE the device
7. Look for "{device.replace('_', ' ').title()} Recovery" WiFi hotspot

ALTERNATIVE: If you have a programmer/flasher tool, use that instead.
""")
    
    def generate_recovery_plan(self):
        """Generate comprehensive recovery plan"""
        self.logger.header("ESP01 DEVICE RECOVERY PLAN")
        
        print("""
CRITICAL ISSUE IDENTIFIED:
- Minimal firmware was deployed WITHOUT fallback hotspot capability
- ESP01 devices are now inaccessible if WiFi connection failed
- No recovery hotspots are being broadcast

IMMEDIATE ACTIONS REQUIRED:

1. SCAN FOR ANY REMAINING HOTSPOTS:
   - Check for any ESP devices still broadcasting recovery hotspots
   - Connect to any available hotspots to reconfigure WiFi

2. PHYSICAL RECOVERY (if no hotspots available):
   - ESP01 devices require physical access to GPIO0 pin
   - Must enter flash mode manually and reflash firmware
   - Use recovery firmware with fallback hotspot enabled

3. FIX MINIMAL FIRMWARE CONFIGURATION:
   - Update wifi-minimal.yaml to ALWAYS include fallback hotspot
   - Prevent this issue from happening again

4. SYSTEMATIC RECOVERY:
   - Recover devices one by one using physical access
   - Flash recovery firmware with fallback hotspot
   - Then deploy proper firmware with new credentials
""")
        
        # Scan for any available hotspots
        hotspots = self.scan_for_recovery_hotspots()
        
        # List affected devices
        bricked_devices = self.list_bricked_devices()
        
        # Create recovery firmware for each device
        self.logger.info("Creating recovery firmware files...")
        for device in bricked_devices:
            self.create_recovery_firmware(device)
        
        print(f"""
RECOVERY FIRMWARE CREATED:
- {len(bricked_devices)} recovery firmware files generated
- Each includes fallback hotspot for future recovery
- Use these for physical flashing if needed

NEXT STEPS:
1. Check if any devices are still accessible via hotspot
2. If not, prepare for physical recovery of each device
3. Fix the minimal firmware configuration to prevent recurrence
""")


def main():
    """Main entry point"""
    print("ESP01 Device Recovery Tool")
    print("=" * 50)
    
    recovery = ESP01Recovery()
    recovery.generate_recovery_plan()


if __name__ == "__main__":
    main()