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

## Using `secrets.yaml`

The `secrets.yaml` file stores sensitive information such as Wi-Fi credentials, API keys, and passwords. This file is referenced by device configuration files to keep sensitive data out of version control.

**Important:**

- Do **not** commit your `secrets.yaml` to public repositories.
- Example entries in `secrets.yaml`:

  ```yaml
  wifi_ssid: "YourWiFiSSID"
  wifi_password: "YourWiFiPassword"
  ota_password: "YourOTAPassword"
  api_key: "YourAPIKey"
  ```

- Reference secrets in your YAML configs using `!secret`, e.g.:

  ```yaml
  wifi:
    ssid: !secret wifi_ssid
    password: !secret wifi_password
  ```

## Development Environment with Mise and Task

This project uses [Mise](https://mise.jdx.dev/) to manage project-specific development tools, ensuring consistent versions of `esphome` and `task`. A [Taskfile.yml](https://taskfile.dev/) is provided to automate common development workflows like building and uploading firmware.

### 1. Setup

1.  **Install Mise:** Follow the instructions on the [Mise website](https://mise.jdx.dev/getting-started.html) to install it.

2.  **Install Project Tools:** Once you've cloned the repository, navigate to the project directory and run:
    ```sh
    mise install
    ```
    This will automatically install the correct versions of `esphome` and `task` as defined in the `.mise.toml` file.

3.  **Create `secrets.yaml`:** Create or update your `secrets.yaml` file in the root directory with your Wi-Fi and other credentials.

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

## Notes

- Many device configs use `!include` to share common settings from the `common/` directory.
- Review each YAML file for device-specific instructions or comments.
- For custom components, see the `src/` and `include/` directories.

## Resources

- [ESPHome Documentation](https://esphome.io/)
- [YAML Configuration Guide](https://esphome.io/guides/configuration-types.html)

---

*Last updated: June 19, 2025*
