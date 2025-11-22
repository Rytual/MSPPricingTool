# MSP NCE Pricing Tool

A self-contained Windows application for eMazzanti Technologies to query Microsoft New Commerce Experience (NCE) license-based pricing.

## Features

- CSV ingestion for Microsoft NCE pricing data
- Microsoft Partner Center API integration for automated updates
- SQLite database for fast local queries
- Professional responsive web UI (Bootstrap 5)
- Real-time filtering and search
- Margin calculator (0-50%)
- Automated quote draft generation
- Dark mode toggle
- CSV export functionality
- System tray icon for easy access
- Windows service support for 24/7 operation
- Secure credential encryption

## Quick Start

### Running the Application

1. Extract the application to your desired location
2. Place the NCE pricing CSV file in the same directory
3. Run `MSP_NCE_Pricing_Tool.exe`
4. Access the web UI at `http://localhost:5000`

### Installing as a Service

1. Download NSSM from https://nssm.cc
2. Run `install_service.bat` as Administrator
3. The application will run 24/7 and start automatically on boot

## Building from Source

### Prerequisites

- Python 3.9 or later
- Windows OS

### Build Steps

```bash
# Install dependencies
pip install -r requirements.txt

# Test the application
python main.py

# Build the EXE
pyinstaller msp_pricing.spec

# The EXE will be in the dist/ directory
```

## Configuration

### Azure AD Setup (for API integration)

1. Create an Azure AD App Registration
2. Add Microsoft Partner Center API permissions
3. Edit `data/config.json` with your tenant_id and client_id
4. On first API update, authenticate via browser

### UI Authentication (optional)

Set `ui_username` and `ui_password` in `data/config.json` to enable basic auth.

## Project Structure

```
.
├── main.py                     # Application entry point
├── config.py                   # Configuration management
├── update_db.py                # Database update logic
├── app.py                      # Flask web server
├── tray.py                     # System tray icon
├── templates/
│   └── query.html              # Web UI
├── install_service.bat         # Service installer
├── setup_auto_update.bat       # Auto-update scheduler
├── auto_update.py              # Auto-update script
├── msp_pricing.spec            # PyInstaller spec
├── requirements.txt            # Python dependencies
└── instructions.md             # Full documentation
```

## Documentation

See `instructions.md` or `instructions.docx` for comprehensive documentation including:
- Azure AD setup
- API configuration
- Service installation
- Troubleshooting
- Advanced configuration

## Technology Stack

- **Backend**: Python, Flask, SQLite, MSAL
- **Frontend**: Bootstrap 5, JavaScript, AJAX
- **Packaging**: PyInstaller
- **Security**: Fernet encryption (cryptography library)

## Requirements

- Windows Server 2016+ or Windows 10/11
- 4GB RAM recommended
- 500MB disk space
- Network connectivity for API and browser UI
- NSSM for service installation

## License

Proprietary - eMazzanti Technologies

## Support

For technical support, contact eMazzanti Technologies IT Department.

## Version

1.0.0 - Initial Release
