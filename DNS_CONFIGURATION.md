# DNS Configuration for MLB.c1632.com

To point the MLB Prediction Tool to the domain MLB.c1632.com, your buddy will need to configure the following DNS records:

## Option 1: Direct IP Configuration (A Record)
If hosting on a VPS or dedicated server:

- **Record Type:** A
- **Host/Name:** @ or MLB (depending on the DNS provider)
- **Value/Points to:** [Server IP Address]
- **TTL:** 3600 (or as recommended by your DNS provider)

## Option 2: Domain Alias Configuration (CNAME Record)
If using a hosting service like Heroku, PythonAnywhere, or similar:

- **Record Type:** CNAME
- **Host/Name:** @ or MLB (depending on the DNS provider)
- **Value/Points to:** 5000-ipaxp344jf7jpibnfbbbo-4477d927.manus.computer
- **TTL:** 3600 (or as recommended by your DNS provider)

## Additional Configuration

### SSL/HTTPS Support
For secure connections, consider:
- Setting up Let's Encrypt for free SSL certificates
- Configuring your web server (Nginx/Apache) to handle SSL termination

### Subdomain Configuration
If you want to use a subdomain like stats.MLB.c1632.com:

- **Record Type:** A or CNAME (as above)
- **Host/Name:** stats
- **Value/Points to:** Same as above

## Verification
After configuring DNS records:
1. Wait for DNS propagation (can take up to 24-48 hours)
2. Verify using: `dig MLB.c1632.com` or `nslookup MLB.c1632.com`
3. Test the website in a browser

## Troubleshooting
If the domain doesn't resolve correctly:
- Verify DNS records are correctly configured
- Check if DNS propagation is complete
- Ensure the web server is properly configured to respond to the domain name
