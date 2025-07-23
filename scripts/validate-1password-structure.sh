#!/bin/bash

# 1Password Structure Validation Script
# Validates that 1Password vaults and items are properly configured for ESPHome

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if 1Password CLI is installed
check_op_cli() {
    if ! command -v op >/dev/null 2>&1; then
        log_error "1Password CLI not found"
        log_info "Install from: https://developer.1password.com/docs/cli/get-started/"
        return 1
    fi
    log_success "1Password CLI found"
    return 0
}

# Check account access
check_account_access() {
    log_info "Checking 1Password account access..."
    
    if [[ -z "$OP_ACCOUNT" ]]; then
        log_error "OP_ACCOUNT environment variable not set"
        log_info "Set with: export OP_ACCOUNT=your-account-name"
        log_info "Or sign in with: op signin"
        return 1
    fi
    
    if ! op account list >/dev/null 2>&1; then
        log_error "Cannot access 1Password account '$OP_ACCOUNT'"
        log_info "Sign in with: op signin"
        log_info "Add account with: op account add --address my.1password.com --email your@email.com"
        return 1
    fi
    
    log_success "Account '$OP_ACCOUNT' is accessible"
    return 0
}

# Check vault access
check_vault_access() {
    local vault_name="$1"
    local vault_description="$2"
    
    log_info "Checking access to '$vault_name' vault..."
    
    if ! op vault list --account="$OP_ACCOUNT" | grep -q "$vault_name"; then
        log_error "Vault '$vault_name' not found or not accessible"
        log_info "Available vaults:"
        op vault list --account="$OP_ACCOUNT" 2>/dev/null || log_error "Cannot list vaults"
        return 1
    fi
    
    log_success "Vault '$vault_name' ($vault_description) is accessible"
    return 0
}

# Check item access and structure
check_item_structure() {
    local vault_name="$1"
    local item_name="$2"
    local expected_fields="$3"
    
    log_info "Checking '$item_name' item in '$vault_name' vault..."
    
    # Check if item exists
    if ! op item get "$item_name" --vault="$vault_name" --account="$OP_ACCOUNT" >/dev/null 2>&1; then
        log_error "Item '$item_name' not found in vault '$vault_name'"
        log_info "Available items in '$vault_name':"
        op item list --vault="$vault_name" --account="$OP_ACCOUNT" 2>/dev/null || log_error "Cannot list items"
        return 1
    fi
    
    log_success "Item '$item_name' found in vault '$vault_name'"
    
    # Check expected fields
    local missing_fields=0
    IFS=',' read -ra FIELDS <<< "$expected_fields"
    for field in "${FIELDS[@]}"; do
        field=$(echo "$field" | xargs)  # Trim whitespace
        log_info "Checking field '$field'..."
        
        if op item get "$item_name" --vault="$vault_name" --account="$OP_ACCOUNT" --fields="$field" >/dev/null 2>&1; then
            log_success "Field '$field' exists"
        else
            log_error "Field '$field' missing or inaccessible"
            missing_fields=$((missing_fields + 1))
        fi
    done
    
    return $missing_fields
}

# Validate field values
validate_field_values() {
    local vault_name="$1"
    local item_name="$2"
    
    log_info "Validating field values in '$item_name'..."
    
    local errors=0
    
    # Validate API key format
    local api_key
    api_key=$(op item get "$item_name" --vault="$vault_name" --account="$OP_ACCOUNT" --fields="api_key" 2>/dev/null || echo "")
    if [[ -n "$api_key" ]]; then
        if [[ ${#api_key} -eq 44 && "$api_key" =~ ^[A-Za-z0-9+/]{43}=$ ]]; then
            if [[ "$api_key" == "rgXTHsxFpWpqZ8keD/h0cPLN6CN2ZznLLyXwh9JgTAk=" ]]; then
                log_error "API key is the known exposed credential - must be rotated!"
                errors=$((errors + 1))
            else
                log_success "API key format is valid and not exposed"
            fi
        else
            log_error "API key format is invalid (expected 44 chars, base64)"
            errors=$((errors + 1))
        fi
    fi
    
    # Validate OTA password format
    local ota_password
    ota_password=$(op item get "$item_name" --vault="$vault_name" --account="$OP_ACCOUNT" --fields="ota_password" 2>/dev/null || echo "")
    if [[ -n "$ota_password" ]]; then
        if [[ ${#ota_password} -eq 32 && "$ota_password" =~ ^[a-fA-F0-9]{32}$ ]]; then
            if [[ "$ota_password" == "5929ccc1f08289c79aca50ebe0a9b7eb" ]]; then
                log_error "OTA password is the known exposed credential - must be rotated!"
                errors=$((errors + 1))
            else
                log_success "OTA password format is valid and not exposed"
            fi
        else
            log_error "OTA password format is invalid (expected 32 chars, hex)"
            errors=$((errors + 1))
        fi
    fi
    
    # Validate fallback password format
    local fallback_password
    fallback_password=$(op item get "$item_name" --vault="$vault_name" --account="$OP_ACCOUNT" --fields="fallback_password" 2>/dev/null || echo "")
    if [[ -n "$fallback_password" ]]; then
        if [[ ${#fallback_password} -ge 12 && "$fallback_password" =~ ^[A-Za-z0-9]+$ ]]; then
            if [[ "$fallback_password" == "1SXRpeXi7AdU" ]]; then
                log_error "Fallback password is the known exposed credential - must be rotated!"
                errors=$((errors + 1))
            else
                log_success "Fallback password format is valid and not exposed"
            fi
        else
            log_error "Fallback password format is invalid (expected 12+ chars, alphanumeric)"
            errors=$((errors + 1))
        fi
    fi
    
    return $errors
}

# Test credential generation
test_credential_generation() {
    log_info "Testing credential generation commands..."
    
    local errors=0
    
    # Test API key generation
    log_info "Testing API key generation..."
    local test_api_key
    test_api_key=$(openssl rand -base64 32)
    if [[ ${#test_api_key} -eq 44 && "$test_api_key" =~ ^[A-Za-z0-9+/]{43}=$ ]]; then
        log_success "API key generation works correctly"
    else
        log_error "API key generation failed"
        errors=$((errors + 1))
    fi
    
    # Test OTA password generation
    log_info "Testing OTA password generation..."
    local test_ota_password
    test_ota_password=$(openssl rand -hex 16)
    if [[ ${#test_ota_password} -eq 32 && "$test_ota_password" =~ ^[a-fA-F0-9]{32}$ ]]; then
        log_success "OTA password generation works correctly"
    else
        log_error "OTA password generation failed"
        errors=$((errors + 1))
    fi
    
    # Test fallback password generation
    log_info "Testing fallback password generation..."
    local test_fallback_password
    test_fallback_password=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-12)
    if [[ ${#test_fallback_password} -eq 12 && "$test_fallback_password" =~ ^[A-Za-z0-9]+$ ]]; then
        log_success "Fallback password generation works correctly"
    else
        log_error "Fallback password generation failed"
        errors=$((errors + 1))
    fi
    
    return $errors
}

# Test secrets generation script
test_secrets_generation() {
    log_info "Testing secrets generation script..."
    
    if [[ ! -f "scripts/generate_secrets.sh" ]]; then
        log_error "scripts/generate_secrets.sh not found"
        return 1
    fi
    
    if [[ ! -x "scripts/generate_secrets.sh" ]]; then
        log_warning "scripts/generate_secrets.sh is not executable"
        chmod +x scripts/generate_secrets.sh
        log_info "Made scripts/generate_secrets.sh executable"
    fi
    
    # Backup existing secrets if they exist
    if [[ -f "secrets.yaml" ]]; then
        cp secrets.yaml secrets.yaml.backup.validation
        log_info "Backed up existing secrets.yaml"
    fi
    
    # Test generation
    if ./scripts/generate_secrets.sh >/dev/null 2>&1; then
        log_success "Secrets generation script works correctly"
        
        # Restore backup if it existed
        if [[ -f "secrets.yaml.backup.validation" ]]; then
            mv secrets.yaml.backup.validation secrets.yaml
            log_info "Restored original secrets.yaml"
        fi
        
        return 0
    else
        log_error "Secrets generation script failed"
        
        # Restore backup if it existed
        if [[ -f "secrets.yaml.backup.validation" ]]; then
            mv secrets.yaml.backup.validation secrets.yaml
            log_info "Restored original secrets.yaml"
        fi
        
        return 1
    fi
}

# Main validation function
main() {
    echo "=================================================="
    echo "1Password Structure Validation"
    echo "=================================================="
    echo
    
    local total_errors=0
    
    # Check 1Password CLI
    if ! check_op_cli; then
        exit 1
    fi
    
    # Check account access
    if ! check_account_access; then
        total_errors=$((total_errors + 1))
    fi
    
    # Check vault access
    if ! check_vault_access "Shared" "Home IoT credentials"; then
        total_errors=$((total_errors + 1))
    fi
    
    if ! check_vault_access "Automation" "ESPHome credentials"; then
        total_errors=$((total_errors + 1))
    fi
    
    # Check item structures
    if ! check_item_structure "Shared" "Home IoT" "network name,wireless network password,domain name"; then
        total_errors=$((total_errors + 1))
    fi
    
    if ! check_item_structure "Automation" "ESPHome" "api_key,ota_password,fallback_password"; then
        total_errors=$((total_errors + 1))
    fi
    
    # Validate field values
    if ! validate_field_values "Automation" "ESPHome"; then
        total_errors=$((total_errors + 1))
    fi
    
    # Test credential generation
    if ! test_credential_generation; then
        total_errors=$((total_errors + 1))
    fi
    
    # Test secrets generation script
    if ! test_secrets_generation; then
        total_errors=$((total_errors + 1))
    fi
    
    echo
    echo "=================================================="
    if [[ $total_errors -eq 0 ]]; then
        log_success "All 1Password validations passed!"
        echo "=================================================="
        echo
        echo "1Password structure is correctly configured:"
        echo "• Account '$OP_ACCOUNT' is accessible"
        echo "• Vault 'Shared' contains 'Home IoT' item with WiFi credentials"
        echo "• Vault 'Automation' contains 'ESPHome' item with device credentials"
        echo "• All required fields are present and properly formatted"
        echo "• Credential generation commands work correctly"
        echo "• Secrets generation script is functional"
        exit 0
    else
        log_error "1Password validation failed with $total_errors error(s)"
        echo "=================================================="
        echo
        echo "To fix issues:"
        echo "1. Install 1Password CLI: https://developer.1password.com/docs/cli/get-started/"
        echo "2. Sign in: op signin"
        echo "3. Create required vaults and items as documented in secrets.yaml.example"
        echo "4. Rotate exposed credentials: Follow CREDENTIAL_ROTATION_GUIDE.md"
        echo "5. Re-run validation: ./scripts/validate-1password-structure.sh"
        exit 1
    fi
}

# Run main function
main "$@"