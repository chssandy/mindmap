#!/bin/bash

set -e

# Detect OS type (fallback mechanism)
OS="unknown"

if [ -f /etc/os-release ]; then
  # Linux standard (Ubuntu, Debian, etc.)
  OS=$(grep -i "^ID=" /etc/os-release | cut -d= -f2 | tr -d '"' | tr '[:upper:]' '[:lower:]')
elif command -v uname >/dev/null; then
  # Fallback to uname (for basic identification on non-standard systems)
  OS=$(uname -s | tr '[:upper:]' '[:lower:]')
fi

# Allow installation only on supported platforms
if [[ "$OS" != "ubuntu" && "$OS" != "debian" && "$OS" != "linux" && "$OS" != "darwin" ]]; then
  echo "Error: Unsupported OS detected ($OS). Only Ubuntu/Debian/Linux/Darwin are supported."
  exit 1
fi

# if  [ "$OS" = "ubuntu" ]; then
#   curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
# fi

# if  [ "$OS" = "debian" ]; then
#   curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
# fi

apt-get update
apt-get install -y nodejs

# Verify installation
node --version
npm --version

# Install markmap-cli
npm install -g markmap-cli

# Verify markmap
markmap --version