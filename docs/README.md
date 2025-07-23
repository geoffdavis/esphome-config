# ESPHome Configuration Documentation

Welcome to the comprehensive documentation for this ESPHome configuration project. This documentation is organized by topic to help you find information quickly and efficiently.

## 🚀 Quick Start

New to this project? Start here:

- **[Quick Start Guide](getting-started/quick-start.md)** - Get up and running in minutes
- **[Development Setup](getting-started/development-setup.md)** - Set up your development environment
- **[Deploy Your First Device](getting-started/first-device.md)** - Step-by-step device deployment

## 📚 Main Documentation Sections

### 🔒 Security
Everything related to credential management and security:
- **[Security Overview](security/overview.md)** - Security framework and best practices
- **[Credential Rotation](security/credential-rotation.md)** - How to rotate exposed credentials
- **[Security Troubleshooting](security/troubleshooting.md)** - Common security issues and solutions

### 🔧 Device Management
Managing your ESPHome devices:
- **[Device Types](device-management/device-types.md)** - ESP32, ESP8266, and ESP01 differences
- **[Two-Stage Deployment](device-management/two-stage-deployment.md)** - ESP01 deployment process
- **[Recovery Procedures](device-management/recovery-procedures.md)** - Device recovery and troubleshooting
- **[Common Tasks](device-management/common-tasks.md)** - Frequently performed operations

### 🏗️ Architecture
Understanding the system design:
- **[System Overview](architecture/system-overview.md)** - High-level architecture and design patterns
- **[File Structure](architecture/file-structure.md)** - Project organization and conventions
- **[Integration Points](architecture/integration-points.md)** - Home Assistant, 1Password, and tool integrations

### 📖 Reference
Complete reference information:
- **[Task Commands](reference/task-commands.md)** - All available task runner commands
- **[Troubleshooting](reference/troubleshooting.md)** - General troubleshooting guide
- **[Memory Bank Guide](reference/memory-bank-guide.md)** - How to use the memory bank system

## 🧠 Memory Bank Integration

This project uses a **Memory Bank** system located in [`.kilocode/rules/memory-bank/`](.kilocode/rules/memory-bank/) that contains the authoritative technical information. The documentation above links to and references memory bank content rather than duplicating it.

### Memory Bank Files
- **[Brief Overview](.kilocode/rules/memory-bank/brief.md)** - Project summary and core requirements
- **[Product Description](.kilocode/rules/memory-bank/product.md)** - What this project does and why
- **[Current Context](.kilocode/rules/memory-bank/context.md)** - Current state and recent changes
- **[System Architecture](.kilocode/rules/memory-bank/architecture.md)** - Complete technical architecture
- **[Technology Stack](.kilocode/rules/memory-bank/tech.md)** - Technologies, tools, and dependencies
- **[Common Tasks](.kilocode/rules/memory-bank/tasks.md)** - Detailed workflow procedures

## 🔄 Status and Historical Information

Current status and historical documentation:
- **[Status Reports](status/)** - Deployment status and current issues
- **[Migration Notes](security/migration-notes.md)** - Historical migration information

## 🆘 Need Help?

1. **Quick Issues**: Check [Troubleshooting](reference/troubleshooting.md)
2. **Security Issues**: See [Security Troubleshooting](security/troubleshooting.md)
3. **Device Issues**: Check [Recovery Procedures](device-management/recovery-procedures.md)
4. **Architecture Questions**: Review [System Overview](architecture/system-overview.md)

## 📝 Documentation Maintenance

This documentation follows a specific integration pattern with the Memory Bank system. See the [Memory Bank Guide](reference/memory-bank-guide.md) for information on how the documentation is organized and maintained.

---

*This documentation structure integrates with the Memory Bank system to provide comprehensive, non-duplicated information about the ESPHome configuration project.*
