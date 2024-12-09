#!/bin/bash

# install.sh - Automated setup script for AI-Data-Security project

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print messages in color
print_message() {
    local type="$1"
    local message="$2"
    case "$type" in
        "info")
            echo -e "\e[34m[INFO]\e[0m $message"
            ;;
        "success")
            echo -e "\e[32m[SUCCESS]\e[0m $message"
            ;;
        "warning")
            echo -e "\e[33m[WARNING]\e[0m $message"
            ;;
        "error")
            echo -e "\e[31m[ERROR]\e[0m $message"
            ;;
        *)
            echo "$message"
            ;;
    esac
}

# Function to check if the script is run from the project root
check_project_root() {
    if [ ! -f "app.py" ] || [ ! -f "config.yaml" ] || [ ! -f "requirements.txt" ]; then
        print_message "error" "This script must be run from the root of the AI-Data-Security project."
        exit 1
    fi
}

# Function to execute Docker commands with or without sudo based on group membership
execute_docker() {
    if groups "$USER" | grep &>/dev/null '\bdocker\b'; then
        docker "$@"
    else
        sudo docker "$@"
    fi
}

# Step 0: Verify Script is Run from Project Root
check_project_root

# Step 1: System Update
print_message "info" "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_message "success" "System packages updated successfully."

# Step 2: Install Docker using Official Installation Script
if ! command -v docker &> /dev/null; then
    print_message "info" "Docker not found. Installing Docker using the official script..."

    # Install prerequisites
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Set up the stable repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Update package index
    sudo apt update

    # Install Docker Engine, CLI, and Containerd
    sudo apt install -y docker-ce docker-ce-cli containerd.io

    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker

    # Create the docker group if it doesn't exist
    sudo groupadd docker || echo "Docker group already exists."

    # Add current user to the docker group to run Docker without sudo
    sudo usermod -aG docker "$USER"

    print_message "success" "Docker installed successfully."
    print_message "info" "Added '$USER' to the 'docker' group."
    print_message "info" "To apply Docker group changes, please log out and log back in."

    # Inform the user that Docker group changes won't apply immediately
    print_message "warning" "Docker group changes will not apply to the current session. Docker commands will use 'sudo' until you log out and back in."
fi

# Step 3: Install Python 3.10, venv, and dev packages
print_message "info" "Installing Python 3.10 and related packages..."

# Add Deadsnakes PPA for Python 3.10 (if not already added)
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.10, venv, and dev packages
sudo apt install -y python3.10 python3.10-venv python3.10-dev
print_message "success" "Python 3.10 and related packages installed successfully."

# Step 4: Install SQLite
if ! command -v sqlite3 &> /dev/null; then
    print_message "info" "SQLite3 not found. Installing SQLite3..."
    sudo apt install -y sqlite3
    print_message "success" "SQLite3 installed successfully."
else
    print_message "info" "SQLite3 is already installed. Skipping SQLite installation."
fi

# Step 5: Set Up Virtual Environment with Python 3.10
print_message "info" "Setting up Python virtual environment with Python 3.10..."

# Check if virtual environment already exists
if [ -d "py_venv" ]; then
    print_message "info" "Virtual environment already exists. Activating..."
    source py_venv/bin/activate
    print_message "success" "Virtual environment activated."
else
    print_message "info" "Creating virtual environment with Python 3.10..."
    python3.10 -m venv py_venv
    source py_venv/bin/activate
    print_message "success" "Virtual environment created and activated successfully."
fi

# Step 6: Upgrade pip, setuptools, and install wheel within the virtual environment
print_message "info" "Upgrading pip, setuptools, and installing wheel..."
pip install --upgrade pip setuptools wheel
print_message "success" "pip, setuptools, and wheel upgraded successfully."

# Step 7: Install pyyaml for YAML processing
print_message "info" "Installing pyyaml for YAML processing..."
pip install pyyaml
print_message "success" "pyyaml installed successfully."

# Step 8: Downgrade pip Temporarily to Install textract==1.6.5
print_message "warning" "Downgrading pip to version <24.0 to install textract==1.6.5..."
pip install --upgrade "pip<24.0"
print_message "success" "pip downgraded to $(pip --version)"

# Step 9: Install textract==1.6.5
print_message "info" "Installing textract==1.6.5..."
pip install textract==1.6.5
print_message "success" "textract==1.6.5 installed successfully."

# Step 10: Create Input, Output, and Log Directories as per config.yaml
print_message "info" "Creating input, output, and log directories as per config.yaml..."

# Extract folder paths and Qdrant settings from config.yaml using Python
read input_folder output_folder log_folder qdrant_host qdrant_port < <(python3.10 -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print(
        config.get('input_folder', 'input_docs'),
        config.get('output_folder', 'output_docs'),
        config.get('log_folder', 'logs'),
        config.get('qdrant_host', '127.0.0.1'),
        config.get('qdrant_port', 6333)
    )
")

# Export Qdrant settings as environment variables
export QDRANT_HOST="$qdrant_host"
export QDRANT_PORT="$qdrant_port"

# Create directories if they don't exist
mkdir -p "$input_folder" "$output_folder" "$log_folder"
print_message "success" "Directories created successfully."

# Step 11: Install Remaining Python Dependencies
if [ -f "requirements.txt" ]; then
    print_message "info" "Installing remaining Python dependencies from requirements.txt..."
    # Remove textract from requirements.txt to prevent reinstallation
    grep -v "^textract==" requirements.txt > temp_requirements.txt
    mv temp_requirements.txt requirements.txt
    pip install -r requirements.txt
    print_message "success" "Remaining Python dependencies installed successfully."
else
    print_message "error" "requirements.txt not found. Please ensure it exists in the project root."
    exit 1
fi

# Step 12: Re-Upgrade pip to Latest Version
print_message "info" "Re-upgrading pip to the latest version..."
pip install --upgrade pip
print_message "success" "pip upgraded to $(pip --version)"

# Step 13: Set Up Qdrant Using Docker Run (Instead of Docker Compose)
print_message "info" "Setting up Qdrant using Docker..."

# Check if Docker is running
if ! systemctl is-active --quiet docker; then
    print_message "info" "Docker is not running. Starting Docker..."
    sudo systemctl start docker
fi

# Check if Qdrant container already exists
if [ "$(execute_docker ps -aq -f name=qdrant)" ]; then
    print_message "info" "Qdrant container already exists. Starting it..."
    execute_docker start qdrant
    print_message "success" "Qdrant container started successfully."
else
    # Run Qdrant container with user-specified host and port
    print_message "info" "Starting Qdrant Docker container..."
    execute_docker run -d --name qdrant \
        -p "$qdrant_port":6333 \
        -v "$(pwd)/$output_folder:/qdrant/storage" \
        qdrant/qdrant
    print_message "success" "Qdrant Docker container started successfully on port $qdrant_port."
fi

# Step 14: Initialize Logging
print_message "info" "Setting up logging..."
LOG_DIR="$log_folder"
LOG_FILE="$LOG_DIR/document_loader.log"
touch "$LOG_FILE"
print_message "success" "Logging setup complete. Logs will be stored in $LOG_FILE."

# Step 15: Configure Streamlit for External Access
print_message "info" "Configuring Streamlit for external access..."

# Create Streamlit config directory if it doesn't exist
mkdir -p ~/.streamlit

# Create Streamlit config file
cat << EOF > ~/.streamlit/config.toml
[server]
headless = true
enableCORS = false
port = 8501
address = "0.0.0.0"
EOF

print_message "success" "Streamlit configured for external access."

# Step 16: Create systemd Service for Streamlit Application
print_message "info" "Creating systemd service for Streamlit application..."

SERVICE_FILE="/etc/systemd/system/streamlit_app.service"

sudo bash -c "cat << EOF > $SERVICE_FILE
[Unit]
Description=Streamlit Application
After=network.target

[Service]
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$(pwd)
Environment=\"PATH=$(pwd)/py_venv/bin:\$PATH\"
ExecStart=$(pwd)/py_venv/bin/streamlit run app.py

[Install]
WantedBy=multi-user.target
EOF"

print_message "success" "systemd service file created at $SERVICE_FILE."

# Step 17: Reload systemd, Enable and Start Streamlit Service
print_message "info" "Reloading systemd daemon..."
sudo systemctl daemon-reload

print_message "info" "Enabling Streamlit service to start on boot..."
sudo systemctl enable streamlit_app.service

print_message "info" "Starting Streamlit service..."
sudo systemctl start streamlit_app.service

print_message "success" "Streamlit service started successfully."

# Step 18: Configure Firewall (UFW) to Allow Qdrant and Streamlit Ports
print_message "info" "Configuring firewall to allow Qdrant and Streamlit ports..."

# Check if UFW is installed
if ! command -v ufw &> /dev/null; then
    print_message "info" "UFW not found. Installing UFW..."
    sudo apt install -y ufw
    print_message "success" "UFW installed successfully."
fi

# Allow Qdrant port
print_message "info" "Allowing Qdrant port $qdrant_port through the firewall..."
execute_docker ps &> /dev/null || sudo ufw allow "$qdrant_port"/tcp
print_message "success" "Allowed port $qdrant_port for Qdrant."

# Allow Streamlit port
streamlit_port=8501
print_message "info" "Allowing Streamlit port $streamlit_port through the firewall..."
sudo ufw allow "$streamlit_port"/tcp
print_message "success" "Allowed port $streamlit_port for Streamlit."

# Enable UFW if not already enabled
status=$(sudo ufw status | grep -i "Status: active")
if [ -z "$status" ]; then
    print_message "info" "Enabling UFW..."
    sudo ufw --force enable
    print_message "success" "UFW enabled successfully."
else
    print_message "info" "UFW is already enabled. Skipping enabling."
fi

# Step 19: Ensure Docker Starts on Boot
print_message "info" "Ensuring Docker service is enabled to start on boot..."
sudo systemctl enable docker
print_message "success" "Docker service enabled to start on boot."

# Step 20: Provide Instructions for Viewing Logs
print_message "info" "To view the Streamlit service logs, use the following command:"
echo "sudo journalctl -u streamlit_app.service -f"

print_message "info" "To view the Qdrant container logs, use the following command:"
if groups "$USER" | grep &>/dev/null '\bdocker\b'; then
    echo "docker logs -f qdrant"
else
    echo "sudo docker logs -f qdrant"
fi

print_message "info" "Installation and configuration completed successfully."
print_message "info" "You can access the Streamlit application at http://<server_ip>:8501/"
print_message "info" "You can access Qdrant at http://<server_ip>:$qdrant_port/health"

# Final Reminder to Log Out and Log In
print_message "warning" "To run Docker commands without 'sudo' in future sessions, please log out and log back in."
