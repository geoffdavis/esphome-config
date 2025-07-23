# ESPHome Device Configurations

This repository contains YAML configuration files for various ESPHome-based devices in your home automation setup. Each YAML file defines the configuration for a specific device, such as sensors, outlets, heat pumps, and more.

## Repository Structure

- Top-level YAML files: Individual device configurations (e.g., `bedroom_east_heatpump.yaml`, `den_multisensor.yaml`).
- `archive/`: Archived or legacy configurations.
- `common/`: Shared YAML includes for device templates, sensors, and components.
- `config/`: Additional configuration files.
- `fonts/`: Font files for display components.
- `include/`: C++ header files for custom ESPHome components.
- `src/`: Source code and advanced custom components.
- `scripts/`: Python security framework and automation scripts.
- `tests/`: Unit tests for the security framework.

## Using `secrets.yaml`

The `secrets.yaml` file stores sensitive information such as Wi-Fi credentials, API keys, and passwords. This file is referenced by device configuration files to keep sensitive data out of version control.

**Important:**

- Do **not** commit your `secrets.yaml` to public repositories.
- Example entries in `secrets.yaml`:

  ```yaml
  wifi_ssid: "YourWiFiSSID"
  wifi_password: "YourWiFiPassword"  # pragma: allowlist secret
  ota_password: "YourOTAPassword"  # pragma: allowlist secret
  api_key: "YourAPIKey"  # pragma: allowlist secret
  ```

- Reference secrets in your YAML configs using `!secret`, e.g.:

  ```yaml
  wifi:
    ssid: !secret wifi_ssid
    password: !secret wifi_password
  ```

## Security Framework

This repository includes a comprehensive Python-based security framework to protect your ESPHome configurations and credentials.

### Quick Security Setup

```bash
# Set up security tools and hooks
python3 scripts/setup_security.py

# Validate your configuration
task security-validate

# Run comprehensive security scan
task security-scan
```

### Key Security Features

- **Credential Validation**: Ensures secrets meet security requirements
- **1Password Integration**: Secure credential storage and retrieval
- **Exposed Credential Detection**: Identifies known compromised credentials
- **Automated Backup**: Secure backup and restore of configurations
- **Development Environment**: Safe test credentials for development

### Security Tasks

```bash
task security-setup              # Set up security tools
task security-validate           # Essential validation
task security-scan              # Comprehensive scan
task security-rotate-credentials # Rotate credentials
task security-backup           # Create backup
task dev-setup                 # Development environment
task test-security             # Run security tests
```

### Documentation

- **[Security Framework Guide](SECURITY_FRAMEWORK.md)**: Comprehensive documentation
- **[Migration Guide](MIGRATION_GUIDE.md)**: Migrating from bash to Python scripts

## Development Environment with Mise and Task

This project uses [Mise](https://mise.jdx.dev/) to manage project-specific development tools, ensuring consistent versions of `esphome` and `task`. A [Taskfile.yml](https://taskfile.dev/) is provided to automate common development workflows like building and uploading firmware.

### 1. Setup

1.  **Install Mise:** Follow the instructions on the [Mise website](https://mise.jdx.dev/getting-started.html) to install it.

2.  **Install Project Tools:** Once you've cloned the repository, navigate to the project directory and run:
    ```sh
    mise install
    ```
    This will automatically install the correct versions of `esphome` and `task` as defined in the `.mise.toml` file.

3.  **Set up security framework:**
    ```sh
    python3 scripts/setup_security.py
    ```

4.  **Create `secrets.yaml`:** Create or update your `secrets.yaml` file in the root directory with your Wi-Fi and other credentials.

    **For development:** Use the development environment setup:
    ```sh
    task dev-setup
    cp dev/secrets.yaml secrets.yaml  # For development only
    ```

### 2. Using Task

The `Taskfile.yml` provides several commands to simplify the development process. Here are some of the most common ones:

-   **List all available tasks:**
    ```sh
    task -l
    ```

-   **Build firmware for a single device:**
    ```sh
    task build -- <device-name>
    ```
    Example: `task build -- den_multisensor`

-   **Upload firmware to a single device:**
    This will automatically build the firmware first. For devices with a two-stage OTA process (a `-minimal.yaml` and `-full.yaml` file), this command will upload the full firmware.
    ```sh
    task upload -- <device-name>
    ```
    Example: `task upload -- den_multisensor`

-   **Upload firmware in two stages:**
    For devices with limited flash space, a two-stage upload is required. This first uploads a minimal firmware, then the full version.
    ```sh
    task upload-two-stage -- <device-name>
    ```
    Example: `task upload-two-stage -- attic_sensor`

-   **Build firmware for all devices:**
    ```sh
    task build-all
    ```

-   **Upload firmware for all devices:**
    This will perform a two-stage upload for devices that require it.
    ```sh
    task upload-all-two-stage
    ```

-   **Clean build files for a device:**
    ```sh
    task clean -- <device-name>
    ```
    Example: `task clean -- den_multisensor`

### Security Integration

All upload tasks automatically run security validation to ensure your configuration is secure before deployment:

```bash
# These tasks include automatic security validation
task upload -- <device-name>
task upload-all-two-stage
task build-all
```

## Security Best Practices

### Credential Management

1. **Never commit secrets**: Use `!secret` references in YAML files
2. **Use 1Password**: Store credentials securely in 1Password vaults
3. **Regular rotation**: Rotate credentials periodically using the automation tools
4. **Validate regularly**: Run security scans before deployments

### Development Workflow

1. **Use development environment**: Set up safe test credentials
2. **Run tests**: Execute security tests before committing changes
3. **Pre-commit hooks**: Automatic validation on every commit
4. **Backup regularly**: Create backups before major changes

### Environment Configuration

Create a `.env` file for 1Password integration:
```bash
# .env (create this file)
OP_ACCOUNT=your-1password-account
```

## Notes

- Many device configs use `!include` to share common settings from the `common/` directory.
- Review each YAML file for device-specific instructions or comments.
- For custom components, see the `src/` and `include/` directories.
- **Security**: All sensitive data should use `!secret` references to `secrets.yaml`
- **Testing**: Use the development environment for safe testing with test credentials

## Resources

### ESPHome
- [ESPHome Documentation](https://esphome.io/)
- [YAML Configuration Guide](https://esphome.io/guides/configuration-types.html)

### Security Framework
- [Security Framework Documentation](SECURITY_FRAMEWORK.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [1Password CLI Documentation](https://developer.1password.com/docs/cli/)

### Development Tools
- [Mise Documentation](https://mise.jdx.dev/)
- [Task Documentation](https://taskfile.dev/)

---

*Last updated: July 16, 2025*
