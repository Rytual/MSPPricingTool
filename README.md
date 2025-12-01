# MSP NCE Pricing Tool

Enterprise Windows application for querying Microsoft New Commerce Experience (NCE) license-based pricing data. Built for managed service providers to streamline pricing operations and quote generation.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [Option 1: Download Pre-Built Release](#option-1-download-pre-built-release)
  - [Option 2: Clone and Build from Source](#option-2-clone-and-build-from-source)
- [Configuration](#configuration)
- [Usage](#usage)
- [Network Access](#network-access)
- [Windows Service Deployment](#windows-service-deployment)
- [Automatic Updates](#automatic-updates)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Backup and Maintenance](#backup-and-maintenance)
- [License](#license)

---

## Overview

The MSP NCE Pricing Tool provides a web-based interface for managing Microsoft NCE pricing data. The application runs locally or on a server and is accessible via web browser from any device on your network.

Key capabilities:
- Import pricing data from Microsoft NCE CSV files
- Query and filter thousands of SKUs instantly
- Calculate custom markup percentages
- Generate professional quote drafts in browser
- Run as a Windows service for 24/7 availability
- Access from any device on your network

---

## Features

### Data Management
- CSV ingestion with automatic parsing and validation
- Microsoft Partner Center API integration (optional)
- SQLite database for high-performance local queries
- Automated scheduled updates

### User Interface
- Responsive web UI built with Bootstrap 5
- Real-time filtering by product, segment, term duration, and billing plan
- Full-text search across products, SKUs, and descriptions
- Interactive markup calculator (0-50% range)
- Slider automatically adjusts to selected item's actual markup
- Dark mode support
- CSV export functionality

### Quote Generation
- Browser-based quote drafts (opens in new tab)
- Print, copy to clipboard, or save functionality
- Customizable quantity and markup
- Professional formatting

### Enterprise Features
- Windows service deployment for 24/7 operation
- System tray icon for administrative control
- Secure credential encryption using Fernet
- Optional basic authentication for web UI
- Network-accessible across organization
- Comprehensive logging

---

## System Requirements

### Minimum Requirements
- Windows Server 2016+ or Windows 10/11
- 4GB RAM
- 500MB available disk space
- Modern web browser (Chrome, Edge, Firefox)

### For Service Installation
- Administrator privileges
- NSSM (Non-Sucking Service Manager) from https://nssm.cc

### For Building from Source
- Python 3.9 or later
- pip package manager

---

## Installation

### Option 1: Download Pre-Built Release

This is the recommended method for most users.

1. **Download the latest release**
   ```
   Navigate to: https://github.com/Rytual/MSPPricingTool/releases
   Download: MSP_NCE_Pricing_Tool.exe
   ```

2. **Create installation directory**
   ```
   C:\MSPPriceTool\
   ```

3. **Copy required files**
   ```
   MSP_NCE_Pricing_Tool.exe
   Nov_NCE_LicenseBasedPL_GA_US.csv (or your pricing CSV)
   ```

4. **Create templates folder and copy template**
   ```
   C:\MSPPriceTool\templates\
   Copy query.html to templates folder
   ```

5. **Run the application**
   ```
   Double-click MSP_NCE_Pricing_Tool.exe
   ```

6. **Access the web interface**
   ```
   Open browser: http://localhost:5000
   Default credentials: Admin / Action4T1m3
   ```

### Option 2: Clone and Build from Source

Use this method if you need to modify the application or prefer to build from source.

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rytual/MSPPricingTool.git
   cd MSPPricingTool
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run in development mode (optional)**
   ```bash
   python main.py
   ```

4. **Build the executable**
   ```bash
   pyinstaller msp_pricing.spec
   ```

5. **Locate the built executable**
   ```
   dist\MSP_NCE_Pricing_Tool.exe
   ```

6. **Deploy**
   - Copy `dist\MSP_NCE_Pricing_Tool.exe` to your installation directory
   - Copy `templates\` folder to the same directory
   - Copy your NCE pricing CSV file to the same directory
   - Run the executable

---

## Configuration

### Default Credentials

On first run, the application sets default credentials:
- Username: `Admin`
- Password: `Action4T1m3`

### Changing Credentials

1. Stop the application
2. Delete `data\config.json`
3. Edit `main.py` line 27-28 to set new defaults
4. Rebuild or restart the application

### Configuration File

Configuration is stored in `data\config.json` (created automatically):
```json
{
  "tenant_id": "",
  "client_id": "",
  "ui_username": "Admin",
  "ui_password": "[encrypted]"
}
```

### Microsoft Partner Center API (Optional)

For automated pricing updates via API:

1. Create an Azure AD App Registration
2. Configure API permissions for Microsoft Partner Center
3. Add credentials to `data\config.json`:
   ```json
   {
     "tenant_id": "your-tenant-id",
     "client_id": "your-client-id"
   }
   ```
4. Use tray icon menu "Update from API" for first-time authentication

---

## Usage

### Accessing the Web Interface

- Local access: `http://localhost:5000`
- Network access: `http://[server-ip]:5000`

### Filtering and Searching

1. Use dropdown filters to narrow results:
   - Product: Filter by Microsoft product name
   - Segment: Commercial, Education, Government, Charity
   - Term Duration: P1Y (Annual), P1M (Monthly)
   - Billing Plan: Annual or Monthly

2. Use the search box for full-text search

3. Click "Search Pricing" to execute query

### Viewing Prices

- Click any row to select it
- The markup slider automatically adjusts to show the item's actual markup
- The price display shows Partner Price, your markup, and calculated quote price

### Column Definitions

| Column | Description |
|--------|-------------|
| Partner Price | Your cost from Microsoft (what you pay) |
| Microsoft Retail Price | Microsoft's suggested retail price (ERP) |
| Markup % | Percentage difference between Partner and Retail price |

### Generating Quotes

1. Select a price from the results
2. Adjust markup percentage using the slider (optional)
3. Enter quantity
4. Click "Generate Quote Draft"
5. Quote opens in new browser tab with options to:
   - Print Quote
   - Copy to Clipboard
   - Close

### Exporting Data

Click "Export to CSV" to download current search results.

### System Tray Menu

Right-click the tray icon for options:
- Open Web UI
- Update from API
- Upload CSV File
- About
- Quit

---

## Network Access

### Local Network Access

1. Find server IP address:
   ```cmd
   ipconfig
   ```

2. Access from other computers:
   ```
   http://[server-ip]:5000
   ```

### Firewall Configuration

The install_service.bat script configures the firewall automatically. To manually configure:

```powershell
netsh advfirewall firewall add rule name="MSP Pricing Tool" dir=in action=allow protocol=TCP localport=5000
```

### External Access Options

For access outside your local network:

1. **VPN (Recommended)**: Connect via VPN, then use local network address
2. **Port Forwarding**: Configure router to forward port 5000 (less secure)
3. **Reverse Proxy**: Use IIS or nginx with HTTPS (most professional)

---

## Windows Service Deployment

For 24/7 operation on a server:

### Prerequisites

1. Download NSSM from https://nssm.cc
2. Extract `nssm.exe` to `C:\Windows\System32` or add to PATH

### Installation

1. Run as Administrator:
   ```cmd
   install_service.bat
   ```

2. The script will:
   - Install the service named "MSPPricingTool"
   - Configure automatic startup
   - Add firewall rule for port 5000
   - Start the service

### Service Management

```cmd
nssm start MSPPricingTool
nssm stop MSPPricingTool
nssm restart MSPPricingTool
nssm status MSPPricingTool
nssm remove MSPPricingTool confirm
```

---

## Automatic Updates

### Setting Up Scheduled Updates

Run as Administrator:
```cmd
setup_auto_update.bat
```

This creates a scheduled task that runs every Sunday at 2:00 AM.

### Manual Update

- Via tray icon: Right-click and select "Upload CSV File" or "Update from API"
- Via command line: `schtasks /run /tn MSPPricingAutoUpdate`

---

## Architecture

### Directory Structure

```
MSPPriceTool/
├── MSP_NCE_Pricing_Tool.exe    # Main application
├── templates/
│   └── query.html              # Web user interface
├── data/                       # Created at runtime
│   ├── nce_pricing.db          # SQLite database
│   ├── config.json             # Configuration (encrypted)
│   └── .key                    # Encryption key
├── logs/                       # Created at runtime
│   └── app.log                 # Application logs
├── Nov_NCE_LicenseBasedPL_GA_US.csv  # Pricing data
├── install_service.bat         # Service installer
├── setup_auto_update.bat       # Scheduled task setup
└── auto_update.py              # Update script
```

### Source Code Structure

```
├── main.py                 # Application entry point
├── config.py               # Configuration management
├── update_db.py            # Database and CSV/API operations
├── app.py                  # Flask web server and REST API
├── tray.py                 # System tray interface
├── templates/
│   └── query.html          # Web UI (Bootstrap 5)
├── requirements.txt        # Python dependencies
└── msp_pricing.spec        # PyInstaller build configuration
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.9+, Flask |
| Database | SQLite |
| Frontend | Bootstrap 5, JavaScript |
| Authentication | MSAL (Microsoft), Fernet encryption |
| Data Processing | Pandas |
| Packaging | PyInstaller |
| Service Management | NSSM |

---

## API Reference

All endpoints require authentication if configured.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/api/filters` | GET | Get filter dropdown values |
| `/api/query` | POST | Query prices with filters |
| `/api/price/<id>` | GET | Get specific price details |
| `/api/draft` | POST | Generate quote draft HTML |
| `/api/export` | POST | Export results to CSV |
| `/api/stats` | GET | Database statistics |

### Query Endpoint Example

```json
POST /api/query
{
  "product": "Microsoft 365",
  "segment": "Commercial",
  "term": "P1Y",
  "billing": "Annual",
  "search": ""
}
```

---

## Troubleshooting

### Application Will Not Start

1. Check if port 5000 is in use:
   ```cmd
   netstat -ano | findstr :5000
   ```

2. Review logs:
   ```
   logs\app.log
   ```

3. Verify write permissions on data\ and logs\ directories

### Database Issues

1. Delete corrupted database:
   ```cmd
   del data\nce_pricing.db
   ```

2. Restart application and re-import CSV

### Web UI Not Loading

1. Verify application is running (check tray icon)
2. Test local access first: `http://localhost:5000`
3. Check firewall settings
4. Clear browser cache

### Service Issues

1. Check service status:
   ```cmd
   nssm status MSPPricingTool
   ```

2. Review service logs:
   ```
   logs\service_stdout.log
   logs\service_stderr.log
   ```

3. Try running EXE manually to identify errors

### Authentication Failures

1. Delete tokens and re-authenticate:
   - Edit `data\config.json`
   - Remove `access_token` and `refresh_token` entries
   - Restart and re-authenticate via tray menu

---

## Backup and Maintenance

### Critical Files to Backup

```
data\nce_pricing.db     # Pricing database
data\config.json        # Configuration
data\.key               # Encryption key (required to decrypt config)
```

### Backup Script Example

```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\Backups\MSPPricing"
New-Item -ItemType Directory -Path $backupDir -Force
Copy-Item "C:\MSPPriceTool\data\*" "$backupDir\$timestamp" -Recurse
```

### Maintenance Schedule

| Task | Frequency |
|------|-----------|
| Update pricing data | Weekly |
| Review logs | Monthly |
| Backup database | Monthly |
| Test quote generation | Monthly |

---

## License

Copyright 2025 eMazzanti Technologies. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## Support

For technical assistance:
- GitHub Issues: https://github.com/Rytual/MSPPricingTool/issues
- eMazzanti Technologies IT Department
