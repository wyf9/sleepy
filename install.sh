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

# Initialize data file
initialize_data() {
    print_step "4" "Initializing data file"

    if [ -f "data.json" ]; then
        print_warning "A data.json file already exists."
        read -p "Do you want to overwrite it? (y/n): " choice
        if [[ ! "$choice" =~ ^[Yy]$ ]]; then
            print_message "Keeping existing data.json file." "$YELLOW"
            return
        fi
    fi

    print_message "Creating data.json file..." "$BLUE"
    cp data.template.json data.json

    print_success "data.json file created successfully"
}

# Display completion message
display_completion() {
    print_step "5" "Installation complete"

    print_success "Sleepy has been successfully installed!"
    echo
    echo -e "${BOLD}To start the server:${NC}"
    echo "  python3 server.py"
    echo
    echo -e "${BOLD}For automatic restart on crash:${NC}"
    echo "  python3 start.py"
    echo
    echo -e "${BOLD}To update your status:${NC}"
    echo "  Use one of the client scripts in the client/ directory"
    echo
    echo -e "${BOLD}For more information, visit:${NC}"
    echo "  https://github.com/wyf9/sleepy"
    echo
    print_message "Enjoy using Sleepy!" "$GREEN"
}

# Main installation process
main() {
    clear
    echo -e "${BOLD}${BLUE}======================================${NC}"
    echo -e "${BOLD}${BLUE}       Sleepy Installation Script     ${NC}"
    echo -e "${BOLD}${BLUE}======================================${NC}"
    echo

    # Check if we're in the right directory
    if [ ! -f "server.py" ] || [ ! -f "requirements.txt" ]; then
        print_error "This script must be run from the Sleepy project root directory."
        exit 1
    fi

    # Check root privileges
    check_root

    # Step 1: Check and install Python if needed
    print_step "1" "Checking and installing system requirements"
    install_python

    # Step 2: Install dependencies
    install_dependencies

    # Step 3: Create .env file
    create_env_file

    # Step 4: Initialize data file
    initialize_data

    # Step 5: Display completion message
    display_completion
}

# Run the main function
main
