#!/bin/bash

# Render build script to handle pandas compilation issues

echo "🚀 Starting Render build process..."

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Install numpy first (required for pandas)
echo "📦 Installing numpy..."
pip install numpy>=1.24.0

# Try to install pandas with pre-compiled wheel
echo "📦 Installing pandas with pre-compiled wheel..."
pip install --only-binary=all pandas>=2.2.0

# If that fails, install from PyPI with specific version
if [ $? -ne 0 ]; then
    echo "⚠️  Pre-compiled pandas failed, trying specific version..."
    pip install pandas==2.2.3
fi

# Install the rest of requirements
echo "📦 Installing remaining requirements..."
pip install -r requirements_render.txt

echo "✅ Build completed successfully!"
