#!/bin/bash
# Script to install the agent-cli globally

# Get the absolute path to the virtual environment
VENV_PATH="$(pwd)/.venv"
ACTIVATE_PATH="$VENV_PATH/bin/activate"
AGENT_CLI_PATH="$VENV_PATH/bin/agent-cli"

# Check if the virtual environment exists
if [ ! -f "$ACTIVATE_PATH" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Create a wrapper script in /usr/local/bin
WRAPPER_SCRIPT="/usr/local/bin/agent-cli"

echo "Creating wrapper script at $WRAPPER_SCRIPT..."
cat > /tmp/agent-cli-wrapper << EOF
#!/bin/bash
# Wrapper script for agent-cli

# Source the virtual environment
source "$ACTIVATE_PATH"

# Run the agent-cli with all arguments passed to this script
"$AGENT_CLI_PATH" "\$@"
EOF

# Make the wrapper script executable
chmod +x /tmp/agent-cli-wrapper

# Move the wrapper script to /usr/local/bin (requires sudo)
echo "Installing wrapper script to $WRAPPER_SCRIPT (requires sudo)..."
sudo mv /tmp/agent-cli-wrapper "$WRAPPER_SCRIPT"

echo "Installation complete! You can now run 'agent-cli' from anywhere."