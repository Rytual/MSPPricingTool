# Deployment Guide

## Git Repository Setup

The Git repository has been initialized with all project files. To push to GitHub:

### 1. Create GitHub Repository

Go to https://github.com/new and create a new repository named `msp-nce-pricing-tool` (or your preferred name).

Do NOT initialize with README, .gitignore, or license (we already have these).

### 2. Push to GitHub

```bash
# Add the remote repository (replace with your GitHub username/organization)
git remote add origin https://github.com/YOUR_USERNAME/msp-nce-pricing-tool.git

# Push to GitHub
git push -u origin master

# Or if using 'main' as default branch
git branch -M main
git push -u origin main
```

### 3. Enable GitHub Actions

GitHub Actions will automatically run on push. The workflow will:
- Build the EXE on Windows
- Run tests (if any)
- Upload artifacts
- Create releases for tagged versions

To create a release:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Project Structure

All files have been created in C:\price:

### Core Application Files
- `main.py` - Application entry point
- `config.py` - Configuration and encryption
- `update_db.py` - Database and API logic
- `app.py` - Flask web server
- `tray.py` - System tray icon
- `templates/query.html` - Web UI

### Installation Scripts
- `install_service.bat` - NSSM service installer
- `setup_auto_update.bat` - Task scheduler setup
- `auto_update.py` - Auto-update script

### Build Files
- `msp_pricing.spec` - PyInstaller configuration
- `requirements.txt` - Python dependencies
- `convert_to_docx.py` - Markdown to DOCX converter

### Documentation
- `README.md` - Project overview
- `instructions.md` - Comprehensive technical documentation
- `instructions.docx` - Documentation in Word format
- `DEPLOYMENT.md` - This file

### Build Artifacts
- `dist/MSP_NCE_Pricing_Tool.exe` - Built executable
- `build/` - PyInstaller build directory

### Configuration
- `.gitignore` - Git ignore rules
- `.github/workflows/ci-cd.yml` - CI/CD pipeline

## Deployment Steps

### Option 1: Deploy Pre-Built EXE

1. Copy the entire `dist` folder to the target server
2. Ensure the CSV file is in the same directory
3. Run the EXE or install as service using `install_service.bat`

### Option 2: Build from Source on Target

1. Clone the repository on the target server
2. Install Python 3.9+
3. Run: `pip install -r requirements.txt`
4. Run: `pyinstaller msp_pricing.spec`
5. Deploy from `dist/` folder

### Option 3: Deploy via GitHub Release

1. Push a version tag to GitHub
2. GitHub Actions will build and create a release
3. Download the release artifacts
4. Deploy to target server

## Production Deployment Checklist

### Prerequisites
- [ ] Windows Server 2016+ or Windows 10/11
- [ ] NSSM downloaded from https://nssm.cc
- [ ] Azure AD App Registration configured (for API)
- [ ] NCE pricing CSV file available

### Deployment Steps
1. [ ] Copy application files to C:\MSPPricingTool (or desired location)
2. [ ] Copy CSV file to application directory
3. [ ] Configure Azure AD credentials in data/config.json (if using API)
4. [ ] Set UI password (optional): edit data/config.json
5. [ ] Install as Windows service: Run install_service.bat as Administrator
6. [ ] Configure firewall: Port 5000 TCP (done automatically by installer)
7. [ ] Setup automatic updates: Run setup_auto_update.bat as Administrator
8. [ ] Test web UI: Navigate to http://localhost:5000
9. [ ] Test from network: http://server-ip:5000
10. [ ] Verify tray icon appears and functions
11. [ ] Test manual CSV upload via tray icon
12. [ ] Test API update (if configured)
13. [ ] Verify service starts on boot

### Post-Deployment
- [ ] Back up data/config.json and data/.key
- [ ] Document server hostname/IP for end users
- [ ] Create admin user guide
- [ ] Schedule regular backups of data/nce_pricing.db
- [ ] Monitor logs/app.log for errors
- [ ] Set up periodic price update schedule (weekly/bi-weekly)

## Network Configuration

### Firewall Rules
The installer automatically adds a firewall rule for port 5000. To manually configure:

```powershell
New-NetFirewallRule -DisplayName "MSP Pricing Tool" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

### Reverse Proxy (Optional)
For production, consider placing behind a reverse proxy:

**IIS with ARR:**
- Install IIS and Application Request Routing
- Create a reverse proxy to localhost:5000
- Enable Windows Authentication or other auth methods

**nginx:**
```nginx
server {
    listen 80;
    server_name pricing.emazzanti.local;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting Build/Deployment

### Build Issues
- **Pandas won't compile**: Use Python 3.11 or earlier, or update pandas version
- **PyInstaller fails**: Ensure all dependencies are installed
- **Missing DLLs**: Check PyInstaller warnings in build/msp_pricing/warn-msp_pricing.txt

### Deployment Issues
- **EXE won't start**: Check logs/app.log for errors
- **Port 5000 in use**: Stop other services or change PORT in config.py and rebuild
- **Service won't install**: Verify NSSM is in PATH or C:\Windows\System32
- **Firewall blocks access**: Run install_service.bat as Admin or manually add firewall rule

### Runtime Issues
- **Database not updating**: Check logs for API errors, verify Azure AD config
- **Web UI not loading**: Ensure service is running, check firewall
- **Authentication fails**: Clear tokens from data/config.json and re-authenticate

## Backup Strategy

### Critical Files
```
data/nce_pricing.db       # Pricing database
data/config.json          # Configuration and encrypted credentials
data/.key                 # Encryption key
```

### Backup Script Example
```powershell
# backup.ps1
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\Backups\MSPPricing\$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force

Copy-Item "C:\MSPPricingTool\data\*" $backupDir -Recurse
Compress-Archive -Path $backupDir -DestinationPath "$backupDir.zip"
Remove-Item $backupDir -Recurse
```

### Schedule Backups
```powershell
# Create scheduled task for daily backups at 1 AM
schtasks /create /tn "MSP Pricing Backup" /tr "powershell.exe -File C:\MSPPricingTool\backup.ps1" /sc daily /st 01:00 /rl highest
```

## Update Procedure

### Updating the Application

1. Stop the service: `nssm stop MSPPricingTool`
2. Backup current files and database
3. Replace EXE with new version
4. Start the service: `nssm start MSPPricingTool`
5. Verify functionality

### Updating via Git (source deployment)

```bash
cd C:\MSPPricingTool
git pull origin main
pip install -r requirements.txt --upgrade
pyinstaller msp_pricing.spec
nssm restart MSPPricingTool
```

## Monitoring

### Health Checks
- Web UI accessible: http://server:5000
- Service status: `nssm status MSPPricingTool`
- Recent logs: Check logs/app.log
- Database updates: Check metadata table for last_import timestamp

### Automated Monitoring
Set up Windows Task Scheduler or monitoring tool to:
- Check if port 5000 responds
- Verify service is running
- Alert on log errors
- Monitor disk space in data/ and logs/

## Support Contacts

For deployment assistance or issues:
- eMazzanti Technologies IT Department
- GitHub Issues: (repository URL)
- Documentation: instructions.md / instructions.docx

## Version History

- v1.0.0 (2025-01-XX) - Initial release
  - Core functionality complete
  - Web UI with real-time updates
  - API integration
  - Service deployment
  - Automated builds via GitHub Actions
