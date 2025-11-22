# MSP NCE Pricing Tool

Enterprise-grade Windows application for querying Microsoft New Commerce Experience (NCE) license-based pricing data. Built for managed service providers to streamline pricing operations and quote generation.

## Overview

The MSP NCE Pricing Tool provides a comprehensive solution for managing Microsoft NCE pricing data with automated updates, real-time filtering, margin calculation, and professional quote generation. The application features a modern web interface accessible across your network and can run as a Windows service for continuous availability.

## Key Capabilities

**Data Management**
- CSV ingestion with automatic parsing and validation
- Microsoft Partner Center API integration with automated updates
- SQLite database for high-performance local queries
- Active price filtering based on effective date ranges
- Automated weekly/bi-weekly update scheduling

**User Interface**
- Professional responsive web UI built with Bootstrap 5
- Real-time filtering by product, segment, term duration, and billing plan
- Full-text search across products, SKUs, and descriptions
- Interactive margin calculator with 0-50% range
- Large animated price display with real-time updates
- Dark mode support for user preference
- CSV export for external analysis

**Quote Generation**
- Automated quote draft creation with margin calculations
- Customizable quantity and pricing
- Professional formatting with all relevant details
- Direct integration with Notepad for easy editing

**Enterprise Features**
- Windows service deployment for 24/7 operation
- System tray icon for administrative control
- Secure credential encryption using Fernet
- Optional basic authentication for web UI
- Comprehensive logging and error handling
- Network-accessible across organization

## Installation

### Quick Start

1. Extract the application package to your installation directory
2. Place the Microsoft NCE pricing CSV file in the application directory
3. Execute `MSP_NCE_Pricing_Tool.exe`
4. Navigate to `http://localhost:5000` in your web browser

### Service Installation

For production deployment with automatic startup:

1. Download NSSM (Non-Sucking Service Manager) from https://nssm.cc
2. Execute `install_service.bat` with Administrator privileges
3. Configure firewall rules (handled automatically by installer)
4. Access the web interface at `http://server-ip:5000`

### Automated Updates

Configure scheduled pricing updates:

1. Execute `setup_auto_update.bat` with Administrator privileges
2. Default schedule: Weekly on Sundays at 2:00 AM
3. Customize schedule via Windows Task Scheduler

## Configuration

### Microsoft Partner Center API

For automated pricing updates via API:

1. Create an Azure AD App Registration in your tenant
2. Configure API permissions for Microsoft Partner Center
3. Add credentials to `data/config.json`:
   ```json
   {
     "tenant_id": "your-tenant-id",
     "client_id": "your-client-id"
   }
   ```
4. Complete interactive authentication on first API update

### Web Interface Authentication

Enable basic authentication for web UI access:

1. Edit `data/config.json`
2. Set `ui_username` and `ui_password`
3. Credentials are automatically encrypted on save

## Building from Source

### Prerequisites

- Python 3.9 or later
- Windows operating system
- Visual Studio Build Tools (for some dependencies)

### Build Process

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run application in development mode
python main.py

# Build standalone executable
pyinstaller msp_pricing.spec

# Executable output: dist/MSP_NCE_Pricing_Tool.exe
```

## Architecture

```
MSP NCE Pricing Tool
├── main.py                 Application entry point and orchestration
├── config.py              Configuration and credential management
├── update_db.py           Data ingestion and API integration
├── app.py                 Flask web server and REST API
├── tray.py                System tray interface
├── templates/
│   └── query.html         Web user interface
├── install_service.bat    Windows service installer
├── setup_auto_update.bat  Scheduled update configuration
├── auto_update.py         Automated update script
└── msp_pricing.spec       PyInstaller build specification
```

## Technology Stack

**Backend Technologies**
- Python 3.9+
- Flask web framework
- SQLite database
- MSAL (Microsoft Authentication Library)
- Pandas for data processing

**Frontend Technologies**
- Bootstrap 5 responsive framework
- JavaScript with AJAX for real-time updates
- Modern CSS with dark mode support

**Security & Packaging**
- Fernet symmetric encryption
- PyInstaller for executable packaging
- Secure token management

## System Requirements

**Minimum Requirements**
- Windows Server 2016 or later / Windows 10/11
- 4GB RAM
- 500MB available disk space
- Network connectivity for API access and web UI
- Modern web browser (Chrome, Edge, Firefox)

**For Service Installation**
- Administrator privileges
- NSSM (Non-Sucking Service Manager)
- Open port 5000 TCP (configurable)

## Documentation

Complete technical documentation is available in multiple formats:

- **instructions.md** - Comprehensive markdown documentation
- **instructions.docx** - Microsoft Word format
- **DEPLOYMENT.md** - Deployment guide with checklists

Documentation covers:
- Detailed Azure AD configuration
- API setup and authentication
- Service installation procedures
- Troubleshooting guides
- Advanced configuration options
- Backup and maintenance procedures

## Support

For technical assistance, implementation support, or issue reporting:

**Primary Support**
- eMazzanti Technologies IT Department

**Repository**
- GitHub Issues: https://github.com/Rytual/MSPPricingTool/issues
- Documentation: See instructions.md

## Version History

**Version 1.0.0**
- Initial production release
- Complete NCE pricing management functionality
- Web UI with real-time filtering and search
- Microsoft Partner Center API integration
- Windows service support
- Automated update scheduling
- Quote generation with margin calculation
- Comprehensive documentation

## License

Copyright (c) 2025 eMazzanti Technologies. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.
