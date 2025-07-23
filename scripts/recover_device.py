#!/usr/bin/env python3
"""
Device Recovery Script for ESPHome devices that have gone offline after deployment.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_fallback_hotspot():
    """Check if device is in fallback hotspot mode"""
    print("🔍 Checking for fallback hotspot...")
    
    # On macOS, check available WiFi networks
    try:
        result = subprocess.run([
            "networksetup", "-listallhardwareports"
        ], capture_output=True, text=True)
        
        # Get WiFi interface
        wifi_interface = None
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if "Wi-Fi" in line and i + 1 < len(lines):
                device_line = lines[i + 1]
                if "Device:" in device_line:
                    wifi_interface = device_line.split("Device: ")[1].strip()
                    break
        
        if not wifi_interface:
            print("❌ Could not find WiFi interface")
            return False
            
        # Scan for networks
        result = subprocess.run([
            "airport", "-s"
        ], capture_output=True, text=True)
        
        networks = result.stdout
        hotspot_found = False
        
        for line in networks.split('\n'):
            if "ESP" in line and ("Den" in line or "Heatpump" in line):
                print(f"✅ Found fallback hotspot: {line.strip()}")
                hotspot_found = True
                
        if not hotspot_found:
            print("❌ No fallback hotspot found")
            
        return hotspot_found
        
    except Exception as e:
        print(f"❌ Error checking networks: {e}")
        return False

def try_recovery_deployment(device_name="denheatpump"):
    """Try to recover device using PorkIOT network"""
    print(f"🔄 Attempting recovery deployment for {device_name}...")
    
    # Backup current secrets
    subprocess.run(["cp", "secrets.yaml", "secrets.yaml.backup"])
    
    # Use recovery secrets
    subprocess.run(["cp", "secrets.yaml.recovery", "secrets.yaml"])
    
    try:
        # Try minimal deployment first
        print("📡 Deploying minimal configuration...")
        result = subprocess.run([
            "task", "upload", f"CONFIG={device_name}-minimal"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Minimal deployment successful")
            
            # Wait a bit for device to stabilize
            time.sleep(10)
            
            # Try full deployment
            print("📡 Deploying full configuration...")
            result = subprocess.run([
                "task", "upload", f"CONFIG={device_name}-full"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Full deployment successful")
                return True
            else:
                print(f"❌ Full deployment failed: {result.stderr}")
                
        else:
            print(f"❌ Minimal deployment failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Deployment timed out")
    except Exception as e:
        print(f"❌ Deployment error: {e}")
    finally:
        # Restore original secrets
        subprocess.run(["cp", "secrets.yaml.backup", "secrets.yaml"])
        
    return False

def check_device_online(device_name="denheatpump"):
    """Check if device is back online"""
    print(f"🔍 Checking if {device_name} is online...")
    
    # Try to ping the device
    try:
        result = subprocess.run([
            "ping", "-c", "3", f"{device_name}.NoT.Home.GeoffDavis.COM"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Device is responding to ping")
            return True
        else:
            print("❌ Device not responding to ping")
            
    except subprocess.TimeoutExpired:
        print("⏰ Ping timed out")
    except Exception as e:
        print(f"❌ Ping error: {e}")
        
    return False

def main():
    print("🚨 ESPHome Device Recovery Tool")
    print("=" * 40)
    
    device_name = sys.argv[1] if len(sys.argv) > 1 else "denheatpump"
    
    # Step 1: Check if device is already back online
    if check_device_online(device_name):
        print("✅ Device is already online!")
        return
    
    # Step 2: Check for fallback hotspot
    if check_fallback_hotspot():
        print("\n📱 Manual Recovery Required:")
        print("1. Connect to the fallback hotspot")
        print("2. Navigate to http://192.168.4.1")
        print("3. Configure WiFi settings")
        print("4. Use PorkIOT network with password: Internet0fRinds.")
        return
    
    # Step 3: Try recovery deployment
    print("\n🔄 Attempting automated recovery...")
    if try_recovery_deployment(device_name):
        print("✅ Recovery successful!")
        
        # Verify device is online
        time.sleep(5)
        if check_device_online(device_name):
            print("✅ Device confirmed online")
        else:
            print("⚠️  Device deployed but not responding")
    else:
        print("❌ Recovery failed")
        print("\n🔧 Manual Recovery Options:")
        print("1. Physical access to device for serial recovery")
        print("2. Check power and network connections")
        print("3. Look for fallback hotspot after device reboot")

if __name__ == "__main__":
    main()