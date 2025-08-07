# Common Tasks and Workflows

This document captures repetitive tasks and their step-by-step workflows
for future reference.

## Documentation Management Tasks

### Update Unified Documentation

**Last performed:** Ongoing maintenance

**Files to modify:**

- Files in `docs/` directory
- Cross-references and navigation links
- Memory Bank integration links

**Steps:**

1. Identify documentation need or update requirement
2. Determine appropriate location in `docs/` structure:

   ```bash
   docs/getting-started/     # New user guides
   docs/security/           # Security-related content
   docs/device-management/  # Device operations
   docs/architecture/       # System design guides
   docs/reference/          # Reference and troubleshooting
   ```

3. Create or update user-friendly content with step-by-step procedures
4. Link to Memory Bank for comprehensive technical details:

   ```markdown
   For complete technical details, see [System Architecture](.kilocode/rules/memory-bank/architecture.md#section).
   ```

5. Update navigation in `docs/README.md`
6. Verify all Memory Bank links work correctly
7. Test procedures for accuracy and completeness

**Important notes:**

- Never duplicate Memory Bank content - always link to it
- Focus on user-friendly guidance and practical procedures
- Include troubleshooting for common issues
- Maintain clear navigation between related topics

### Validate Documentation Integration

**Last performed:** Regular maintenance

**Files to modify:**

- Documentation link validation
- Cross-reference verification
- Navigation flow testing

**Steps:**

1. Validate Memory Bank links are working:

   ```bash
   grep -r "\.kilocode/rules/memory-bank/" docs/ | while read line; do
       file=$(echo "$line" | cut -d: -f1)
       link=$(echo "$line" | grep -o '\.kilocode/rules/memory-bank/[^)]*')
       if [ ! -f "$link" ]; then
           echo "Broken link in $file: $link"
       fi
   done
   ```

2. Check for potentially unlinked documentation:

   ```bash
   find docs/ -name "*.md" -not -name "README.md" | while read file; do
       basename=$(basename "$file")
       if ! grep -q "$basename" docs/README.md; then
           echo "Potentially unlinked file: $file"
       fi
   done
   ```

3. Verify navigation flow makes sense for different user journeys
4. Test all procedures documented in guides
5. Update any outdated command examples or references

**Important notes:**

- Run validation monthly to catch broken links
- Test procedures in clean environment before documenting
- Keep documentation maintenance guidelines current
- Focus on user experience and clear navigation

### Consolidate Legacy Documentation

**Last performed:** Major reorganization completed

**Files to modify:**

- Legacy documentation files
- Status reports and historical information
- Integration with unified structure

**Steps:**

1. Identify overlapping content with Memory Bank and unified docs
2. Extract user-friendly procedures for unified documentation
3. Create appropriate links to Memory Bank for technical details
4. Move status reports and historical info to `docs/status/`
5. Archive or delete completely duplicated content after verification
6. Update all references throughout the project
7. Verify no important information was lost in consolidation

**Important notes:**

- Preserve historical context in `docs/status/` directory
- Don't delete until verifying content is preserved elsewhere
- Update any scripts or automation that reference moved files
- Document consolidation decisions for future reference

## Device Management Tasks

### Add New Device Configuration

**Last performed:** Ongoing
**Files to modify:**

- Create new device YAML file (e.g., `new_device.yaml`)
- Update device-specific substitutions
- Select appropriate common packages

**Steps:**

1. Create device configuration file with descriptive name
2. Define substitutions section with device-specific parameters:

   ```yaml
   substitutions:
     name: device-name
     friendly_name: Device Name
     # Hardware-specific pin assignments
   ```

3. Include appropriate packages based on hardware platform:
   - ESP32: `nodemcuv2.yaml` or `esp32_device_base.yaml`
   - ESP8266: `nodemcuv2.yaml` or `wemosd1mini.yaml`
   - ESP01: `esp01.yaml`
4. Add connectivity packages:
   - Full devices: `wifi.yaml`, `ipv6.yaml`
   - ESP01 minimal: `wifi-minimal.yaml`
5. Include sensor packages as needed:
   - `sensor/bme280.yaml`, `sensor/dht.yaml`, etc.
6. Test configuration: `task build -- device-name`
7. Deploy: `task upload -- device-name` or `task upload-two-stage -- device-name`

**Important notes:**

- Use consistent naming conventions (lowercase with hyphens)
- Always include fallback hotspot for recovery
- Test with minimal configuration first for ESP01 devices
- Document hardware connections in comments

### Add New Sensor Type

**Last performed:** As needed
**Files to modify:**

- Create new sensor package in `common/sensor/`
- Update device configurations to include new sensor
- Test with representative devices

**Steps:**

1. Create sensor configuration file in `common/sensor/sensor_name.yaml`
2. Define sensor platform and configuration:

   ```yaml
   sensor:
     - platform: sensor_type
       name: "${friendly_name} Sensor Name"
       # Sensor-specific configuration
   ```

3. Use substitution variables for pin assignments and device-specific settings
4. Add any required I2C or SPI bus configurations
5. Include sensor in test device configuration
6. Validate sensor readings and entity creation in Home Assistant
7. Document sensor wiring and requirements in comments
8. Update relevant device configurations to include new sensor

**Important notes:**

- Use substitution variables for hardware-specific settings
- Test sensor accuracy and update intervals
- Ensure sensor names follow consistent patterns
- Add appropriate filters for noisy sensors

### ESP01 Two-Stage Deployment

**Last performed:** Regular maintenance
**Files to modify:**

- `device-minimal.yaml` (stage 1)
- `device-full.yaml` (stage 2)
- Ensure both configurations are synchronized

**Steps:**

1. Create minimal configuration with essential services only:

   ```yaml
   packages:
     wifi: !include common/wifi-minimal.yaml
     esp01: !include common/esp01.yaml
   ```

2. Create full configuration with all desired features:

   ```yaml
   packages:
     wifi: !include common/wifi.yaml
     ipv6: !include common/ipv6.yaml
     sensors: !include common/sensors.yaml
     esp01: !include common/esp01.yaml
   ```

3. Deploy using two-stage process: `task upload-two-stage -- device-name`
4. Verify device connectivity after each stage
5. Monitor memory usage and optimize if needed

**Important notes:**

- Always maintain recovery capability in minimal configuration
- Test OTA functionality before full deployment
- Keep configurations synchronized between stages
- Monitor device stability after full deployment

## Security Management Tasks

### Credential Rotation

**Last performed:** As needed for security
**Files to modify:**

- 1Password vaults (Automation and Shared)
- `secrets.yaml` (regenerated)
- Deployment validation

**Steps:**

1. Run security validation: `task security-validate`
2. Create backup: `python3 scripts/backup_secrets.py create`
3. Generate new credentials: `python3 scripts/rotate_credentials.py`
4. Update 1Password vaults with new credentials
5. Regenerate secrets file: `./scripts/generate_secrets.sh`
6. Validate new credentials: `python3 scripts/validate_secrets.py`
7. Deploy using rotation-aware deployment: `python3 scripts/deploy_with_rotation.py --all`
8. Verify all devices are accessible
9. Track rotation: `python3 scripts/track_secret_rotation.py add`

**Important notes:**

- Always backup before rotation
- Use `deploy_with_rotation.py` for seamless credential transitions
- Script handles both old and new credentials during deployment
- Verify 1Password integration is working
- Document rotation in tracking system

### Device Recovery

**Last performed:** As needed for device issues
**Files to modify:**

- Recovery network configuration
- Device-specific recovery procedures
- Recovery deployment scripts

**Steps:**

1. Identify offline or bricked devices
2. Check for fallback hotspot: Look for "[Device Name] ESP" networks
3. If hotspot available:
   - Connect to fallback hotspot
   - Access device at <http://192.168.4.1>
   - Reconfigure WiFi settings
4. If no hotspot (ESP01 devices):
   - Set up recovery network with exact credentials device expects
   - Wait for device to connect to recovery network
   - Deploy fixed firmware: `python3 scripts/recover_device.py <device_name>`
5. For physical recovery:
   - Use serial connection for firmware flashing
   - Follow ESP01 physical recovery procedures
6. Verify device connectivity after recovery

**Important notes:**

- ESP01 devices may require recovery network setup
- Always include fallback hotspot in minimal configurations
- Document recovery procedures for each device type
- Test recovery procedures periodically

### Security Framework Setup

**Last performed:** Initial setup and updates
**Files to modify:**

- Pre-commit hooks configuration
- Security tool installation
- Development environment setup

**Steps:**

1. Install security framework: `python3 scripts/setup_security.py`
2. Configure 1Password CLI and authentication
3. Set up environment variables in `.env` file
4. Install pre-commit hooks: `pre-commit install`
5. Run initial security scan: `task security-scan`
6. Set up development environment: `python3 scripts/setup_dev_secrets.py`
7. Run security tests: `task test-security`
8. Validate complete setup: `task security-validate`

**Important notes:**

- Ensure 1Password CLI is authenticated
- Test all security validation steps
- Verify pre-commit hooks are working
- Set up development credentials for safe testing

### Backup and Restore Operations

**Last performed:** Regular maintenance
**Files to modify:**

- Backup directory structure
- Backup manifests and metadata
- Recovery procedures

**Steps:**

1. Create backup: `python3 scripts/backup_secrets.py create`
2. List available backups: `python3 scripts/backup_secrets.py list`
3. Verify backup integrity: `python3 scripts/backup_secrets.py verify <backup_id>`
4. Restore from backup: `python3 scripts/backup_secrets.py restore <backup_id>`
5. Test restored configuration: `task security-validate`
6. Clean up old backups: `python3 scripts/backup_secrets.py cleanup --days 30`

**Important notes:**

- Regular backups before major changes
- Test restore procedures periodically
- Keep backup retention policy current
- Document backup and restore procedures

### Add Security Validation Rule

**Last performed:** Framework development
**Files to modify:**

- `scripts/security_lib.py` (core validation logic)
- `scripts/validate_secrets.py` (validation script)
- `tests/test_security_lib.py` (unit tests)

**Steps:**

1. Identify new security requirement or vulnerability
2. Add validation logic to appropriate class in `security_lib.py`
3. Update validation script to use new validation
4. Add comprehensive unit tests for new validation
5. Test validation with known good and bad examples
6. Update documentation with new validation requirements
7. Run full test suite: `python3 tests/run_tests.py`
8. Test integration with pre-commit hooks

**Important notes:**

- Always add unit tests for new validation logic
- Test both positive and negative cases
- Document validation requirements clearly
- Ensure validation integrates with existing workflow

## Development Environment Tasks

### Set Up New Development Environment

**Last performed:** New developer onboarding
**Files to modify:**

- Local environment setup
- Tool installation and configuration
- Development credentials

**Steps:**

1. Install Mise: Follow installation guide
2. Clone repository and navigate to project directory
3. Install project tools: `mise install`
4. Set up security framework: `python3 scripts/setup_security.py`
5. Configure 1Password CLI access
6. Set up development environment: `python3 scripts/setup_dev_secrets.py`
7. Install pre-commit hooks: `pre-commit install`
8. Run initial validation: `task security-validate`
9. Test device build: `task build -- test_device`
10. Verify all tools and workflows are working

**Important notes:**

- Use development credentials for testing
- Verify all security tools are working
- Test build and deployment processes
- Document any environment-specific issues

### Update Development Tools

**Last performed:** Regular maintenance
**Files to modify:**

- `.mise.toml` (tool versions)
- `requirements.txt` (Python dependencies)
- `package.json` (Node.js dependencies)

**Steps:**

1. Check for tool updates: `mise outdated`
2. Update tool versions in `.mise.toml`
3. Install updated tools: `mise install`
4. Update Python dependencies: `pip install -r requirements.txt --upgrade`
5. Update Node.js dependencies: `npm update`
6. Run tests to ensure compatibility: `task test-security`
7. Test build process: `task build-all`
8. Update documentation if needed
9. Commit tool version updates

**Important notes:**

- Test thoroughly after updates
- Check for breaking changes in tool updates
- Update documentation for any workflow changes
- Coordinate updates across development team

## Maintenance Tasks

### Bulk Device Updates

**Last performed:** Regular maintenance
**Files to modify:**

- Multiple device configurations
- Common component updates

**Steps:**

1. Run security validation: `task security-validate`
2. Test changes with single device first
3. Create backup of current configurations
4. Run bulk build: `task build-all`
5. Deploy to all devices: `task upload-all-two-stage`
6. Monitor deployment progress and handle offline devices
7. Verify device functionality after updates
8. Document any issues or failures
9. Update device inventory and status

**Important notes:**

- Always test with single device first
- Handle offline devices gracefully
- Monitor device health after updates
- Keep deployment logs for troubleshooting

### Common Component Updates

**Last performed:** Feature additions and improvements
**Files to modify:**

- Files in `common/` directory
- Device configurations using updated components
- Testing and validation

**Steps:**

1. Identify component requiring updates
2. Create backup of current component
3. Update component configuration
4. Test with representative devices
5. Validate sensor readings and functionality
6. Update documentation and comments
7. Deploy to test devices first
8. Roll out to production devices
9. Monitor for issues and rollback if needed

**Important notes:**

- Test with multiple device types
- Verify backward compatibility
- Update component documentation
- Monitor device performance after changes

### Security Audit and Cleanup

**Last performed:** Regular security maintenance
**Files to modify:**

- Security configurations
- Credential validation
- Audit documentation

**Steps:**

1. Run comprehensive security scan: `task security-scan`
2. Review credential rotation history
3. Check for exposed credentials in all files
4. Validate 1Password integration and access
5. Review and update security documentation
6. Test security validation pipeline
7. Update security tools and dependencies
8. Document findings and recommendations
9. Plan and execute any necessary security improvements

**Important notes:**

- Document all security findings
- Update security procedures as needed
- Test all security tools and validations
- Coordinate security updates with deployments
