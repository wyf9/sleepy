# Sleepy Project Installation Script for Windows
# This script helps you set up the Sleepy project on Windows systems

# Function to print colored messages
function Write-ColorMessage {
    param (
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param (
        [string]$StepNumber,
        [string]$Message
    )
    Write-Host "`n[Step $StepNumber] " -ForegroundColor Blue -NoNewline
    Write-Host $Message -ForegroundColor White
}

function Write-Success {
    param (
        [string]$Message
    )
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param (
        [string]$Message
    )
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param (
        [string]$Message
    )
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Check if PowerShell is running as Administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check and install Python if needed
function Install-Python {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = (python --version) 2>&1
        if ($pythonVersion -match "Python 3\.(\d+)\.(\d+)") {
            $minorVersion = [int]$Matches[1]
            if ($minorVersion -ge 6) {
                Write-Success "Found $pythonVersion"
                Write-Success "Python version is compatible (3.6+)"
                return
            }
        }
        Write-Warning "Python version is too old. Sleepy requires Python 3.6 or newer."
    }
    else {
        Write-Warning "Python 3 is not installed."
    }
    
    Write-ColorMessage "Will attempt to install Python 3..." "Blue"
    
    # Create a temporary directory for the installer
    $tempDir = "temp_python_install"
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    
    # Download Python installer
    $pythonUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    $installerPath = Join-Path $tempDir "python_installer.exe"
    
    Write-ColorMessage "Downloading Python installer..." "Blue"
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
    }
    catch {
        Write-Error "Failed to download Python installer."
        Write-ColorMessage "Please install Python 3.6+ manually from https://www.python.org/downloads/" "Yellow"
        Remove-Item -Path $tempDir -Recurse -Force
        exit 1
    }
    
    # Run the installer
    Write-ColorMessage "Running Python installer..." "Blue"
    Write-ColorMessage "This will install Python 3.10.11 with the following options:" "Yellow"
    Write-ColorMessage "- Install for all users" "Yellow"
    Write-ColorMessage "- Add Python to PATH" "Yellow"
    Write-ColorMessage "- Install pip" "Yellow"
    
    Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
    
    # Clean up
    Remove-Item -Path $tempDir -Recurse -Force
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    # Verify installation
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = (python --version) 2>&1
        Write-Success "Successfully installed $pythonVersion"
        
        # Make sure pip is available
        if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
            Write-Warning "pip not found, attempting to install..."
            python -m ensurepip --upgrade
        }
    }
    else {
        Write-Error "Failed to install Python 3"
        Write-ColorMessage "Please install Python 3.6+ manually and run this script again." "Yellow"
        exit 1
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Step "2" "Installing dependencies"
    
    # Check if pip is installed
    if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
        Write-Error "pip is not installed. Please install pip for Python 3."
        exit 1
    }
    
    # Install dependencies
    Write-ColorMessage "Installing required packages..." "Blue"
    
    try {
        python -m pip install -r requirements.txt
        Write-Success "Dependencies installed successfully"
    }
    catch {
        Write-Error "Failed to install dependencies"
        exit 1
    }
}

# Create .env file
function Create-EnvFile {
    Write-Step "3" "Setting up configuration"
    
    if (Test-Path ".env") {
        Write-Warning "A .env file already exists."
        $choice = Read-Host "Do you want to overwrite it? (y/n)"
        if ($choice -ne "y") {
            Write-ColorMessage "Keeping existing .env file." "Yellow"
            return
        }
    }
    
    Write-ColorMessage "Creating .env file..." "Blue"
    Copy-Item ".env.example" ".env"
    
    # Generate a random secret
    $secret = -join ((48..57) + (97..122) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
    (Get-Content ".env") -replace 'SLEEPY_SECRET = ""', "SLEEPY_SECRET = `"$secret`"" | Set-Content ".env"
    
    # Ask for user name
    $username = Read-Host "Enter your name (default: User)"
    if ([string]::IsNullOrEmpty($username)) {
        $username = "User"
    }
    
    (Get-Content ".env") -replace 'sleepy_page_user = "User"', "sleepy_page_user = `"$username`"" | Set-Content ".env"
    
    # Update page title
    (Get-Content ".env") -replace 'sleepy_page_title = "User Alive\?"', "sleepy_page_title = `"$username Alive?`"" | Set-Content ".env"
    
    # Update page description
    (Get-Content ".env") -replace 'sleepy_page_desc = "User''s Online Status Page"', "sleepy_page_desc = `"$username's Online Status Page`"" | Set-Content ".env"
    
    Write-Success ".env file created successfully"
    Write-ColorMessage "You can further customize your configuration by editing the .env file." "Blue"
}

# Display completion message
function Show-CompletionMessage {
    Write-Step "5" "Installation complete"
    
    Write-Success "Sleepy has been successfully installed!"
    Write-Host ""
    Write-Host "To start the server:" -ForegroundColor White
    Write-Host "  python server.py"
    Write-Host ""
    Write-Host "For automatic restart on crash:" -ForegroundColor White
    Write-Host "  python start.py"
    Write-Host ""
    Write-Host "To update your status:" -ForegroundColor White
    Write-Host "  Use one of the client scripts in the client/ directory"
    Write-Host ""
    Write-Host "For more information, visit:" -ForegroundColor White
    Write-Host "  https://github.com/sleepy-project/sleepy"
    Write-Host ""
    Write-ColorMessage "Enjoy using Sleepy!" "Green"
}

# Main installation process
function Start-Installation {
    Clear-Host
    Write-Host "======================================" -ForegroundColor Blue
    Write-Host "       Sleepy Installation Script     " -ForegroundColor Blue
    Write-Host "======================================" -ForegroundColor Blue
    Write-Host ""
    
    # Check if we're in the right directory
    if (-not (Test-Path "server.py") -or -not (Test-Path "requirements.txt")) {
        Write-Error "This script must be run from the Sleepy project root directory."
        exit 1
    }
    
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-Warning "This script is not running as Administrator."
        Write-ColorMessage "Some operations might fail. It's recommended to run as Administrator." "Yellow"
        $choice = Read-Host "Continue anyway? (y/n)"
        if ($choice -ne "y") {
            Write-ColorMessage "Installation aborted." "Red"
            exit 1
        }
    }
    
    # Step 1: Check and install Python if needed
    Write-Step "1" "Checking and installing system requirements"
    Install-Python
    
    # Step 2: Install dependencies
    Install-Dependencies
    
    # Step 3: Create .env file
    Create-EnvFile
    
    # Step 4: Display completion message
    Show-CompletionMessage
}

# Run the main function
Start-Installation
