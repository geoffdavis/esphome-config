#!/usr/bin/env python3
"""
ESPHome Secret Rotation Tracking Script

Tracks and logs secret rotation activities, maintains rotation history,
and provides reporting on credential lifecycle management.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the scripts directory to the path to import security_lib
sys.path.insert(0, str(Path(__file__).parent))

from security_lib import (
    SecurityLogger,
    SecurityConfig,
    OnePasswordManager,
    CredentialValidator,
    SecureFileHandler
)


class SecretRotationTracker:
    """Tracks and manages secret rotation history"""
    
    def __init__(self):
        self.logger = SecurityLogger("rotation_tracker")
        self.file_handler = SecureFileHandler()
        self.validator = CredentialValidator()
        self.rotation_log_file = "CREDENTIAL_ROTATION_LOG.json"
        self.markdown_log_file = "CREDENTIAL_ROTATION_LOG.md"
    
    def load_rotation_history(self) -> List[Dict[str, Any]]:
        """Load rotation history from JSON file"""
        if not os.path.exists(self.rotation_log_file):
            return []
        
        try:
            with open(self.rotation_log_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load rotation history: {e}")
            return []
    
    def save_rotation_history(self, history: List[Dict[str, Any]]) -> bool:
        """Save rotation history to JSON file"""
        try:
            with open(self.rotation_log_file, 'w') as f:
                json.dump(history, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save rotation history: {e}")
            return False
    
    def add_rotation_entry(self, rotation_type: str, reason: str, 
                          credentials_rotated: List[str], 
                          method: str = "manual",
                          notes: str = "") -> bool:
        """Add a new rotation entry to the history"""
        history = self.load_rotation_history()
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": rotation_type,
            "reason": reason,
            "credentials_rotated": credentials_rotated,
            "method": method,
            "performed_by": os.getenv('USER', 'unknown'),
            "notes": notes,
            "validation_status": "pending"
        }
        
        history.append(entry)
        
        if self.save_rotation_history(history):
            self.logger.success(f"Added rotation entry: {rotation_type}")
            return True
        return False
    
    def update_validation_status(self, entry_index: int, status: str, 
                                validation_notes: str = "") -> bool:
        """Update validation status of a rotation entry"""
        history = self.load_rotation_history()
        
        if 0 <= entry_index < len(history):
            history[entry_index]["validation_status"] = status
            history[entry_index]["validation_timestamp"] = datetime.now().isoformat()
            if validation_notes:
                history[entry_index]["validation_notes"] = validation_notes
            
            if self.save_rotation_history(history):
                self.logger.success(f"Updated validation status to: {status}")
                return True
        
        self.logger.error("Invalid entry index or failed to save")
        return False
    
    def get_rotation_stats(self) -> Dict[str, Any]:
        """Get rotation statistics"""
        history = self.load_rotation_history()
        
        if not history:
            return {
                "total_rotations": 0,
                "last_rotation": None,
                "rotations_by_type": {},
                "rotations_by_reason": {},
                "average_rotation_interval": None
            }
        
        # Calculate statistics
        total_rotations = len(history)
        last_rotation = history[-1]["date"] if history else None
        
        # Group by type and reason
        rotations_by_type = {}
        rotations_by_reason = {}
        
        for entry in history:
            rotation_type = entry.get("type", "unknown")
            reason = entry.get("reason", "unknown")
            
            rotations_by_type[rotation_type] = rotations_by_type.get(rotation_type, 0) + 1
            rotations_by_reason[reason] = rotations_by_reason.get(reason, 0) + 1
        
        # Calculate average interval
        average_interval = None
        if len(history) > 1:
            try:
                dates = [datetime.fromisoformat(entry["timestamp"]) for entry in history]
                dates.sort()
                intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                average_interval = sum(intervals) / len(intervals)
            except Exception:
                pass
        
        return {
            "total_rotations": total_rotations,
            "last_rotation": last_rotation,
            "rotations_by_type": rotations_by_type,
            "rotations_by_reason": rotations_by_reason,
            "average_rotation_interval_days": average_interval
        }
    
    def check_rotation_due(self, max_age_days: int = 90) -> Dict[str, Any]:
        """Check if rotation is due based on last rotation date"""
        history = self.load_rotation_history()
        
        if not history:
            return {
                "rotation_due": True,
                "reason": "No rotation history found",
                "days_since_last": None,
                "last_rotation": None
            }
        
        last_entry = history[-1]
        last_rotation_date = datetime.fromisoformat(last_entry["timestamp"])
        days_since_last = (datetime.now() - last_rotation_date).days
        
        rotation_due = days_since_last >= max_age_days
        
        return {
            "rotation_due": rotation_due,
            "reason": f"Last rotation was {days_since_last} days ago" if rotation_due else "Recent rotation",
            "days_since_last": days_since_last,
            "last_rotation": last_entry["date"],
            "max_age_days": max_age_days
        }
    
    def validate_current_credentials(self) -> Dict[str, Any]:
        """Validate current credentials and check for exposed ones"""
        try:
            op_manager = OnePasswordManager()
            credentials = op_manager.get_esphome_credentials()
            
            if not credentials:
                return {
                    "status": "error",
                    "message": "Failed to retrieve credentials from 1Password"
                }
            
            validation_results = {}
            exposed_found = False
            
            for cred_type, cred_value in credentials.items():
                if cred_type == 'api_key':
                    valid, msg = self.validator.validate_api_key(cred_value)
                elif cred_type == 'ota_password':
                    valid, msg = self.validator.validate_ota_password(cred_value)
                elif cred_type == 'fallback_password':
                    valid, msg = self.validator.validate_fallback_password(cred_value)
                else:
                    continue
                
                validation_results[cred_type] = {
                    "valid": valid,
                    "message": msg,
                    "exposed": "exposed credential" in msg.lower()
                }
                
                if "exposed credential" in msg.lower():
                    exposed_found = True
            
            return {
                "status": "success",
                "validation_results": validation_results,
                "exposed_credentials_found": exposed_found,
                "requires_immediate_rotation": exposed_found
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Validation failed: {e}"
            }
    
    def generate_markdown_report(self) -> bool:
        """Generate markdown report from rotation history"""
        history = self.load_rotation_history()
        stats = self.get_rotation_stats()
        
        try:
            content = "# ESPHome Credential Rotation Log\n\n"
            content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Statistics section
            content += "## Rotation Statistics\n\n"
            content += f"- **Total Rotations**: {stats['total_rotations']}\n"
            content += f"- **Last Rotation**: {stats['last_rotation'] or 'Never'}\n"
            
            if stats['average_rotation_interval_days']:
                content += f"- **Average Interval**: {stats['average_rotation_interval_days']:.1f} days\n"
            
            content += "\n### Rotations by Type\n\n"
            for rotation_type, count in stats['rotations_by_type'].items():
                content += f"- **{rotation_type}**: {count}\n"
            
            content += "\n### Rotations by Reason\n\n"
            for reason, count in stats['rotations_by_reason'].items():
                content += f"- **{reason}**: {count}\n"
            
            # Rotation history
            content += "\n## Rotation History\n\n"
            
            if not history:
                content += "*No rotation history available.*\n"
            else:
                for i, entry in enumerate(reversed(history)):
                    content += f"### Rotation {len(history) - i}\n\n"
                    content += f"**Date**: {entry['date']}\n"
                    content += f"**Time**: {entry['time']}\n"
                    content += f"**Type**: {entry['type']}\n"
                    content += f"**Reason**: {entry['reason']}\n"
                    content += f"**Method**: {entry['method']}\n"
                    content += f"**Performed By**: {entry['performed_by']}\n"
                    
                    if entry.get('credentials_rotated'):
                        content += f"**Credentials Rotated**: {', '.join(entry['credentials_rotated'])}\n"
                    
                    content += f"**Validation Status**: {entry.get('validation_status', 'unknown')}\n"
                    
                    if entry.get('notes'):
                        content += f"**Notes**: {entry['notes']}\n"
                    
                    if entry.get('validation_notes'):
                        content += f"**Validation Notes**: {entry['validation_notes']}\n"
                    
                    content += "\n---\n\n"
            
            with open(self.markdown_log_file, 'w') as f:
                f.write(content)
            
            self.logger.success(f"Markdown report generated: {self.markdown_log_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate markdown report: {e}")
            return False
    
    def run_rotation_check(self) -> bool:
        """Run comprehensive rotation check"""
        self.logger.header("ESPHome Secret Rotation Check")
        
        # Check if rotation is due
        rotation_check = self.check_rotation_due()
        
        if rotation_check["rotation_due"]:
            self.logger.warning(f"Rotation may be due: {rotation_check['reason']}")
        else:
            self.logger.success(f"Rotation not due: {rotation_check['reason']}")
        
        # Validate current credentials
        validation_result = self.validate_current_credentials()
        
        if validation_result["status"] == "error":
            self.logger.error(validation_result["message"])
            return False
        
        if validation_result["exposed_credentials_found"]:
            self.logger.error("EXPOSED CREDENTIALS DETECTED!")
            self.logger.error("Immediate rotation required!")
            
            for cred_type, result in validation_result["validation_results"].items():
                if result["exposed"]:
                    self.logger.error(f"{cred_type}: {result['message']}")
            
            return False
        else:
            self.logger.success("No exposed credentials detected")
            
            for cred_type, result in validation_result["validation_results"].items():
                if result["valid"]:
                    self.logger.success(f"{cred_type}: Valid")
                else:
                    self.logger.warning(f"{cred_type}: {result['message']}")
        
        # Display statistics
        stats = self.get_rotation_stats()
        self.logger.info(f"Total rotations performed: {stats['total_rotations']}")
        if stats['last_rotation']:
            self.logger.info(f"Last rotation: {stats['last_rotation']}")
        
        return True


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command in ['-h', '--help']:
            print("""
ESPHome Secret Rotation Tracking Script

This script tracks and manages secret rotation activities.

Usage:
    python3 scripts/track_secret_rotation.py [command] [options]

Commands:
    check           - Run rotation check and validation
    add             - Add rotation entry (interactive)
    stats           - Show rotation statistics
    report          - Generate markdown report
    validate        - Validate current credentials
    due             - Check if rotation is due

Examples:
    python3 scripts/track_secret_rotation.py check
    python3 scripts/track_secret_rotation.py stats
    python3 scripts/track_secret_rotation.py report

For more information, see SECURITY.md
            """)
            return
        
        tracker = SecretRotationTracker()
        
        if command == "check":
            success = tracker.run_rotation_check()
            sys.exit(0 if success else 1)
        
        elif command == "stats":
            stats = tracker.get_rotation_stats()
            print("\nRotation Statistics:")
            print(f"Total rotations: {stats['total_rotations']}")
            print(f"Last rotation: {stats['last_rotation'] or 'Never'}")
            if stats['average_rotation_interval_days']:
                print(f"Average interval: {stats['average_rotation_interval_days']:.1f} days")
            
            print("\nRotations by type:")
            for rotation_type, count in stats['rotations_by_type'].items():
                print(f"  {rotation_type}: {count}")
        
        elif command == "report":
            tracker.generate_markdown_report()
        
        elif command == "validate":
            result = tracker.validate_current_credentials()
            if result["status"] == "error":
                print(f"Error: {result['message']}")
                sys.exit(1)
            
            print("Credential Validation Results:")
            for cred_type, validation in result["validation_results"].items():
                status = "✓" if validation["valid"] else "✗"
                print(f"  {status} {cred_type}: {validation['message']}")
            
            if result["exposed_credentials_found"]:
                print("\n⚠️  EXPOSED CREDENTIALS DETECTED - IMMEDIATE ROTATION REQUIRED!")
                sys.exit(1)
        
        elif command == "due":
            check = tracker.check_rotation_due()
            print(f"Rotation due: {check['rotation_due']}")
            print(f"Reason: {check['reason']}")
            if check['days_since_last'] is not None:
                print(f"Days since last rotation: {check['days_since_last']}")
        
        elif command == "add":
            # Interactive mode for adding rotation entry
            print("Adding rotation entry (interactive mode):")
            rotation_type = input("Rotation type (scheduled/emergency/security): ").strip()
            reason = input("Reason for rotation: ").strip()
            credentials = input("Credentials rotated (comma-separated): ").strip().split(',')
            credentials = [c.strip() for c in credentials if c.strip()]
            method = input("Method used (manual/automated): ").strip() or "manual"
            notes = input("Additional notes (optional): ").strip()
            
            if tracker.add_rotation_entry(rotation_type, reason, credentials, method, notes):
                print("Rotation entry added successfully!")
            else:
                print("Failed to add rotation entry!")
                sys.exit(1)
        
        else:
            print(f"Unknown command: {command}")
            print("Use --help for usage information")
            sys.exit(1)
    
    else:
        # Default: run rotation check
        tracker = SecretRotationTracker()
        success = tracker.run_rotation_check()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()