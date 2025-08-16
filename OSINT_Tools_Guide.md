# OSINT Tools Installation and Usage Guide

## Successfully Installed Tools

✅ **Sherlock** - Find usernames across social networks  
✅ **SpiderFoot** - Automated reconnaissance and intelligence gathering

## Installation Summary

Both tools have been successfully installed on your Windows system:
- Sherlock: Installed via pip and available globally as `sherlock` command
- SpiderFoot: Installed locally in `osint_tools\spiderfoot\` directory

## Usage Instructions

### 1. Sherlock - Username Investigation

**Basic Command:**
```powershell
sherlock username
```

**Examples:**
```powershell
# Search for a single username
sherlock john_doe

# Search multiple usernames
sherlock john_doe jane_smith

# Save results to file
sherlock john_doe -o results.txt

# Save results in CSV format
sherlock john_doe --csv

# Save results in Excel format
sherlock john_doe --xlsx

# Search only specific sites
sherlock john_doe --site Instagram --site Twitter

# Use proxy
sherlock john_doe --proxy socks5://127.0.0.1:1080

# Verbose output for debugging
sherlock john_doe --verbose
```

**Output Options:**
- Results are displayed in terminal by default
- Use `-o filename` to save to a specific file
- Use `--csv` for CSV format
- Use `--xlsx` for Excel format
- Use `--folderoutput` for multiple usernames

### 2. SpiderFoot - Reconnaissance Tool

**Basic Command:**
```powershell
python osint_tools\spiderfoot\sf.py -s TARGET
```

**Examples:**
```powershell
# Basic domain reconnaissance
python osint_tools\spiderfoot\sf.py -s example.com

# IP address investigation
python osint_tools\spiderfoot\sf.py -s 192.168.1.1

# Email address investigation
python osint_tools\spiderfoot\sf.py -s user@example.com

# List available modules
python osint_tools\spiderfoot\sf.py -M

# List available event types
python osint_tools\spiderfoot\sf.py -T

# Use specific modules
python osint_tools\spiderfoot\sf.py -s example.com -m sfp_dnsresolve,sfp_whois

# Passive reconnaissance only
python osint_tools\spiderfoot\sf.py -s example.com -u passive

# Save output to CSV
python osint_tools\spiderfoot\sf.py -s example.com -o csv > results.csv

# Start web interface (GUI)
python osint_tools\spiderfoot\sf.py -l 127.0.0.1:5001
# Then open browser to: http://127.0.0.1:5001
```

**SpiderFoot Use Cases:**
- `passive`: Safe, non-intrusive reconnaissance
- `footprint`: Network footprinting
- `investigate`: Detailed investigation
- `all`: All available modules

## Key Features

### Sherlock Features:
- ✅ 400+ social media platforms
- ✅ Fast concurrent checking
- ✅ Multiple output formats
- ✅ Tor support
- ✅ Proxy support
- ✅ CSV/Excel export

### SpiderFoot Features:
- ✅ 200+ reconnaissance modules
- ✅ Web-based GUI interface
- ✅ Multiple target types (domains, IPs, emails)
- ✅ Automated data correlation
- ✅ Export capabilities
- ✅ Passive and active scanning modes

## Security Notes

⚠️ **Important Considerations:**
- Always ensure you have permission to investigate targets
- Use responsibly and ethically
- Consider using VPN/Tor for sensitive investigations
- Be aware of rate limits on various platforms
- Some SpiderFoot modules may trigger security alerts

## Troubleshooting

If you encounter issues:

1. **Sherlock not found**: Restart your terminal/PowerShell
2. **SpiderFoot errors**: Make sure you're in the correct directory
3. **Module issues**: Update pip packages: `python -m pip install --upgrade [package]`
4. **Permission errors**: Run PowerShell as administrator if needed

## Quick Start Examples

**Find social media accounts:**
```powershell
sherlock testuser --csv
```

**Domain reconnaissance:**
```powershell
python osint_tools\spiderfoot\sf.py -s example.com -u passive -o csv > domain_results.csv
```

**Start SpiderFoot web interface:**
```powershell
python osint_tools\spiderfoot\sf.py -l 127.0.0.1:5001
```

## File Structure
```
D:\new cyber\
├── osint_tools\
│   ├── sherlock\          # Sherlock source code
│   └── spiderfoot\        # SpiderFoot source code
├── install_osint_tools.ps1  # Installation script
└── OSINT_Tools_Guide.md     # This guide
```

## Legal Notice
These tools are for legitimate security research and authorized testing only. Always comply with applicable laws and terms of service.
