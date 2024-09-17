#!/bin/bash
# Bash Script for install Fsociety tools
# Must run to install tool

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to log errors
error_log() {
    echo -e "\e[31m[✘] $1\e[0m"
}

# Function to handle installation in different environments
install_packages() {
    if [ "$TERMUX" = true ]; then
        log "Installing packages for Termux"
        pkg install -y git python || { error_log "Package installation failed!"; exit 1; }
    elif [ "$(uname)" = "Darwin" ]; then
        log "Installing Python 3.12 on macOS"
        brew install python@3.12 || { error_log "Failed to install Python 3.12 with Homebrew!"; exit 1; }
    else
        log "Installing packages for Linux"
        sudo apt update && sudo apt install -y git python3.12 python3.12-venv python3.12-dev || { error_log "Package installation failed!"; exit 1; }
    fi
}


# Main installation process
install_fsociety() {
    log "Cloning Fsociety repository..."
    git clone --depth=1 https://github.com/Manisso/fsociety "$INSTALL_DIR" || { error_log "Failed to clone repository!"; exit 1; }

    log "Creating executable..."
    echo "#!$BASH_PATH
python3 $INSTALL_DIR/fsociety.py" "${1+"$@"}" > "$INSTALL_DIR/fsociety"
    chmod +x "$INSTALL_DIR/fsociety"

    log "Copying files to binary directory..."
    if [ "$TERMUX" = true ]; then
        cp "$INSTALL_DIR/fsociety" "$BIN_DIR"
        cp "$INSTALL_DIR/fsociety.cfg" "$BIN_DIR"
    else
        sudo cp "$INSTALL_DIR/fsociety" "$BIN_DIR"
        sudo cp "$INSTALL_DIR/fsociety.cfg" "$BIN_DIR"
    fi
    rm "$INSTALL_DIR/fsociety"
}


# Check if script is being run as root or using sudo
if [ "$EUID" -ne 0 ] && [ "$(uname)" != "Darwin" ]; then
    error_log "Please run as root or using sudo!"
    exit 1
fi
# Clear the terminal and print the welcome message
clear
echo "
███████╗███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
█████╗  ███████╗██║   ██║██║     ██║█████╗     ██║    ╚████╔╝
██╔══╝  ╚════██║██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝
██║     ███████║╚██████╔╝╚██████╗██║███████╗   ██║      ██║
╚═╝     ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝

██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗     ███████╗██████╗
██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║     ██╔════╝██╔══██╗
██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║     █████╗  ██████╔╝
██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║     ██╔══╝  ██╔══██╗
██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗███████╗██║  ██║
╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
";

# Determine installation directories
if [ "$PREFIX" = "/data/data/com.termux/files/usr" ]; then
    INSTALL_DIR="$PREFIX/usr/share/doc/fsociety"
    BIN_DIR="$PREFIX/bin/"
    BASH_PATH="$PREFIX/bin/bash"
    TERMUX=true
elif [ "$(uname)" = "Darwin" ]; then
    INSTALL_DIR="/usr/local/fsociety"
    BIN_DIR="/usr/local/bin/"
    BASH_PATH="/bin/bash"
    TERMUX=false
else
    INSTALL_DIR="$HOME/.fsociety"
    BIN_DIR="/usr/local/bin/"
    BASH_PATH="/usr/bin/env bash"
    TERMUX=false
fi

log "Checking for existing installation..."
if [ -d "$INSTALL_DIR" ]; then
    read -p "[◉] A directory fsociety was found! Do you want to replace it? [Y/n]: " -r REPLACE
    if [[ "$REPLACE" =~ ^[Yy]$ ]]; then
        log "Removing existing installation..."
        if [ "$TERMUX" = true ]; then
            rm -rf "$INSTALL_DIR"
            rm "$BIN_DIR/fsociety*"
        else
            sudo rm -rf "$INSTALL_DIR"
            sudo rm "$BIN_DIR/fsociety*"
        fi
    else
        error_log "Installation aborted. Remove previous installations first."
        exit 1
    fi
fi

log "Cleaning up old directories..."
[ -d "$ETC_DIR/Manisso" ] && sudo rm -rf "$ETC_DIR/Manisso"

# Install required packages
install_packages

# Install fsociety tool
install_fsociety

# Final check to confirm successful installation
if [ -d "$INSTALL_DIR" ]; then
    log "Tool installed successfully!"
    echo -e "\n[✔] You can execute the tool by typing \e[32mfsociety\e[0m\n"
else
    error_log "Installation failed!"
    exit 1
fi