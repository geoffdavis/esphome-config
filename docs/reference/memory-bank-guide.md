# Memory Bank Guide

This guide explains how to use and understand the Memory Bank system that
provides authoritative technical information for this project.

## What is the Memory Bank?

The Memory Bank is a comprehensive knowledge system located in
[`.kilocode/rules/memory-bank/`](.kilocode/rules/memory-bank/) that contains
the complete, authoritative technical documentation for this project. It
serves as the single source of truth that other documentation references
rather than duplicates.

## Memory Bank Structure

### Core Files

#### [Brief Overview](.kilocode/rules/memory-bank/brief.md)

- **Purpose**: High-level project summary
- **Content**: Core requirements, goals, and project scope
- **Use**: Quick understanding of what this project does

#### [Product Description](.kilocode/rules/memory-bank/product.md)

- **Purpose**: Detailed product information
- **Content**: Problems solved, user experience goals, success metrics
- **Use**: Understanding why this project exists and how it should work

#### [Current Context](.kilocode/rules/memory-bank/context.md)

- **Purpose**: Current project state and recent changes
- **Content**: Active work, recent developments, next steps
- **Use**: Understanding current focus and recent progress

#### [System Architecture](.kilocode/rules/memory-bank/architecture.md)

- **Purpose**: Complete technical architecture
- **Content**: System design, component relationships, file organization
- **Use**: Understanding how the system is built and organized

#### [Technology Stack](.kilocode/rules/memory-bank/tech.md)

- **Purpose**: Technologies, tools, and dependencies
- **Content**: Development environment, frameworks, tool versions
- **Use**: Setting up development environment and understanding tech choices

#### [Common Tasks](.kilocode/rules/memory-bank/tasks.md)

- **Purpose**: Detailed workflow procedures
- **Content**: Step-by-step task documentation, repetitive procedures
- **Use**: Following established workflows and procedures

## How to Use the Memory Bank

### For Quick Information

Start with the **Brief** and **Product** files:

```bash
# Quick project overview
cat .kilocode/rules/memory-bank/brief.md

# Understand project purpose
cat .kilocode/rules/memory-bank/product.md
```

### For Technical Details

Refer to **Architecture** and **Tech** files:

```bash
# Complete system architecture
less .kilocode/rules/memory-bank/architecture.md

# Technology stack and tools
less .kilocode/rules/memory-bank/tech.md
```

### For Current Work

Check the **Context** file:

```bash
# Current project state
cat .kilocode/rules/memory-bank/context.md
```

### For Procedures

Use the **Tasks** file:

```bash
# Detailed workflow procedures
less .kilocode/rules/memory-bank/tasks.md
```

## Integration with Documentation

### Linking Strategy

The unified documentation system links to Memory Bank content rather than duplicating it:

**Example from Security Overview:**

```markdown
## Security Architecture
For complete security architecture details, see [System Architecture - Security Architecture](.kilocode/rules/memory-bank/architecture.md#security-architecture).
```

**Example from Device Management:**

```markdown
## Common Tasks
For detailed credential management procedures, see [Credential Management Tasks](.kilocode/rules/memory-bank/tasks.md#credential-rotation).
```

### Content Hierarchy

1. **Unified Documentation**: User-friendly guides with essential information
2. **Memory Bank**: Complete technical details and authoritative information
3. **Integration**: Links connect user guides to comprehensive technical details

## Memory Bank Sections

### Architecture File Sections

- **Overview**: System architecture principles
- **Core Architecture Patterns**: Hierarchical configuration, package system, deployment
- **Security Architecture**: Credential management, validation pipeline
- **Device Architecture Patterns**: Different device types and configurations
- **Build and Deployment Architecture**: Task automation, development environment
- **Data Flow Architecture**: Credential flow, device communication, recovery
- **File Organization Patterns**: Project structure and conventions

### Tasks File Sections

- **Device Management Tasks**: Adding devices, sensors, ESP01 deployment
- **Security Management Tasks**: Credential rotation, device recovery, security setup
- **Development Environment Tasks**: Environment setup, tool updates
- **Maintenance Tasks**: Bulk updates, component updates, security audits

### Tech File Sections

- **Core Technologies**: ESPHome, hardware platforms, programming languages
- **Development Environment**: Tool management, task automation, dependencies
- **Security Framework**: Python security library, scripts, testing
- **Quality Assurance**: Pre-commit hooks, code quality tools
- **External Integrations**: 1Password, Home Assistant, development tools

## Finding Information

### By Topic

| Topic | Primary Location | Supporting Documentation |
|-------|------------------|-------------------------|
| **Security** | [Architecture - Security](.kilocode/rules/memory-bank/architecture.md#security-architecture) | [Security Overview](../security/overview.md) |
| **Device Types** | [Architecture - Device Patterns](.kilocode/rules/memory-bank/architecture.md#device-architecture-patterns) | [Device Types](../device-management/device-types.md) |
| **Deployment** | [Architecture - Build/Deploy](.kilocode/rules/memory-bank/architecture.md#build-and-deployment-architecture) | [Two-Stage Deployment](../device-management/two-stage-deployment.md) |
| **Recovery** | [Tasks - Device Recovery](.kilocode/rules/memory-bank/tasks.md#device-recovery) | [Recovery Procedures](../device-management/recovery-procedures.md) |
| **Tools** | [Tech - Development Environment](.kilocode/rules/memory-bank/tech.md#development-environment) | [Development Setup](../getting-started/development-setup.md) |

### By Use Case

| Use Case | Start Here | Then Reference |
|----------|------------|----------------|
| **New to Project** | [Brief](.kilocode/rules/memory-bank/brief.md) → [Product](.kilocode/rules/memory-bank/product.md) | [Quick Start](../getting-started/quick-start.md) |
| **Setting Up Development** | [Tech - Development Environment](.kilocode/rules/memory-bank/tech.md#development-environment) | [Development Setup](../getting-started/development-setup.md) |
| **Understanding Architecture** | [Architecture](.kilocode/rules/memory-bank/architecture.md) | [System Overview](../architecture/system-overview.md) |
| **Following Procedures** | [Tasks](.kilocode/rules/memory-bank/tasks.md) | Topic-specific guides in `docs/` |
| **Current Status** | [Context](.kilocode/rules/memory-bank/context.md) | [Status Reports](../status/) |

## Memory Bank Maintenance

### Content Updates

The Memory Bank is maintained automatically and should not be edited directly. It serves as the authoritative source
that other documentation references.

### Accessing Updates

When Memory Bank content is updated:

1. **Linked documentation** automatically references the latest content
2. **No manual updates** needed in referencing documentation
3. **Single source of truth** ensures consistency

### Integration Benefits

- **No Duplication**: Information exists in one authoritative location
- **Always Current**: Links always point to latest information
- **Comprehensive**: Complete technical details available when needed
- **User-Friendly**: Guides provide accessible entry points to detailed information

## Best Practices

### When to Use Memory Bank Directly

- **Comprehensive technical details** needed
- **Complete procedure documentation** required
- **Authoritative information** for decision-making
- **Understanding system architecture** in depth

### When to Use Unified Documentation

- **Getting started** with the project
- **Following common procedures** with guidance
- **Troubleshooting** with step-by-step help
- **Understanding concepts** before diving into details

### Navigation Tips

1. **Start with unified docs** for user-friendly guidance
2. **Follow links to Memory Bank** for complete technical details
3. **Use Memory Bank sections** to find specific technical information
4. **Reference both** for comprehensive understanding

## Example Usage Workflows

### New Developer Onboarding

1. Read [Brief](.kilocode/rules/memory-bank/brief.md) for project overview
2. Follow [Quick Start Guide](../getting-started/quick-start.md) for setup
3. Reference [Tech - Development Environment](.kilocode/rules/memory-bank/tech.md#development-environment) for
   detailed tool information
4. Use [Tasks](.kilocode/rules/memory-bank/tasks.md) for specific procedures

### Troubleshooting Security Issues

1. Start with [Security Troubleshooting](../security/troubleshooting.md) for common issues
2. Reference [Architecture - Security](.kilocode/rules/memory-bank/architecture.md#security-architecture) for system understanding
3. Follow [Tasks - Security Management](.kilocode/rules/memory-bank/tasks.md#security-management-tasks) for detailed procedures

### Understanding Device Recovery

1. Begin with [Recovery Procedures](../device-management/recovery-procedures.md) for guided steps
2. Reference [Tasks - Device Recovery](.kilocode/rules/memory-bank/tasks.md#device-recovery) for complete technical
   procedures
3. Check [Architecture - Device Patterns](.kilocode/rules/memory-bank/architecture.md#device-architecture-patterns) for
   device-specific considerations

## Related Documentation

- **[Documentation Index](../README.md)** - Main documentation navigation
- **[System Overview](../architecture/system-overview.md)** - High-level architecture guide
- **[Quick Start](../getting-started/quick-start.md)** - Getting started with the project

---

*The Memory Bank system ensures comprehensive, authoritative technical documentation while maintaining user-friendly
access through the unified documentation structure.*
