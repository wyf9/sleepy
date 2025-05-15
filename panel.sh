#!/bin/bash
# Sleepy Management Panel
# This script provides a simple interface to manage the Sleepy service

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
BG_BLUE="\033[44m"
BG_GREEN="\033[42m"
NC="\033[0m" # No Color

# Get terminal size
TERM_COLS=$(tput cols)
TERM_ROWS=$(tput lines)

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
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

# Check if systemd is available
check_systemd() {
    if ! command -v systemctl &>/dev/null; then
        print_error "systemd is not available on this system."
        print_message "This script requires systemd to manage the Sleepy service." "$YELLOW"
        exit 1
    fi
}

# Check if the service is installed
check_service() {
    if ! systemctl list-unit-files | grep -q sleepy.service; then
        print_error "Sleepy service is not installed."
        print_message "Run the install.sh script to set up the service first." "$YELLOW"
        exit 1
    fi
}

# Start the service
start_service() {
    print_message "Starting Sleepy service..." "$BLUE"
    sudo systemctl start sleepy.service
    if [ $? -eq 0 ]; then
        print_success "Sleepy service started successfully"
    else
        print_error "Failed to start Sleepy service"
    fi
}

# Stop the service
stop_service() {
    print_message "Stopping Sleepy service..." "$BLUE"
    sudo systemctl stop sleepy.service
    if [ $? -eq 0 ]; then
        print_success "Sleepy service stopped successfully"
    else
        print_error "Failed to stop Sleepy service"
    fi
}

# Restart the service
restart_service() {
    print_message "Restarting Sleepy service..." "$BLUE"
    sudo systemctl restart sleepy.service
    if [ $? -eq 0 ]; then
        print_success "Sleepy service restarted successfully"
    else
        print_error "Failed to restart Sleepy service"
    fi
}

# Check service status
status_service() {
    echo -e "${BOLD}${BLUE}Sleepy Service Status:${NC}"
    echo
    systemctl status sleepy.service
}

# Enable service to start on boot
enable_service() {
    print_message "Enabling Sleepy service to start on boot..." "$BLUE"
    sudo systemctl enable sleepy.service
    if [ $? -eq 0 ]; then
        print_success "Sleepy service enabled successfully"
    else
        print_error "Failed to enable Sleepy service"
    fi
}

# Disable service from starting on boot
disable_service() {
    print_message "Disabling Sleepy service from starting on boot..." "$BLUE"
    sudo systemctl disable sleepy.service
    if [ $? -eq 0 ]; then
        print_success "Sleepy service disabled successfully"
    else
        print_error "Failed to disable Sleepy service"
    fi
}

# View logs
view_logs() {
    echo -e "${BOLD}${BLUE}Sleepy Service Logs:${NC}"
    echo
    sudo journalctl -u sleepy.service --no-pager | tail -n 50
    echo
    print_message "To see more logs, run: sudo journalctl -u sleepy.service" "$BLUE"
}

# View real-time logs
view_realtime_logs() {
    clear
    echo -e "${BOLD}${BLUE}Sleepy Service Real-time Logs${NC}"
    echo -e "${YELLOW}Press Ctrl+C to exit${NC}"
    echo
    sudo journalctl -u sleepy.service -f
}

# View configuration file
view_config() {
    clear
    echo -e "${BOLD}${BLUE}Sleepy Configuration File (.env):${NC}"
    echo

    ENV_FILE=$(find_env_file)
    if [ $? -eq 0 ]; then
        echo -e "${BOLD}Configuration file:${NC} $ENV_FILE"
        echo
        cat "$ENV_FILE"
    else
        print_error "Could not find .env file"
    fi
}

# View secret key
view_secret() {
    clear
    echo -e "${BOLD}${BLUE}Sleepy Secret Key:${NC}"
    echo

    ENV_FILE=$(find_env_file)
    if [ $? -eq 0 ]; then
        SECRET=$(grep "SLEEPY_SECRET" "$ENV_FILE" | cut -d '"' -f 2)
        if [ -n "$SECRET" ]; then
            echo -e "${BOLD}Secret key:${NC} $SECRET"
            echo
            print_message "Keep this key secure! It is used for authentication." "$YELLOW"
        else
            print_error "Secret key not found in $ENV_FILE"
        fi
    else
        print_error "Could not find .env file"
    fi
}

# View service information
view_service_info() {
    clear
    echo -e "${BOLD}${BLUE}Sleepy Service Information:${NC}"
    echo

    # Get service file path
    SERVICE_FILE="/etc/systemd/system/sleepy.service"
    if [ -f "$SERVICE_FILE" ]; then
        echo -e "${BOLD}Service file:${NC} $SERVICE_FILE"
        echo
        cat "$SERVICE_FILE"
    else
        print_error "Service file not found at $SERVICE_FILE"
    fi
}

# Find the .env file
find_env_file() {
    # Get the service directory from systemd
    SERVICE_DIR=$(systemctl show -p FragmentPath sleepy.service | grep -o '/.*/' | head -1)

    # If we couldn't get it from systemd, use current directory
    if [ -z "$SERVICE_DIR" ]; then
        SERVICE_DIR=$(pwd)
    fi

    # Check if .env file exists
    ENV_FILE="${SERVICE_DIR}/.env"
    if [ -f "$ENV_FILE" ]; then
        echo "$ENV_FILE"
        return 0
    else
        # Try to find .env file in common locations
        FOUND_ENV=$(find /home -name ".env" -type f -path "*/sleepy/*" 2>/dev/null | head -1)

        if [ -n "$FOUND_ENV" ]; then
            echo "$FOUND_ENV"
            return 0
        else
            return 1
        fi
    fi
}

# List all configuration items
config_list() {
    clear
    echo -e "${BOLD}${BLUE}Sleepy Configuration Items:${NC}"
    echo

    ENV_FILE=$(find_env_file)
    if [ $? -eq 0 ]; then
        echo -e "${BOLD}Configuration file:${NC} $ENV_FILE"
        echo

        # Extract and format configuration items
        echo -e "${BOLD}${CYAN}Current Configuration:${NC}"
        echo

        # Read the .env file line by line
        while IFS= read -r line || [ -n "$line" ]; do
            # Skip empty lines and comments
            if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
                continue
            fi

            # Extract key and value
            if [[ "$line" =~ ^([A-Za-z0-9_]+)[[:space:]]*=[[:space:]]*\"(.*)\" ]]; then
                KEY="${BASH_REMATCH[1]}"
                VALUE="${BASH_REMATCH[2]}"

                # Format the output
                echo -e "${BOLD}${KEY}${NC} = \"${VALUE}\""
            elif [[ "$line" =~ ^([A-Za-z0-9_]+)[[:space:]]*=[[:space:]]*([^\"]*) ]]; then
                KEY="${BASH_REMATCH[1]}"
                VALUE="${BASH_REMATCH[2]}"

                # Format the output
                echo -e "${BOLD}${KEY}${NC} = ${VALUE}"
            fi
        done < "$ENV_FILE"
    else
        print_error "Could not find .env file"
        return 1
    fi
}

# Set a configuration item
config_set() {
    local key="$1"
    local value="$2"

    if [ -z "$key" ] || [ -z "$value" ]; then
        print_error "Both key and value must be provided"
        echo "Usage: sleepy config-set KEY VALUE"
        return 1
    fi

    ENV_FILE=$(find_env_file)
    if [ $? -eq 0 ]; then
        echo -e "${BOLD}Configuration file:${NC} $ENV_FILE"

        # Check if the key exists
        if grep -q "^${key}" "$ENV_FILE"; then
            # Determine if the value should be quoted
            if grep -q "^${key}.*=\"" "$ENV_FILE"; then
                # Update with quotes
                sed -i "s/^${key}[[:space:]]*=[[:space:]]*\".*\"/${key} = \"${value}\"/" "$ENV_FILE"
            else
                # Update without quotes
                sed -i "s/^${key}[[:space:]]*=[[:space:]]*.*/${key} = ${value}/" "$ENV_FILE"
            fi

            print_success "Updated configuration: ${key} = ${value}"
        else
            print_warning "Key '${key}' not found in configuration file"
            read -p "Do you want to add this key-value pair? (y/n): " choice
            if [[ "$choice" =~ ^[Yy]$ ]]; then
                # Add new key-value pair (with quotes by default)
                echo "${key} = \"${value}\"" >> "$ENV_FILE"
                print_success "Added new configuration: ${key} = \"${value}\""
            else
                print_message "Configuration not updated." "$YELLOW"
            fi
        fi

        # Ask if user wants to restart the service
        read -p "Do you want to restart the service to apply changes? (y/n): " choice
        if [[ "$choice" =~ ^[Yy]$ ]]; then
            restart_service
        else
            print_warning "Changes will take effect after service restart"
        fi
    else
        print_error "Could not find .env file"
        return 1
    fi
}

# Interactive config set
interactive_config_set() {
    clear
    echo -e "${BOLD}${BLUE}Set Configuration Value:${NC}"
    echo

    # First list current configuration
    ENV_FILE=$(find_env_file)
    if [ $? -eq 0 ]; then
        echo -e "${BOLD}Configuration file:${NC} $ENV_FILE"
        echo

        # Show current configuration
        echo -e "${BOLD}${CYAN}Current Configuration:${NC}"
        echo

        # Create an array to store keys
        declare -a CONFIG_KEYS

        # Read the .env file line by line
        local i=0
        while IFS= read -r line || [ -n "$line" ]; do
            # Skip empty lines and comments
            if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
                continue
            fi

            # Extract key and value
            if [[ "$line" =~ ^([A-Za-z0-9_]+)[[:space:]]*=[[:space:]]*\"(.*)\" ]]; then
                KEY="${BASH_REMATCH[1]}"
                VALUE="${BASH_REMATCH[2]}"

                # Store key in array
                CONFIG_KEYS[$i]="$KEY"
                i=$((i+1))

                # Format the output
                echo -e "${BOLD}$i)${NC} ${BOLD}${KEY}${NC} = \"${VALUE}\""
            elif [[ "$line" =~ ^([A-Za-z0-9_]+)[[:space:]]*=[[:space:]]*([^\"]*) ]]; then
                KEY="${BASH_REMATCH[1]}"
                VALUE="${BASH_REMATCH[2]}"

                # Store key in array
                CONFIG_KEYS[$i]="$KEY"
                i=$((i+1))

                # Format the output
                echo -e "${BOLD}$i)${NC} ${BOLD}${KEY}${NC} = ${VALUE}"
            fi
        done < "$ENV_FILE"

        echo
        echo -e "${BOLD}${YELLOW}Enter 'n' to add a new configuration item${NC}"
        echo

        # Ask which key to modify
        read -p "Enter the number of the item to modify (or 'n' for new, 'q' to quit): " choice

        if [[ "$choice" == "q" ]]; then
            return 0
        elif [[ "$choice" == "n" ]]; then
            # Add new configuration
            read -p "Enter new configuration key: " new_key
            read -p "Enter value for $new_key: " new_value

            if [ -z "$new_key" ] || [ -z "$new_value" ]; then
                print_error "Both key and value must be provided"
                read -p "Press Enter to continue..."
                return 1
            fi

            # Add new key-value pair (with quotes by default)
            echo "${new_key} = \"${new_value}\"" >> "$ENV_FILE"
            print_success "Added new configuration: ${new_key} = \"${new_value}\""
        elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#CONFIG_KEYS[@]} ]; then
            # Modify existing configuration
            key_index=$((choice-1))
            selected_key="${CONFIG_KEYS[$key_index]}"

            # Get current value
            current_value=$(grep "^${selected_key}" "$ENV_FILE" | sed -E "s/^${selected_key}[[:space:]]*=[[:space:]]*\"?([^\"]*)\"?/\1/")

            read -p "Enter new value for $selected_key [$current_value]: " new_value

            # If no input, keep current value
            if [ -z "$new_value" ]; then
                new_value="$current_value"
            fi

            # Determine if the value should be quoted
            if grep -q "^${selected_key}.*=\"" "$ENV_FILE"; then
                # Update with quotes
                sed -i "s/^${selected_key}[[:space:]]*=[[:space:]]*\".*\"/${selected_key} = \"${new_value}\"/" "$ENV_FILE"
            else
                # Update without quotes
                sed -i "s/^${selected_key}[[:space:]]*=[[:space:]]*.*/${selected_key} = ${new_value}/" "$ENV_FILE"
            fi

            print_success "Updated configuration: ${selected_key} = ${new_value}"
        else
            print_error "Invalid choice"
            read -p "Press Enter to continue..."
            return 1
        fi

        # Ask if user wants to restart the service
        read -p "Do you want to restart the service to apply changes? (y/n): " choice
        if [[ "$choice" =~ ^[Yy]$ ]]; then
            restart_service
        else
            print_warning "Changes will take effect after service restart"
        fi
    else
        print_error "Could not find .env file"
        read -p "Press Enter to continue..."
        return 1
    fi
}

# Show help
show_help() {
    echo -e "${BOLD}${BLUE}Sleepy Management Panel${NC}"
    echo
    echo -e "${BOLD}Usage:${NC}"
    echo "  sleepy [command]"
    echo
    echo -e "${BOLD}Commands:${NC}"
    echo "  start      Start the Sleepy service"
    echo "  stop       Stop the Sleepy service"
    echo "  restart    Restart the Sleepy service"
    echo "  status     Check the status of the Sleepy service"
    echo "  enable     Enable Sleepy to start on boot"
    echo "  disable    Disable Sleepy from starting on boot"
    echo "  logs       View the service logs"
    echo "  follow     View real-time logs (follow mode)"
    echo "  config     View the configuration file (.env)"
    echo "  config-list List all configuration items"
    echo "  config-set  Set a configuration value (config-set KEY VALUE)"
    echo "  secret     View the secret key"
    echo "  info       View service information"
    echo "  help       Show this help message"
    echo
    echo -e "${BOLD}Interactive Mode:${NC}"
    echo "  Run 'sleepy' without any arguments to launch the interactive menu"
    echo
}

# Draw a centered header
draw_header() {
    local header_text="$1"
    local padding=$(( (TERM_COLS - ${#header_text}) / 2 ))

    echo
    printf "%${TERM_COLS}s" | tr ' ' '='
    echo -e "\n"
    printf "%${padding}s${BOLD}${BLUE}%s${NC}%${padding}s\n" "" "$header_text" ""
    echo
    printf "%${TERM_COLS}s" | tr ' ' '='
    echo
}

# Draw a menu item
draw_menu_item() {
    local number="$1"
    local text="$2"
    local description="$3"

    echo -e "  ${CYAN}$number${NC}) ${BOLD}$text${NC}"
    if [ ! -z "$description" ]; then
        echo -e "     $description"
    fi
    echo
}

# Get service status for display
get_service_status_display() {
    if systemctl is-active --quiet sleepy.service; then
        echo -e "${GREEN}● Active${NC}"
    else
        echo -e "${RED}○ Inactive${NC}"
    fi
}

# Get service enabled status for display
get_service_enabled_display() {
    if systemctl is-enabled --quiet sleepy.service 2>/dev/null; then
        echo -e "${GREEN}● Enabled${NC}"
    else
        echo -e "${YELLOW}○ Disabled${NC}"
    fi
}

# Show interactive menu
show_interactive_menu() {
    clear

    # Header
    draw_header "Sleepy Management Panel"

    # Get current directory
    CURRENT_DIR=$(pwd)

    # Status summary
    echo -e "${BOLD}Service Status:${NC} $(get_service_status_display)"
    echo -e "${BOLD}Autostart:${NC} $(get_service_enabled_display)"
    echo -e "${BOLD}Installation Path:${NC} ${CURRENT_DIR}"
    echo

    # Menu options
    echo -e "${BOLD}${MAGENTA}Service Control:${NC}"
    draw_menu_item "1" "Start Service" "Start the Sleepy service"
    draw_menu_item "2" "Stop Service" "Stop the Sleepy service"
    draw_menu_item "3" "Restart Service" "Restart the Sleepy service"

    echo -e "${BOLD}${MAGENTA}Service Configuration:${NC}"
    draw_menu_item "4" "Enable Autostart" "Enable Sleepy to start on boot"
    draw_menu_item "5" "Disable Autostart" "Disable Sleepy from starting on boot"

    echo -e "${BOLD}${MAGENTA}Monitoring:${NC}"
    draw_menu_item "6" "View Status" "Check detailed status of the Sleepy service"
    draw_menu_item "7" "View Logs" "View the service logs"
    draw_menu_item "8" "Real-time Logs" "View logs in real-time (follow mode)"

    echo -e "${BOLD}${MAGENTA}Configuration:${NC}"
    draw_menu_item "9" "View Config" "View the configuration file (.env)"
    draw_menu_item "c" "List Config" "List all configuration items"
    draw_menu_item "e" "Edit Config" "Edit configuration values"
    draw_menu_item "0" "View Secret" "View the secret key"
    draw_menu_item "i" "Service Info" "View service information"

    echo -e "${BOLD}${MAGENTA}Other:${NC}"
    draw_menu_item "q" "Quit" "Exit the management panel"

    echo
    read -p "Enter your choice: " choice

    case $choice in
        1)
            clear
            check_service
            start_service
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        2)
            clear
            check_service
            stop_service
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        3)
            clear
            check_service
            restart_service
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        4)
            clear
            check_service
            enable_service
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        5)
            clear
            check_service
            disable_service
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        6)
            clear
            check_service
            status_service
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        7)
            clear
            check_service
            view_logs
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        8)
            clear
            check_service
            view_realtime_logs
            # After user presses Ctrl+C to exit real-time logs
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        9)
            clear
            check_service
            view_config
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        c|C)
            clear
            check_service
            config_list
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        e|E)
            clear
            check_service
            interactive_config_set
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        0)
            clear
            check_service
            view_secret
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        i|I)
            clear
            check_service
            view_service_info
            echo
            read -p "Press Enter to continue..."
            show_interactive_menu
            ;;
        q|Q)
            clear
            echo -e "${BOLD}${GREEN}Thank you for using Sleepy Management Panel!${NC}"
            exit 0
            ;;
        *)
            clear
            print_error "Invalid option: $choice"
            sleep 2
            show_interactive_menu
            ;;
    esac
}

# Main function
main() {
    # Check if systemd is available
    check_systemd

    # If no arguments provided, show interactive menu
    if [ -z "$1" ]; then
        check_service
        show_interactive_menu
        return
    fi

    # Process command line arguments
    case "$1" in
        start)
            check_service
            start_service
            ;;
        stop)
            check_service
            stop_service
            ;;
        restart)
            check_service
            restart_service
            ;;
        status)
            check_service
            status_service
            ;;
        enable)
            check_service
            enable_service
            ;;
        disable)
            check_service
            disable_service
            ;;
        logs)
            check_service
            view_logs
            ;;
        follow)
            check_service
            view_realtime_logs
            ;;
        config)
            check_service
            view_config
            ;;
        config-list)
            check_service
            config_list
            ;;
        config-set)
            check_service
            if [ -z "$2" ] || [ -z "$3" ]; then
                print_error "Both key and value must be provided"
                echo "Usage: sleepy config-set KEY VALUE"
                exit 1
            fi
            config_set "$2" "$3"
            ;;
        secret)
            check_service
            view_secret
            ;;
        info)
            check_service
            view_service_info
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run the main function with all arguments
main "$@"
