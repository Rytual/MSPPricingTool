# Claude Development Reference - MSP NCE Pricing Tool

This document provides comprehensive context for Claude (or any AI assistant) to understand and continue development on this project.

---

## Project Overview

**Name:** MSP NCE Pricing Tool
**Purpose:** Enterprise Windows application for querying Microsoft New Commerce Experience (NCE) license-based pricing data
**Owner:** eMazzanti Technologies
**Users:** Sales team and network engineers
**Repository:** https://github.com/Rytual/MSPPricingTool

### What It Does

- Imports Microsoft NCE pricing data from CSV files (downloaded from Partner Center)
- Provides a web-based search/filter interface at `http://localhost:5000`
- Calculates markup percentages for quoting
- Generates printable quote drafts
- Runs as a system tray application on Windows
- Can be deployed for 24/7 operation via Windows Scheduled Task

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.9+ |
| Web Framework | Flask | 3.0+ |
| Database | SQLite | 3 |
| Frontend | Bootstrap 5, jQuery, DataTables | Latest |
| Data Processing | Pandas | 2.2+ |
| System Tray | pystray, Pillow | Latest |
| API Auth | MSAL (Microsoft) | 1.25+ |
| Encryption | cryptography (Fernet) | 41+ |
| Packaging | PyInstaller | 6.3+ |

---

## Directory Structure

### Development Directory (C:\price)

```
C:\price/
├── .git/                    # Git repository
├── .gitignore               # Git ignore rules
├── data/                    # Runtime data (gitignored)
│   ├── nce_pricing.db       # SQLite database
│   ├── config.json          # Configuration
│   └── .key                 # Fernet encryption key
├── dist/                    # PyInstaller output (gitignored)
├── logs/                    # Application logs (gitignored)
├── static/
│   └── microsoft-partner.png # Logo displayed in header
├── templates/
│   └── query.html           # Main web UI (Bootstrap 5)
├── app.py                   # Flask web server and REST API
├── config.py                # Configuration management
├── main.py                  # Application entry point
├── tray.py                  # System tray interface
├── update_db.py             # Database and CSV/API operations
├── auto_update.py           # Scheduled update script
├── msp_pricing.spec         # PyInstaller build configuration
├── requirements.txt         # Python dependencies
├── install_service.bat      # NSSM service installer
├── setup_auto_update.bat    # Scheduled task for auto-updates
├── MSP_NCE_Pricing_Tool.exe # Pre-built executable
├── Nov_NCE_LicenseBasedPL_GA_US.csv # Sample pricing data
├── README.md                # User documentation
├── NETWORK_ACCESS.md        # Network configuration guide
└── CLAUDE.md                # This file
```

### Deployment Directory (C:\MSPPriceTool)

When deployed, users only need:

```
C:\MSPPriceTool/
├── MSP_NCE_Pricing_Tool.exe  # Main application
├── Nov_NCE_LicenseBasedPL_GA_US.csv # Pricing data
├── microsoft-partner.png     # Logo (optional, bundled in EXE)
├── install_service.bat       # Optional service installer
├── setup_auto_update.bat     # Optional auto-update setup
├── README.md                 # Documentation
├── NETWORK_ACCESS.md         # Network guide
├── data/                     # Created at runtime
└── logs/                     # Created at runtime
```

---

## Source Code Architecture

### main.py (Entry Point)

**Purpose:** Application launcher and coordinator

**Key Functions:**
- `check_database_exists()` - Verifies SQLite database presence
- `initial_setup()` - First-run initialization
- `get_db_record_count()` - Queries pricing record count
- `run_web_server()` - Spawns Flask server in daemon thread
- `run_tray()` - Spawns system tray icon in main thread
- `main()` - Orchestrates startup sequence

**Flow:**
1. Initialize logging
2. Initialize database (`update_db.init_database()`)
3. Check for and import initial CSV if database empty
4. Start Flask web server in background thread
5. Start system tray in foreground (blocking)

**Important:** Previously set default credentials here (removed). Authentication code still exists in app.py but is bypassed when no password is configured.

---

### app.py (Flask Web Server)

**Purpose:** REST API and web interface

**Key Components:**

1. **Path Resolution** (lines 17-25):
   ```python
   if getattr(sys, 'frozen', False):
       template_folder = str(Path(sys._MEIPASS) / 'templates')
       static_folder = str(Path(sys._MEIPASS) / 'static')
   else:
       template_folder = str(BASE_DIR / 'templates')
       static_folder = str(BASE_DIR / 'static')
   ```

2. **Authentication** (lines 39-64):
   - `check_auth()` - Returns True if no password set
   - `requires_auth` decorator - Bypasses auth if no password configured
   - HTTP Basic Auth used when password is set

3. **API Endpoints:**
   | Endpoint | Method | Description |
   |----------|--------|-------------|
   | `/` | GET | Main web interface |
   | `/api/filters` | GET | Filter dropdown values |
   | `/api/query` | POST | Search prices with filters |
   | `/api/price/<id>` | GET | Single price details |
   | `/api/draft` | POST | Generate quote HTML |
   | `/api/export` | POST | Export to CSV |
   | `/api/stats` | GET | Database statistics |

4. **Database Connection:**
   - SQLite at `BASE_DIR / "data" / DB_NAME`
   - Uses `sqlite3.Row` for dict-like access

---

### config.py (Configuration)

**Purpose:** Configuration management with encryption

**Key Constants:**
```python
APP_NAME = "MSP NCE Pricing Tool"
APP_VERSION = "1.0.0"
DB_NAME = "nce_pricing.db"
PORT = 5000
HOST = "0.0.0.0"  # Network accessible
```

**Path Resolution:**
```python
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent.absolute()
else:
    BASE_DIR = Path(__file__).parent.absolute()
```

**Encryption:**
- Uses Fernet symmetric encryption
- Key stored in `data/.key`
- Used for API tokens (client_secret, refresh_token, access_token)

**Config Properties:**
- `tenant_id`, `client_id` - Azure AD credentials (plaintext)
- `client_secret`, `refresh_token`, `access_token` - Encrypted
- `ui_username`, `ui_password` - For web UI auth (currently unused)
- `last_update` - ISO timestamp

---

### update_db.py (Database Operations)

**Purpose:** CSV ingestion and Partner Center API integration

**Database Schema:**
```sql
CREATE TABLE prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ChangeIndicator TEXT,
    ProductTitle TEXT,
    ProductId TEXT,
    SkuId TEXT,
    SkuTitle TEXT,
    Publisher TEXT,
    SkuDescription TEXT,
    UnitOfMeasure TEXT,
    TermDuration TEXT,          -- P1Y, P1M, P3Y
    BillingPlan TEXT,
    Market TEXT,
    Currency TEXT,
    UnitPrice REAL,             -- Partner price (cost)
    PricingTierRangeMin TEXT,
    PricingTierRangeMax TEXT,
    EffectiveStartDate TEXT,
    EffectiveEndDate TEXT,
    Tags TEXT,
    ERPPrice REAL,              -- Microsoft retail price
    Segment TEXT,
    PreviousValues TEXT,
    imported_at TIMESTAMP
);

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
);
```

**Key Functions:**
- `init_database()` - Creates tables and indexes
- `ingest_csv(csv_path, force=False)` - Imports CSV, checks hash to avoid duplicate imports
- `calculate_csv_hash()` - MD5 hash for change detection
- `get_msal_app()` - Creates MSAL PublicClientApplication
- `acquire_token_interactive()` - Browser-based OAuth login
- `acquire_token_silent()` - Silent token refresh
- `fetch_from_partner_center_api()` - Fetches from Partner Center (not fully implemented)

**CSV Import Notes:**
- Renames "ERP Price" column to "ERPPrice"
- Uses pandas with UTF-8-BOM encoding
- Clears and rebuilds entire database on import

---

### tray.py (System Tray)

**Purpose:** Windows system tray icon and menu

**Menu Items:**
1. Open Web UI (default) - Opens browser to localhost:5000
2. Update from API - Triggers Partner Center API fetch
3. Upload CSV File - Opens file dialog for CSV selection
4. About - Shows version info
5. Quit - Graceful shutdown

**Icon Generation:**
- Creates 64x64 image programmatically
- Microsoft blue background (#0078D4)
- White dollar sign ($)

**Dependencies:**
- pystray - System tray functionality
- PIL/Pillow - Image generation
- tkinter - File dialog

---

### templates/query.html (Web UI)

**Purpose:** Main user interface

**Features:**
- Bootstrap 5 responsive design
- Dark mode support (CSS classes)
- DataTables for results display
- Real-time filtering via AJAX
- Markup calculator with slider (0-50%)
- Quote draft generation (opens in new browser tab)
- CSV export

**Key JavaScript Functions:**
- `loadFilters()` - Populates dropdowns from `/api/filters`
- `searchPricing()` - Queries `/api/query` with filters
- `selectPrice(id)` - Handles row selection, updates calculator
- `generateDraft()` - Calls `/api/draft`, opens result in new tab
- `exportCSV()` - Calls `/api/export`, downloads file

**Header Structure:**
```html
<div class="header-bar">
    <img src="/static/microsoft-partner.png" ...>
    <h1>MSP NCE Pricing Tool</h1>
    <small>eMazzanti Technologies - Microsoft Partner Center Pricing</small>
</div>
```

---

### msp_pricing.spec (PyInstaller)

**Purpose:** Build configuration for standalone EXE

**Key Settings:**
```python
datas=[
    ('templates', 'templates'),
    ('static', 'static'),
    ('Nov_NCE_LicenseBasedPL_GA_US.csv', '.'),
]
console=False  # No console window
```

**Build Command:**
```bash
pyinstaller msp_pricing.spec
```

**Output:** `dist/MSP_NCE_Pricing_Tool.exe` (~50MB)

---

## Deployment Methods

### Method 1: Scheduled Task (Recommended)

Runs application at system startup under a specific user account. Provides 24/7 web access and tray icon when user RDPs in.

```cmd
schtasks /create /tn "MSPPricingTool" /tr "C:\MSPPriceTool\MSP_NCE_Pricing_Tool.exe" /sc onstart /ru "DOMAIN\Username" /rp * /rl highest
```

### Method 2: Windows Service with NSSM

Runs as true Windows service. No tray icon (services run in Session 0). Requires NSSM download.

```cmd
nssm install MSPPricingTool "C:\MSPPriceTool\MSP_NCE_Pricing_Tool.exe"
nssm start MSPPricingTool
```

**Limitation:** No GUI/tray access. CSV updates require manual file replacement or future web upload feature.

---

## Authentication System (Currently Disabled)

The application has a complete HTTP Basic Auth system that is currently bypassed:

**How it works:**
1. `main.py` previously set default credentials on startup (removed)
2. `config.py` stores encrypted `ui_password`
3. `app.py` has `@requires_auth` decorator
4. Decorator checks `if not config.ui_password: return f(*args, **kwargs)` (bypass)

**To re-enable authentication:**
1. In `main.py`, add back:
   ```python
   if not config.ui_password:
       config.ui_username = "Admin"
       config.ui_password = "YourPassword"
   ```
2. Rebuild EXE

---

## Microsoft Partner Center API

**Status:** Partially implemented, not configured

**Required for API access:**
1. Azure AD App Registration
2. API permissions for Partner Center
3. Configure `tenant_id` and `client_id` in `data/config.json`
4. First-time interactive browser authentication via tray menu

**Endpoint:** `https://api.partnercenter.microsoft.com/v1/ratecards/azure`

**Note:** CSV import is currently the primary data source. API integration was stubbed but recommends CSV.

---

## Known Issues and Limitations

1. **Partner Center API** - Not fully implemented, recommends CSV import
2. **Single instance** - No mutex/lock to prevent multiple instances
3. **Large CSV handling** - Entire database is cleared and rebuilt on import
4. **No web-based CSV upload** - Requires tray icon access

---

## Future Enhancement Ideas

1. **Web-based CSV upload** - Add file upload to web UI for service deployment
2. **Multiple instance prevention** - Add mutex lock
3. **Incremental CSV updates** - Diff-based import instead of full rebuild
4. **User management** - Multi-user auth with roles
5. **Price change alerts** - Notify on significant price changes
6. **Quote history** - Save generated quotes to database
7. **API integration completion** - Full Partner Center API support

---

## Development Workflow

### Making Changes

1. Edit source files in `C:\price`
2. Test by running `python main.py`
3. Build EXE: `pyinstaller msp_pricing.spec`
4. Test EXE from `dist/` folder
5. Copy EXE to root: `copy dist\MSP_NCE_Pricing_Tool.exe .`
6. Commit and push to GitHub

### Git Workflow

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

### Testing Checklist

- [ ] Application starts without errors
- [ ] Web UI loads at localhost:5000
- [ ] Filters populate correctly
- [ ] Search returns results
- [ ] Row selection works
- [ ] Markup calculator updates
- [ ] Quote draft generates
- [ ] CSV export downloads
- [ ] Tray icon appears
- [ ] Tray menu items work
- [ ] CSV upload via tray works

---

## Important Files Summary

| File | Purpose | Edit Frequency |
|------|---------|----------------|
| `app.py` | Web server, API endpoints | High |
| `templates/query.html` | User interface | High |
| `main.py` | Startup logic | Low |
| `config.py` | Configuration | Low |
| `update_db.py` | Database operations | Medium |
| `tray.py` | System tray | Low |
| `msp_pricing.spec` | Build config | Low |
| `README.md` | User documentation | Medium |

---

## Contact and Support

- **Repository:** https://github.com/Rytual/MSPPricingTool
- **Issues:** https://github.com/Rytual/MSPPricingTool/issues
- **Organization:** eMazzanti Technologies

---

*Last Updated: December 2025*
