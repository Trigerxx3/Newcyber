#!/bin/bash

# Create OSINT tools directory
mkdir -p osint_tools
cd osint_tools

# Install Sherlock
echo "Installing Sherlock..."
git clone https://github.com/sherlock-project/sherlock.git
cd sherlock
python3 -m pip install -r requirements.txt
cd ..

# Install Spiderfoot
echo "Installing Spiderfoot..."
git clone https://github.com/smicallef/spiderfoot.git
cd spiderfoot
python3 -m pip install -r requirements.txt
cd ..

# Make scripts executable
chmod +x sherlock/sherlock.py
chmod +x spiderfoot/sf.py

echo "OSINT tools installation complete!"