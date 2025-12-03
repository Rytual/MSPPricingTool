# MSP NCE Pricing Tool

A pricing lookup and quote generation tool for Microsoft New Commerce Experience (NCE) licenses. Built for eMazzanti Technologies sales team and engineers.

---

## Quick Start

1. **Download** - Download the ZIP from GitHub and extract to any folder
2. **Run** - Double-click `MSP_NCE_Pricing_Tool.exe`
3. **Access** - Open your browser to `http://localhost:5000`

That's it! The application runs in your system tray and serves a web interface for looking up Microsoft pricing.

---

## What This Tool Does

- **Search Microsoft NCE Pricing** - Quickly find pricing for any Microsoft 365, Azure, or other NCE product
- **Filter by Product, Segment, Term, and Billing Plan** - Narrow down results to exactly what you need
- **Calculate Custom Markup** - Adjust markup percentage (0-50%) to see your quote price
- **Generate Quote Drafts** - Create professional quote summaries with one click
- **Export to CSV** - Download search results for spreadsheets or further analysis

---

## Using the Tool

### Accessing the Web Interface

Once the application is running (you'll see a "$" icon in your system tray):

- **On the same computer**: Open `http://localhost:5000`
- **From another computer on the network**: Open `http://[server-ip]:5000`

### Finding Prices

1. Use the **filter dropdowns** to narrow by Product, Segment, Term Duration, or Billing Plan
2. Or use the **Search box** to search by product name, SKU, or description
3. Click **Search Pricing** to see results

### Creating a Quote

1. Search for the product you need
2. Click on a row in the results table to select it
3. Adjust the **Markup Percentage** slider if needed (default is 20%)
4. Enter the **Quantity** of licenses
5. Click **Generate Quote Draft** to create a printable quote summary

### Exporting Data

Click **Export to CSV** to download the current search results as a spreadsheet file.

---

## System Tray Menu

Right-click the "$" icon in your system tray to access:

- **Open Web UI** - Opens the pricing tool in your browser
- **Update from API** - Fetch latest pricing from Microsoft Partner Center (requires configuration)
- **Upload CSV File** - Import a new pricing CSV file
- **About** - Version information
- **Quit** - Close the application

---

## Updating Pricing Data

### Option 1: Upload a New CSV

1. Download the latest NCE pricing CSV from Microsoft Partner Center
2. Right-click the tray icon and select **Upload CSV File**
3. Select your downloaded CSV file
4. The database will update automatically

### Option 2: Keep CSV in Application Folder

Place any CSV file with "NCE" in the filename in the same folder as the EXE. The application will detect and import it on startup if the database is empty.

---

## Network Access

### Allow Other Computers to Access the Tool

If you want others on your network to use the pricing tool:

1. **Run as Administrator** and execute `install_service.bat` - this sets up a Windows service and firewall rule
2. Share the server's IP address with your team (e.g., `http://192.168.1.100:5000`)

### Finding Your Server's IP Address

Open Command Prompt and run:
```
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

---

## Running as a Windows Service

For servers or always-on access:

1. Download [NSSM](https://nssm.cc/download) (Non-Sucking Service Manager)
2. Extract `nssm.exe` to `C:\Windows\System32`
3. Run `install_service.bat` as Administrator

The service will:
- Start automatically when Windows boots
- Run in the background without requiring a logged-in user
- Restart automatically if it crashes

### Managing the Service

```
nssm start MSPPricingTool      # Start the service
nssm stop MSPPricingTool       # Stop the service
nssm restart MSPPricingTool    # Restart the service
nssm remove MSPPricingTool     # Uninstall the service
```

---

## Files Included

| File | Purpose |
|------|---------|
| `MSP_NCE_Pricing_Tool.exe` | The main application |
| `Nov_NCE_LicenseBasedPL_GA_US.csv` | Sample pricing data (replace with current data) |
| `install_service.bat` | Installs as Windows service (optional) |
| `setup_auto_update.bat` | Sets up scheduled pricing updates (optional) |
| `microsoft-partner.png` | Microsoft Partner logo |
| `README.md` | This documentation |
| `NETWORK_ACCESS.md` | Detailed network configuration guide |

### Files Created at Runtime

The application creates these folders/files when first run:

- `data/` - Contains the SQLite database and configuration
- `logs/` - Contains application logs for troubleshooting

---

## Troubleshooting

### Application won't start

- Make sure no other application is using port 5000
- Check `logs/app.log` for error messages
- Try running as Administrator

### Can't access from another computer

- Verify Windows Firewall allows port 5000 (run `install_service.bat` to configure)
- Check that both computers are on the same network
- Verify the server IP address is correct

### Pricing data seems old

- Upload a fresh CSV from Microsoft Partner Center
- Or use the tray menu to update from API (requires Azure AD configuration)

### Browser shows authentication prompt

This shouldn't happen with the current version. If it does:
1. Close the application
2. Delete the `data/config.json` file
3. Restart the application

---

## Support

For issues or questions:

- **Internal**: Contact eMazzanti Technologies IT Department
- **GitHub**: https://github.com/Rytual/MSPPricingTool/issues

---

## Version

**Version 1.0.0** - MSP NCE Pricing Tool

Copyright (c) 2025 eMazzanti Technologies. All rights reserved.
