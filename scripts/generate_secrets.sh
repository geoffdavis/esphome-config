#!/bin/bash

# This script generates the secrets.yaml file by fetching secrets from 1Password.

# --- Configuration ---
# Replace the placeholders below with the correct 1Password references.
# Format: op://<vault>/<item>/<field>

WIFI_SSID_REF="op://Shared/Home IoT/network name"
WIFI_PASSWORD_REF="op://Shared/Home IoT/wireless network password"
WIFI_DOMAIN_REF="op://Shared/Home IoT/domain name"
API_KEY_REF="op://Automation/ESPHome/api_key"
FALLBACK_PASSWORD_REF="op://Automation/ESPHome/fallback_password"
OTA_PASSWORD_REF="op://Automation/ESPHome/ota_password"

# --- Fetch Secrets ---
WIFI_SSID=$(op read "$WIFI_SSID_REF" --account="CamiAndGeoff")
WIFI_PASSWORD=$(op read "$WIFI_PASSWORD_REF" --account="CamiAndGeoff")
WIFI_DOMAIN=$(op read "$WIFI_DOMAIN_REF" --account="CamiAndGeoff")
API_KEY=$(op read "$API_KEY_REF" --account="CamiAndGeoff")
FALLBACK_PASSWORD=$(op read "$FALLBACK_PASSWORD_REF" --account="CamiAndGeoff")
OTA_PASSWORD=$(op read "$OTA_PASSWORD_REF" --account="CamiAndGeoff")

# --- Generate secrets.yaml ---
cat > secrets.yaml << EOL
# ESPhome secrets file
# This file is auto-generated. DO NOT EDIT MANUALLY.

# wifi credentials
wifi_ssid: "${WIFI_SSID}"
wifi_password: "${WIFI_PASSWORD}"
wifi_domain: "${WIFI_DOMAIN}"

# API key
api_key: "${API_KEY}"

# Fallback hotspot password
fallback_password: "${FALLBACK_PASSWORD}"

# OTA password
ota_password: "${OTA_PASSWORD}"
EOL

echo "secrets.yaml generated successfully."