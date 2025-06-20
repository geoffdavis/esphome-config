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

## Building and Uploading Device Configurations

1. **Install ESPHome:**
   - Using pip: `pip install esphome`
   - Or use the [ESPHome Dashboard](https://esphome.io/guides/getting_started_command_line.html)

2. **Clone this repository:**

   ```sh
   git clone <your-repo-url>
   cd esphome
   ```

3. **Create or update your `secrets.yaml`** in the root directory with your Wi-Fi and other credentials.

4. **Build and upload a device configuration:**
   - Connect your ESP device via USB or use OTA (Over-The-Air) updates.
   - Run:

     ```sh
     esphome run <device_config.yaml>
     ```

   - Example:

     ```sh
     esphome run bedroom_east_heatpump.yaml
     ```

5. **Advanced:**
   - Use `esphome compile <device_config.yaml>` to only build the firmware.
   - Use `esphome upload <device_config.yaml>` to upload to a device.

## Notes

- Many device configs use `!include` to share common settings from the `common/` directory.
- Review each YAML file for device-specific instructions or comments.
- For custom components, see the `src/` and `include/` directories.

## Resources

- [ESPHome Documentation](https://esphome.io/)
- [YAML Configuration Guide](https://esphome.io/guides/configuration-types.html)

---

*Last updated: June 19, 2025*
