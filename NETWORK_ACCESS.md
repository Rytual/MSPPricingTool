# Network Access Guide

Complete guide for accessing the MSP NCE Pricing Tool from different network locations.

## Default Credentials

**Username:** Admin
**Password:** Action4T1m3

These credentials are set automatically on first run and provide basic security for the pricing data.

## Access Scenarios

### Scenario 1: Local Server Access

Access from the same machine where the application is running:

```
http://localhost:5000
```

### Scenario 2: Local Network Access

Access from other computers on the same network.

**Find Server IP Address:**

1. On the server, open Command Prompt
2. Run: `ipconfig`
3. Look for "IPv4 Address" under your active network adapter
4. Example: `192.168.1.100`

**Access from other computers:**

```
http://192.168.1.100:5000
```

Replace `192.168.1.100` with your actual server IP address.

**Windows Firewall Configuration:**

The `install_service.bat` script automatically configures the firewall. To verify or manually configure:

```powershell
# Check if rule exists
netsh advfirewall firewall show rule name="MSP Pricing Tool"

# Add rule if needed (run as Administrator)
netsh advfirewall firewall add rule name="MSP Pricing Tool" dir=in action=allow protocol=TCP localport=5000

# To allow from specific IP range only
netsh advfirewall firewall add rule name="MSP Pricing Tool" dir=in action=allow protocol=TCP localport=5000 remoteip=192.168.1.0/24
```

### Scenario 3: External Access (Outside Your Network)

Access the application from outside your local network (home, remote office, etc.).

## External Access Methods

### Method 1: Port Forwarding (Simple but Less Secure)

**Steps:**

1. **Find Your Public IP Address**
   - Visit https://whatismyipaddress.com
   - Note your public IP (e.g., `203.0.113.45`)

2. **Configure Router Port Forwarding**

   Access your router admin panel (usually `192.168.1.1` or `192.168.0.1`):

   - Login to router (check router label for default credentials)
   - Find "Port Forwarding" or "Virtual Server" section
   - Create new rule:
     - **Service Name:** MSP Pricing Tool
     - **External Port:** 5000 (or different for security)
     - **Internal IP:** Your server's local IP (e.g., `192.168.1.100`)
     - **Internal Port:** 5000
     - **Protocol:** TCP
     - **Enable:** Yes

3. **Access Externally**

   From outside your network:
   ```
   http://203.0.113.45:5000
   ```

   Or if you used a different external port (e.g., 8080):
   ```
   http://203.0.113.45:8080
   ```

**Security Considerations:**

- Your pricing data will be accessible from the internet
- Only basic authentication protects the data
- Traffic is NOT encrypted (HTTP, not HTTPS)
- Your public IP may change (use Dynamic DNS service)
- Consider restricting access by IP if possible

**Recommended Security Enhancements:**

- Change the external port to something non-standard (e.g., 8443 instead of 5000)
- Use a firewall rule to allow only specific IP addresses
- Consider VPN instead (see Method 2)

### Method 2: VPN Access (Recommended for Security)

Set up a VPN to your office network, then access as if you're on the local network.

**Advantages:**
- All traffic is encrypted
- No need to expose the application to the internet
- Access other office resources securely
- Better security compliance

**Common VPN Solutions:**

1. **Windows Built-in VPN (PPTP/L2TP)**
   - Configure on Windows Server
   - Connect using Windows VPN client
   - Access via: `http://192.168.1.100:5000`

2. **OpenVPN**
   - Open-source VPN solution
   - Client available for all platforms
   - More secure than PPTP

3. **WireGuard**
   - Modern, fast VPN protocol
   - Simple configuration
   - Excellent performance

4. **Commercial VPN Solutions**
   - TeamViewer VPN
   - Hamachi
   - ZeroTier (free for small networks)

**After VPN is Connected:**

Simply use the local network address:
```
http://192.168.1.100:5000
```

### Method 3: Reverse Proxy with HTTPS (Most Professional)

Use a reverse proxy to add HTTPS encryption and additional security.

**Using IIS (Windows Server):**

1. Install IIS and Application Request Routing (ARR)
2. Configure reverse proxy to `localhost:5000`
3. Add SSL certificate (Let's Encrypt for free)
4. Access via: `https://pricing.yourdomain.com`

**Using Cloudflare Tunnel:**

1. Create Cloudflare account (free)
2. Install Cloudflare Tunnel on server
3. Create tunnel to `localhost:5000`
4. Get public URL with automatic HTTPS
5. No port forwarding needed

## Static IP vs Dynamic IP

**Dynamic IP (Most Common for Home/Small Office):**

Your public IP changes periodically. Solutions:

1. **Dynamic DNS (DDNS)**
   - Services: No-IP, DuckDNS, Dynu (free options)
   - Gives you a domain name: `yourname.ddns.net`
   - Automatically updates when IP changes
   - Access via: `http://yourname.ddns.net:5000`

2. **Router with DDNS Support**
   - Many routers have built-in DDNS client
   - Configure in router settings
   - Automatic updates

**Static IP (Business Internet):**

If you have a static IP from your ISP:
- Your public IP never changes
- Can use it directly or point a domain to it
- More reliable for external access

## Recommended Setup for Different Scenarios

### Small Office (5-20 Users)

**Setup:** Local Network Only

- Install on office server
- Access via local IP: `http://192.168.1.100:5000`
- No external access needed
- Simplest and most secure

### Remote Workers (Occasional Access)

**Setup:** VPN

- Set up office VPN server
- Remote workers connect via VPN
- Access like they're in office
- Secure and professional

### Multiple Locations (Branch Offices)

**Setup:** Site-to-Site VPN + Central Server

- VPN between office locations
- Central server hosts application
- All locations access via private network
- Most secure for business

### Mobile/Frequent External Access

**Setup:** Cloudflare Tunnel or VPN

- Cloudflare Tunnel: Easy, automatic HTTPS, no port forwarding
- Or VPN: More secure, better for compliance
- Avoid simple port forwarding for security reasons

## Testing Your Setup

### Test Local Network Access

From another computer on your network:

1. Open Command Prompt
2. Test connectivity: `ping 192.168.1.100`
3. Open browser: `http://192.168.1.100:5000`
4. Login with Admin/Action4T1m3

### Test External Access (If Configured)

From your phone (using mobile data, not WiFi):

1. Open browser
2. Navigate to: `http://YOUR_PUBLIC_IP:5000`
3. Should prompt for username/password
4. Login with Admin/Action4T1m3

## Troubleshooting

### Cannot Access from Local Network

**Check Windows Firewall:**
```powershell
netsh advfirewall firewall show rule name="MSP Pricing Tool"
```

**Test if port is listening:**
```powershell
netstat -an | findstr :5000
```

Should show: `0.0.0.0:5000` or `*:5000` in LISTENING state

**Test with telnet:**
```powershell
telnet 192.168.1.100 5000
```

If it connects, the server is working. If not, check firewall.

### Cannot Access Externally

1. **Verify port forwarding is enabled** in router
2. **Check your public IP hasn't changed**
3. **Test from outside your network** (use mobile data)
4. **Check ISP doesn't block the port** (some ISPs block common ports)

### Cannot Login (Authentication Fails)

1. **Verify credentials:** Admin / Action4T1m3 (case-sensitive)
2. **Check logs:** `logs\app.log` for authentication errors
3. **Reset credentials:** Delete `data\config.json` and restart

## Security Best Practices

### For Internal Use Only
- Keep application on local network only
- Use Windows Firewall to restrict access
- Regularly update the application
- Backup database regularly

### For External Access
- Always use VPN when possible
- If using port forwarding:
  - Use non-standard ports
  - Implement IP whitelisting
  - Monitor access logs
  - Consider HTTPS reverse proxy
- Change default password
- Keep server updated
- Monitor for unauthorized access attempts

## Changing the Default Password

To change from the default password:

1. Stop the application
2. Edit `data\config.json`
3. Find and modify:
   ```json
   {
     "ui_username": "Admin",
     "ui_password": "YOUR_ENCRYPTED_PASSWORD_HERE"
   }
   ```
4. Or delete `data\config.json` entirely
5. Edit `main.py` to change default password in code
6. Rebuild the application

Alternatively, the password can be changed programmatically by creating a password reset utility.

## Network Diagram Examples

### Local Network Only
```
[Users on Network] ---> [Server (192.168.1.100:5000)] ---> [Application]
```

### External Access via Port Forwarding
```
[Internet Users] ---> [Router (203.0.113.45:5000)] ---> [Server (192.168.1.100:5000)] ---> [Application]
```

### External Access via VPN
```
[Internet Users] ---> [VPN Server] ---> [Private Network] ---> [Server (192.168.1.100:5000)] ---> [Application]
```

## Quick Reference

| Scenario | URL Format | Security |
|----------|-----------|----------|
| Same server | `http://localhost:5000` | High |
| Local network | `http://192.168.1.100:5000` | High |
| Port forwarding | `http://203.0.113.45:5000` | Medium |
| VPN | `http://192.168.1.100:5000` | High |
| Reverse proxy | `https://pricing.company.com` | High |

## Support

For network configuration assistance:
- Check your router manual for port forwarding instructions
- Consult your IT department for VPN setup
- Review Windows Firewall documentation for advanced rules

For application-specific issues:
- Check `logs\app.log` for error messages
- Verify service is running: `nssm status MSPPricingTool`
- Review DEPLOYMENT.md for troubleshooting steps
