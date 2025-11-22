MSP NCE Pricing Tool - Technical Documentation
eMazzanti Technologies

Application Overview

The MSP NCE Pricing Tool is a self-contained Windows application designed specifically for eMazzanti Technologies to query and manage Microsoft New Commerce Experience (NCE) license-based pricing. This enterprise-grade solution provides a professional web-based user interface for searching Microsoft product pricing, calculating margins, and generating quote drafts.

Key Features

The application offers a comprehensive set of features including CSV file ingestion for pricing data, automated API integration with Microsoft Partner Center for regular price updates, local SQLite database for fast queries, a responsive web UI with Bootstrap 5 and Fluent UI-inspired design, real-time price filtering and search capabilities, dynamic margin calculation with 0-50% range, automated quote draft generation that opens in Notepad, dark mode toggle for user preference, CSV export functionality for pricing data, system tray icon for easy access and management, secure credential storage with encryption, network-accessible web interface on port 5000, and Windows service capability for 24/7 operation.

System Requirements

Prerequisites

The application requires a Windows Server 2016 or later, or Windows 10/11 for operation. At least 4GB RAM is recommended, with 500MB disk space needed. Network connectivity is required for API access and browser-based UI. A modern web browser such as Chrome, Edge, or Firefox is necessary. For service installation, NSSM (Non-Sucking Service Manager) is required and can be downloaded from https://nssm.cc. Administrator privileges are needed for service installation and firewall configuration.

Optional Requirements

For API integration, an Azure AD App Registration is required with Microsoft Partner Center access. If rebuilding from source, Python 3.9 or later is needed.

Azure AD and Partner Center API Setup

To enable automatic pricing updates from Microsoft Partner Center API, you must configure Azure AD authentication.

Step 1: Create Azure AD App Registration

Log into the Azure Portal at https://portal.azure.com with Partner Center admin credentials. Navigate to Azure Active Directory, then App registrations, and click New registration. Enter a name such as "MSP Pricing Tool", select "Accounts in this organizational directory only", and for Redirect URI, select "Public client/native" and enter http://localhost. Click Register and note the Application (client) ID and Directory (tenant) ID for later use.

Step 2: Configure API Permissions

In your app registration, go to API permissions and click Add a permission. Select Microsoft Partner Center from the list. Select Delegated permissions and check "user_impersonation". Click Add permissions and request admin consent if required.

Step 3: Configure Application Settings

On first run, the application will prompt for authentication if API access is configured. Open the application configuration file at data/config.json and add your Azure AD credentials in the following format:

{
  "tenant_id": "your-tenant-id-here",
  "client_id": "your-client-id-here"
}

Note that the client secret and tokens are stored encrypted in the configuration file. Do not edit encrypted values directly.

Step 4: Initial Authentication

When you first trigger an API update via the tray icon menu item "Update from API", a browser window will open for interactive authentication. Sign in with Partner Center admin credentials. After successful authentication, the application will store refresh tokens for future automatic updates. Tokens are encrypted and stored securely in data/config.json.

Installation and Deployment

Installing the Pre-Built Application

Extract the application ZIP file to your desired location, for example C:\MSPPricingTool. Ensure the CSV file Nov_NCE_LicenseBasedPL_GA_US.csv is in the same directory for initial import. The application will automatically import the CSV on first run.

Running as a Desktop Application

Double-click MSP_NCE_Pricing_Tool.exe to start the application. A system tray icon will appear in the notification area. Right-click the tray icon to access the menu with options to open the web UI, update from API, upload CSV file, view about information, or quit the application. Access the web interface by opening a browser and navigating to http://localhost:5000.

Installing as a Windows Service (24/7 Operation)

For production deployment on a Windows Server, install as a service for 24/7 operation.

Download NSSM from https://nssm.cc/download and extract nssm.exe to C:\Windows\System32 or add to your system PATH. Right-click install_service.bat and select "Run as administrator". The script will install the service named "MSPPricingTool", configure it for automatic startup, add a firewall rule for port 5000, and start the service automatically.

To verify the service is running, open Services (services.msc) and look for "MSP NCE Pricing Tool", or check the web UI at http://localhost:5000 or http://your-server-ip:5000 from another machine on the network.

Service Management Commands

To start the service, use: nssm start MSPPricingTool
To stop the service, use: nssm stop MSPPricingTool
To restart the service, use: nssm restart MSPPricingTool
To remove the service, use: nssm remove MSPPricingTool confirm

View service logs at logs/service_stdout.log and logs/service_stderr.log.

Setting Up Automatic Updates

To enable weekly automatic pricing updates from the Partner Center API, run setup_auto_update.bat as administrator. This creates a Windows Scheduled Task that runs every Sunday at 2:00 AM. You can customize the schedule by editing the task in Task Scheduler (taskschd.msc) or modify the setup_auto_update.bat script.

To manually trigger an update at any time, use the tray icon menu or run: schtasks /run /tn MSPPricingAutoUpdate

Using the Application

Accessing the Web Interface

Open a web browser and navigate to http://localhost:5000 for local access or http://server-ip:5000 for network access. If basic authentication is configured, enter the username (default: admin) and password.

Filtering and Searching Prices

The main interface provides multiple filter options. Select a Product from the dropdown to filter by Microsoft product name. Choose a Segment to filter by customer type including Commercial, Education, Government, or Charity. Select a Term Duration to filter by contract length such as P1Y for Annual or P1M for Monthly. Choose a Billing Plan to filter by Annual or Monthly billing. Use the Search box to search across products, SKUs, and descriptions.

Click the "Search Pricing" button to execute the query. Results appear in the scrollable table below with sortable columns.

Viewing and Selecting Prices

The results table displays product information, SKU details, term and billing information, customer segment, and base price in USD. Click any row in the table to select it. The selected row highlights and the large price display updates with the current pricing and margin calculation.

Calculating Margins

The margin calculator on the right side of the interface allows you to adjust the margin percentage. Use the slider to set margin from 0% to 50%, with a default of 20%. The price display updates in real-time showing the base price, margin percentage, and final price per user per month. Enter the quantity of licenses needed in the Quantity field.

Generating Quote Drafts

After selecting a price and setting your margin and quantity, click the "Generate Quote Draft" button. The application will create a formatted quote summary and open it in Notepad automatically. The quote includes product information, SKU details, pricing with margin applied, quantity and total estimate, effective dates, and a description.

Edit the draft in Notepad as needed, save it, and use it as a basis for customer quotes.

Exporting Data

To export the current search results to CSV, click the "Export to CSV" button. The CSV file will download to your browser's default download location with a timestamp in the filename. Open the exported CSV in Excel or any spreadsheet application for further analysis.

Dark Mode Toggle

Click the moon/sun icon button in the bottom-right corner to toggle between light and dark themes. Your preference is saved automatically.

Manual Data Updates

Updating from Partner Center API

Right-click the system tray icon and select "Update from API". The application will authenticate with Microsoft Partner Center and fetch the latest pricing data. A notification will appear indicating success or failure. Check logs/app.log for detailed information if updates fail.

Uploading a CSV File

Right-click the system tray icon and select "Upload CSV File". Browse to your downloaded NCE pricing CSV file from Microsoft. The application will parse the CSV, filter active prices, and update the database. A notification confirms the import status.

The CSV must be in the standard Microsoft NCE format with columns for ChangeIndicator, ProductTitle, ProductId, SkuId, SkuTitle, Publisher, SkuDescription, UnitOfMeasure, TermDuration, BillingPlan, Market, Currency, UnitPrice, PricingTierRangeMin, PricingTierRangeMax, EffectiveStartDate, EffectiveEndDate, Tags, ERP Price, Segment, and PreviousValues.

Security Configuration

Credential Encryption

All sensitive credentials including Azure AD tokens, client secrets, and UI passwords are encrypted using Fernet symmetric encryption. The encryption key is stored in data/.key and should be backed up securely. Never commit the .key file to version control or share it publicly.

Setting UI Authentication

To enable basic authentication for the web UI, edit data/config.json and set ui_username and ui_password. Note that passwords should be set via the configuration management system to ensure encryption. For production deployment, consider using a reverse proxy with more robust authentication such as IIS with Windows Authentication or nginx with OAuth.

Firewall Configuration

The application listens on port 5000 by default. The install_service.bat script automatically adds a Windows Firewall rule. To manually configure, open Windows Defender Firewall with Advanced Security. Create a new inbound rule for port 5000 TCP. Set the action to "Allow the connection" and apply to Domain, Private, and Public profiles as needed.

Network Access

To access the application from other computers on your network, ensure the server's firewall allows port 5000. Use the server's hostname or IP address, for example http://msp-server:5000. For external access, configure your network firewall and consider using HTTPS with a reverse proxy.

Troubleshooting

Application Won't Start

Check if port 5000 is already in use by running: netstat -ano | findstr :5000
Review logs in the logs/ directory, particularly app.log and service_stderr.log. Verify that data/ and logs/ directories have write permissions. Ensure all required DLL files are present if you moved the EXE to a new location.

Database Issues

If the database becomes corrupted, delete data/nce_pricing.db and restart the application. Import the CSV file again via the tray icon. The database will be recreated automatically.

API Authentication Failures

Verify your Azure AD App Registration is configured correctly with the right API permissions. Check that tenant_id and client_id in data/config.json are correct. Try deleting the encrypted tokens from config.json and re-authenticating. Check Partner Center access with your admin account at https://partner.microsoft.com. Review error details in logs/app.log for specific authentication error messages.

Web UI Not Loading

Ensure the application is running by checking for the tray icon or service status. Test local access first at http://localhost:5000 before trying network access. Clear browser cache and try incognito mode. Check browser console for JavaScript errors by pressing F12. Verify templates/query.html exists and is not corrupted.

Service Won't Start

Check the service status in Services (services.msc). Review logs at logs/service_stdout.log and logs/service_stderr.log. Ensure NSSM is installed correctly by running: nssm status MSPPricingTool
Try running the EXE manually first to identify any immediate errors. Verify the service has proper permissions to access the installation directory.

CSV Import Failures

Verify the CSV file is in the correct Microsoft NCE format. Check that the file encoding is UTF-8 with or without BOM. Ensure EffectiveStartDate and EffectiveEndDate columns contain valid ISO 8601 dates. Look for any special characters or formatting issues in the CSV. Check logs/app.log for specific parsing errors.

Performance Issues

If the database becomes very large with more than 100,000 records, consider regular maintenance. The application creates indexes automatically for optimal query performance. Close unused browser tabs to free up memory. Check Windows Task Manager for high CPU or memory usage. Consider deploying on a dedicated server for production use.

Advanced Configuration

Changing the Web Server Port

Edit config.py and modify the PORT constant. Rebuild the application if using the EXE version. Update firewall rules and service configuration accordingly.

Custom Margin Defaults

Edit templates/query.html and modify the default value in the margin slider input from value="20" to your preferred default.

Database Backup

The database is located at data/nce_pricing.db. Regularly back up this file along with data/config.json and data/.key. For automated backups, create a scheduled task to copy these files to a backup location.

Rebuilding from Source

If you need to modify the application or rebuild the EXE, follow these steps.

Install Python 3.9 or later from https://www.python.org. Clone or extract the source code. Open a command prompt in the application directory. Install dependencies by running: pip install -r requirements.txt

Make your desired code changes. Test by running: python main.py

Build the EXE using PyInstaller by running: pyinstaller msp_pricing.spec

The EXE will be created in the dist/ directory. Copy templates/ directory and CSV file to the dist/ folder alongside the EXE.

Logging and Monitoring

Log Files

Application logs are stored in the logs/ directory. The main log file is logs/app.log which contains application events, errors, and warnings. Service logs when running as a Windows service are at logs/service_stdout.log and logs/service_stderr.log. Logs automatically rotate when they reach 10MB, keeping the last 5 log files.

Log Levels

The default log level is INFO. To enable debug logging, edit config.py and change the log level to DEBUG. Restart the application for changes to take effect.

Monitoring Tips

Regularly check logs/app.log for errors or warnings. Monitor disk space in the data/ and logs/ directories. Set up Windows Event Log monitoring for service start/stop events. Consider using a monitoring tool like PRTG or Zabbix for production deployments. Track database update timestamps in the data/metadata table.

Support and Maintenance

For technical support, contact eMazzanti Technologies IT Department. When reporting issues, include the application version, relevant log excerpts from logs/app.log, steps to reproduce the issue, and screenshots if applicable.

Regular Maintenance Tasks

Update the pricing database weekly or bi-weekly using either the API or CSV upload. Back up the database and configuration files monthly. Review logs for errors or warnings monthly. Update the application when new versions are released. Test the web UI and quote generation functionality monthly. Verify that automatic updates are running as scheduled by checking the Task Scheduler history.

Version History

Version 1.0.0 - Initial release with core features including CSV import, web UI, margin calculator, quote generation, and Partner Center API integration.

Technical Architecture

The application consists of several key components. The main.py module serves as the application entry point that coordinates all components. The config.py module handles configuration management and credential encryption. The update_db.py module manages database operations, CSV parsing, and API integration. The app.py module implements the Flask web server and REST API endpoints. The tray.py module provides the system tray icon and menu. The templates/query.html file is the Bootstrap 5 responsive web UI.

The data flow begins with pricing data sourced from either Microsoft Partner Center API or CSV files. This data is processed through parsing and filtering to include only active prices, then stored in a SQLite database with indexes for fast queries. The web UI makes AJAX requests to Flask API endpoints, which query the database and return results in JSON format. The UI updates in real-time using JavaScript and Bootstrap components.

Security features include Fernet symmetric encryption for credentials using the cryptography library, encrypted storage of Azure AD tokens and refresh tokens, optional basic authentication for web UI access, secure token handling with automatic refresh, and local-only database access without external exposure.

Appendix

Useful Commands

To check if the service is running: sc query MSPPricingTool
To view service configuration: nssm dump MSPPricingTool
To test port 5000 locally: curl http://localhost:5000
To view scheduled tasks: schtasks /query /tn MSPPricingAutoUpdate /v
To manually run the update task: schtasks /run /tn MSPPricingAutoUpdate

File and Directory Structure

The installation directory contains the following structure. The main executable is MSP_NCE_Pricing_Tool.exe. Configuration files include config.py, update_db.py, app.py, tray.py, and main.py. The templates/ directory contains the query.html web UI. The data/ directory holds nce_pricing.db (SQLite database), config.json (configuration with encrypted credentials), and .key (encryption key). The logs/ directory contains app.log and service logs. Installation scripts include install_service.bat, setup_auto_update.bat, and auto_update.py. The initial CSV file is Nov_NCE_LicenseBasedPL_GA_US.csv. Documentation includes instructions.md and instructions.docx. Additional files are requirements.txt for Python dependencies and msp_pricing.spec for PyInstaller configuration.

API Endpoints Reference

The web application exposes several REST API endpoints. The root endpoint GET / returns the main query interface HTML page. The GET /api/filters endpoint returns unique values for dropdown filters. The POST /api/query endpoint with JSON body containing filter parameters returns pricing results. The GET /api/price/<id> endpoint returns detailed information for a specific price ID. The POST /api/draft endpoint with JSON body containing price_id, margin, and quantity generates a quote draft. The POST /api/export endpoint with JSON body containing results array exports results to CSV. The GET /api/stats endpoint returns database statistics.

All endpoints require authentication if basic auth is configured.

Microsoft Partner Center API Notes

The application uses the Microsoft Partner Center API for automated pricing updates. The API requires delegated authentication using Azure AD. The primary endpoint is https://api.partnercenter.microsoft.com/v1. Authentication uses MSAL (Microsoft Authentication Library) for Python with the scope https://api.partnercenter.microsoft.com/user_impersonation. The first authentication is interactive via browser. Subsequent authentications use stored refresh tokens. Tokens are automatically refreshed when expired.

Note that the Partner Center API structure may vary. The current implementation provides a foundation that can be adapted to the specific API endpoints and response formats. For initial deployment, CSV-based updates are recommended until API integration is fully validated with your Partner Center account.

Conclusion

The MSP NCE Pricing Tool provides a comprehensive solution for managing Microsoft NCE pricing data with a professional user interface, automated updates, and enterprise-grade security. For questions or support, contact eMazzanti Technologies IT Department.

Generated for eMazzanti Technologies
MSP NCE Pricing Tool v1.0.0
