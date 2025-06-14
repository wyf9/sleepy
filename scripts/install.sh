#!/bin/bash
# Sleepy Project Installation Script
# This script helps you set up the Sleepy project on Unix-like systems

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

print_step() {
    echo -e "\n${BOLD}${BLUE}[Step $1]${NC} ${BOLD}$2${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if script is run with root privileges
check_root() {
    if [ "$(id -u)" -eq 0 ]; then
        print_warning "You are running this script as root. It's recommended to install Python packages as a regular user."
        read -p "Continue as root? (y/n): " choice
        if [[ ! "$choice" =~ ^[Yy]$ ]]; then
            print_message "Installation aborted." "$RED"
            exit 1
        fi
    fi
}

# Install Python 3 if not present
install_python() {
    if command -v python3 &>/dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Found Python $python_version"

        # Check if Python version is at least 3.6
        if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1)"; then
            print_success "Python version is compatible (3.6+)"
            return 0
        else
            print_warning "Python version is too old. Sleepy requires Python 3.6 or newer."
            print_message "Will attempt to install a newer version..." "$BLUE"
        fi
    else
        print_warning "Python 3 is not installed."
        print_message "Will attempt to install Python 3..." "$BLUE"
    fi

    # Detect OS
    OS=$(detect_os)

    # Install Python based on OS
    case $OS in
        ubuntu|debian|linuxmint|pop)
            print_message "Detected Debian/Ubuntu-based system" "$BLUE"
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        fedora|centos|rhel)
            print_message "Detected Red Hat-based system" "$BLUE"
            sudo dnf install -y python3 python3-pip
            ;;
        arch|manjaro)
            print_message "Detected Arch-based system" "$BLUE"
            sudo pacman -Sy python python-pip
            ;;
        darwin)
            print_message "Detected macOS" "$BLUE"
            if command -v brew &>/dev/null; then
                brew install python3
            else
                print_message "Installing Homebrew first..." "$BLUE"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                brew install python3
            fi
            ;;
        *)
            print_error "Unsupported operating system: $OS"
            print_message "Please install Python 3.6+ manually and run this script again." "$YELLOW"
            exit 1
            ;;
    esac

    # Verify installation
    if command -v python3 &>/dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Successfully installed Python $python_version"

        # Make sure pip is available
        if ! command -v pip3 &>/dev/null; then
            print_warning "pip3 not found, attempting to install..."
            case $OS in
                ubuntu|debian|linuxmint|pop)
                    sudo apt-get install -y python3-pip
                    ;;
                fedora|centos|rhel)
                    sudo dnf install -y python3-pip
                    ;;
                arch|manjaro)
                    sudo pacman -Sy python-pip
                    ;;
            esac
        fi
    else
        print_error "Failed to install Python 3"
        print_message "Please install Python 3.6+ manually and run this script again." "$YELLOW"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_step "2" "Installing dependencies"

    # Check if pip is installed
    if ! command -v pip3 &>/dev/null; then
        print_error "pip3 is not installed. Please install pip for Python 3."
        exit 1
    fi

    # Install dependencies
    print_message "Installing required packages..." "$BLUE"

    # Determine if we should use --break-system-packages flag (for Python 3.11+)
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" &>/dev/null; then
        pip3 install -r requirements.txt --break-system-packages
    else
        pip3 install -r requirements.txt
    fi

    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Create .env file
create_env_file() {
    print_step "3" "Setting up configuration"

    if [ -f ".env" ]; then
        print_warning "A .env file already exists."
        read -p "Do you want to overwrite it? (y/n): " choice
        if [[ ! "$choice" =~ ^[Yy]$ ]]; then
            print_message "Keeping existing .env file." "$YELLOW"
            return
        fi
    fi

    print_message "Creating .env file..." "$BLUE"
    cp .env.example .env

    # Generate a random secret
    secret=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    sed -i "s/SLEEPY_SECRET = \"\"/SLEEPY_SECRET = \"$secret\"/" .env

    # Ask for user name
    read -p "Enter your name (default: User): " username
    username=${username:-User}
    sed -i "s/sleepy_page_user = \"User\"/sleepy_page_user = \"$username\"/" .env

    # Update page title
    sed -i "s/sleepy_page_title = \"User Alive?\"/sleepy_page_title = \"$username Alive?\"/" .env

    # Update page description
    sed -i "s/sleepy_page_desc = \"User's Online Status Page\"/sleepy_page_desc = \"$username's Online Status Page\"/" .env

    print_success ".env file created successfully"
    print_message "You can further customize your configuration by editing the .env file." "$BLUE"
}

# Create systemd service
create_systemd_service() {
    print_step "5" "Setting up systemd service"

    # Check if systemd is available
    if ! command -v systemctl &>/dev/null; then
        print_warning "systemd is not available on this system. Skipping service creation."
        return
    fi

    # Ask if user wants to create a systemd service
    read -p "Do you want to register Sleepy as a systemd service? (y/n): " choice
    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        print_message "Skipping systemd service creation." "$YELLOW"
        return
    fi

    # Get current directory and user
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)

    # Create service file
    print_message "Creating systemd service file..." "$BLUE"

    SERVICE_FILE="[Unit]
Description=Sleepy Status Page
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${CURRENT_DIR}
ExecStart=$(which python3) ${CURRENT_DIR}/server.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"

    # Write service file
    echo "$SERVICE_FILE" | sudo tee /etc/systemd/system/sleepy.service > /dev/null

    if [ $? -eq 0 ]; then
        print_success "Service file created successfully"

        # Set Python capabilities to bind to privileged ports
        print_message "Setting Python capabilities to bind to privileged ports..." "$BLUE"
        python_path=$(which python3)
        python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
        if [ -f "/usr/bin/python$python_version" ]; then
            sudo setcap 'cap_net_bind_service=+ep' "/usr/bin/python$python_version"
            print_success "Set capabilities for /usr/bin/python$python_version"
        elif [ -n "$python_path" ]; then
            sudo setcap 'cap_net_bind_service=+ep' "$python_path"
            print_success "Set capabilities for $python_path"
        else
            print_warning "Could not find Python binary to set capabilities"
        fi

        # Configure firewall to allow HTTPS traffic
        print_message "Configuring firewall to allow HTTPS traffic..." "$BLUE"
        if command -v iptables &>/dev/null; then
            sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
            print_success "Firewall rule added for port 443"
        else
            print_warning "iptables not found, skipping firewall configuration"
        fi

        # Reload systemd
        print_message "Reloading systemd..." "$BLUE"
        sudo systemctl daemon-reload

        # Enable service
        print_message "Enabling sleepy service..." "$BLUE"
        sudo systemctl enable sleepy.service

        if [ $? -eq 0 ]; then
            print_success "Sleepy service has been enabled and will start on boot"

            # Make panel.sh executable
            chmod +x scripts/panel.sh
            print_success "Management panel script is now executable"

            # Create alias for panel.sh
            ALIAS_COMMAND="alias sleepy='${CURRENT_DIR}/scripts/panel.sh'"

            # Display the alias command for the user to use
            print_message "To use the 'sleepy' command, run the following:" "$BLUE"
            print_message "$ALIAS_COMMAND" "$YELLOW"
            echo
            print_message "You can add this line to your shell configuration file (~/.bashrc, ~/.zshrc, or ~/.profile)" "$BLUE"
            print_message "to make the alias permanent." "$BLUE"

            # Ask if user wants to start the service now
            read -p "Do you want to start the Sleepy service now? (y/n): " choice
            if [[ "$choice" =~ ^[Yy]$ ]]; then
                print_message "Starting sleepy service..." "$BLUE"
                sudo systemctl start sleepy.service

                if [ $? -eq 0 ]; then
                    print_success "Sleepy service started successfully"
                else
                    print_error "Failed to start Sleepy service"
                    print_message "You can try starting it manually with: sudo systemctl start sleepy.service" "$YELLOW"
                fi
            else
                print_message "You can start the service later with: sudo systemctl start sleepy.service" "$BLUE"
            fi
        else
            print_error "Failed to enable Sleepy service"
        fi
    else
        print_error "Failed to create service file"
    fi
}

# Display completion message
display_completion() {
    print_step "6" "Installation complete"

    print_success "Sleepy has been successfully installed!"
    echo
    echo -e "${BOLD}To start the server:${NC}"
    echo "  python3 server.py"
    echo
    echo -e "${BOLD}For automatic restart on crash:${NC}"
    echo "  python3 start.py"
    echo

    # If systemd service was created
    if systemctl list-unit-files | grep -q sleepy.service; then
        echo -e "${BOLD}To manage the Sleepy service:${NC}"
        echo "  sleepy start     # Start the service"
        echo "  sleepy stop      # Stop the service"
        echo "  sleepy restart   # Restart the service"
        echo "  sleepy status    # Check service status"
        echo "  sleepy logs      # View service logs"
        echo "  sleepy enable    # Enable autostart"
        echo "  sleepy disable   # Disable autostart"
        echo "  sleepy help      # Show all commands"
        echo
        echo -e "${BOLD}Note:${NC} Run the alias command shown above to use the 'sleepy' command"
        echo "      in the current terminal session."
        echo
    fi

    echo -e "${BOLD}To update your status:${NC}"
    echo "  Use one of the client scripts in the client/ directory"
    echo
    echo -e "${BOLD}For more information, visit:${NC}"
    echo "  https://github.com/sleepy-project/sleepy"
    echo
    # Show installation directory
    echo -e "${BOLD}Installation directory:${NC}"
    echo "  $(pwd)"
    echo
    print_message "Enjoy using Sleepy!" "$GREEN"
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
    elif [ -f /etc/debian_version ]; then
        OS=debian
    elif [ -f /etc/redhat-release ]; then
        OS=centos
    else
        OS=$(uname -s)
    fi
    echo $OS
}

# Check if git is installed and install if needed
check_git() {
    if ! command -v git &>/dev/null; then
        print_warning "Git is not installed. Installing git..."

        # Detect OS
        OS=$(detect_os)

        # Install git based on OS
        case $OS in
            ubuntu|debian|linuxmint|pop)
                sudo apt-get update
                sudo apt-get install -y git
                ;;
            fedora|centos|rhel)
                sudo dnf install -y git
                ;;
            arch|manjaro)
                sudo pacman -Sy git
                ;;
            darwin)
                if command -v brew &>/dev/null; then
                    brew install git
                else
                    print_error "Homebrew is not installed. Please install git manually."
                    exit 1
                fi
                ;;
            *)
                print_error "Unsupported operating system: $OS"
                print_message "Please install git manually and run this script again." "$YELLOW"
                exit 1
                ;;
        esac

        if ! command -v git &>/dev/null; then
            print_error "Failed to install git"
            exit 1
        else
            print_success "Git installed successfully"
        fi
    fi
}

# Clone repository
clone_repository() {
    print_step "1" "Cloning Sleepy repository"

    # Check if git is installed
    check_git

    # Ask for installation directory
    read -p "Enter installation directory (default: ~/sleepy): " install_dir
    install_dir=${install_dir:-~/sleepy}

    # Expand tilde to home directory
    install_dir="${install_dir/#\~/$HOME}"

    print_message "Installation directory: $install_dir" "$BLUE"

    # Check if directory exists
    if [ -d "$install_dir" ]; then
        print_warning "Directory $install_dir already exists."
        read -p "Do you want to use this directory anyway? (y/n): " choice
        if [[ ! "$choice" =~ ^[Yy]$ ]]; then
            print_message "Installation aborted." "$RED"
            exit 1
        fi
    else
        # Create directory
        mkdir -p "$install_dir"
        if [ $? -ne 0 ]; then
            print_error "Failed to create directory $install_dir"
            exit 1
        fi
        print_success "Created directory $install_dir"
    fi

    # Change to installation directory
    cd "$install_dir"
    if [ $? -ne 0 ]; then
        print_error "Failed to change to directory $install_dir"
        exit 1
    fi

    # Check if we're already in a git repository
    if [ -d ".git" ]; then
        print_warning "This directory is already a git repository."
        read -p "Do you want to pull the latest changes instead? (y/n): " choice
        if [[ "$choice" =~ ^[Yy]$ ]]; then
            print_message "Pulling latest changes..." "$BLUE"
            git pull
            if [ $? -eq 0 ]; then
                print_success "Repository updated successfully"
            else
                print_error "Failed to update repository"
                exit 1
            fi
            return
        else
            print_message "Continuing with existing repository..." "$YELLOW"
            return
        fi
    fi

    # Clone the repository
    print_message "Cloning Sleepy repository to $install_dir..." "$BLUE"
    git clone --depth=1 -b main https://github.com/sleepy-project/sleepy.git .

    if [ $? -eq 0 ]; then
        print_success "Repository cloned successfully"

        # Make the install.sh script executable
        chmod +x scripts/install.sh

        # Check if we need to run the script from the cloned repository
        if [ "$0" != "./scripts/install.sh" ] && [ "$0" != "scripts/install.sh" ]; then
            print_message "Running installation from the cloned repository..." "$BLUE"
            exec ./scripts/install.sh
            exit 0
        fi
    else
        print_error "Failed to clone repository"
        exit 1
    fi
}

# Check if script is being run from curl/wget
is_running_from_web() {
    # Check if the script is being piped from curl or wget
    if [ -t 0 ]; then
        # Terminal input is available, not being piped
        return 1
    else
        # No terminal input, likely being piped
        return 0
    fi
}

# Main installation process
main() {
    clear
    echo -e "${BOLD}${BLUE}======================================${NC}"
    echo -e "${BOLD}${BLUE}       Sleepy Installation Script     ${NC}"
    echo -e "${BOLD}${BLUE}======================================${NC}"
    echo

    # Check if we're running the script directly from the web (curl/wget)
    if is_running_from_web; then
        print_message "Running installation script from web..." "$BLUE"
        # We need to save the script to a temporary file and then execute it
        TEMP_SCRIPT=$(mktemp)
        cat > "$TEMP_SCRIPT"
        chmod +x "$TEMP_SCRIPT"
        exec "$TEMP_SCRIPT"
        exit 0
    fi

    # Check if we're in the Sleepy directory
    if [ ! -f "server.py" ] || [ ! -f "requirements.txt" ]; then
        print_message "Not in Sleepy project directory. Will clone the repository." "$YELLOW"
        # We're not in the Sleepy directory, need to clone the repo
        clone_repository
    else
        print_success "Running from Sleepy project directory"
    fi

    # Check root privileges
    check_root

    # Step 2: Check and install Python if needed
    print_step "2" "Checking and installing system requirements"
    install_python

    # Step 3: Install dependencies
    install_dependencies

    # Step 4: Create .env file
    create_env_file

    # Step 5: Create systemd service (optional)
    create_systemd_service

    # Step 6: Display completion message
    display_completion
}

# Run the main function
main
