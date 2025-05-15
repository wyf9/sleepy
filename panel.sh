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
