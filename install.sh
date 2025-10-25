#!/bin/bash

# fsociety Installation Script
# This script sets up fsociety with all dependencies on Linux/macOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    echo "=================================================="
    print_message "$BLUE" "$1"
    echo "=================================================="
    echo ""
}

print_success() {
    print_message "$GREEN" "✓ $1"
}

print_error() {
    print_message "$RED" "✗ $1"
}

print_warning() {
    print_message "$YELLOW" "! $1"
}

print_info() {
    print_message "$BLUE" "→ $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_warning "Please do not run this script as root"
        print_info "The script will ask for sudo when needed"
        exit 1
    fi
}

# Check Python version
check_python() {
    print_header "Checking Python Version"

    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
        print_success "Python 3.12 found"
    elif command -v python3.13 &> /dev/null; then
        PYTHON_CMD="python3.13"
        print_success "Python 3.13 found"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [ "$(echo "$PYTHON_VERSION >= 3.12" | bc -l)" -eq 1 ]; then
            PYTHON_CMD="python3"
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.12+ is required, found Python $PYTHON_VERSION"
            print_info "Please install Python 3.12 or higher"
            exit 1
        fi
    else
        print_error "Python 3.12+ is required but not found"
        print_info "Please install Python 3.12 or higher"
        exit 1
    fi
}

# Detect OS
detect_os() {
    print_header "Detecting Operating System"

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
            print_success "Detected: $PRETTY_NAME"
        else
            print_error "Cannot detect Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "Detected: macOS"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_header "Installing System Dependencies"

    case $OS in
        ubuntu|debian|kali)
            print_info "Installing dependencies for Debian/Ubuntu..."
            sudo apt update
            sudo apt install -y \
                git \
                python3-pip \
                python3-venv \
                nmap \
                nmap-scripts \
                build-essential \
                libpcap-dev \
                libssl-dev \
                curl \
                wget \
                golang-go
            print_success "System dependencies installed"
            ;;

        arch|manjaro)
            print_info "Installing dependencies for Arch Linux..."
            sudo pacman -Sy --noconfirm \
                git \
                python-pip \
                nmap \
                base-devel \
                libpcap \
                openssl \
                curl \
                wget \
                go
            print_success "System dependencies installed"
            ;;

        fedora|rhel|centos)
            print_info "Installing dependencies for Fedora/RHEL..."
            sudo dnf install -y \
                git \
                python3-pip \
                nmap \
                gcc \
                gcc-c++ \
                make \
                libpcap-devel \
                openssl-devel \
                curl \
                wget \
                golang
            print_success "System dependencies installed"
            ;;

        macos)
            print_info "Installing dependencies for macOS..."
            if ! command -v brew &> /dev/null; then
                print_error "Homebrew is required but not installed"
                print_info "Install from: https://brew.sh"
                exit 1
            fi
            brew install \
                git \
                nmap \
                libpcap \
                openssl \
                curl \
                wget \
                go
            print_success "System dependencies installed"
            ;;

        *)
            print_warning "Unknown OS, skipping system dependencies"
            print_info "Please install: git, nmap, gcc, libpcap, golang manually"
            ;;
    esac
}

# Install optional tools
install_optional_tools() {
    print_header "Installing Optional Tools"

    # Ask about hashcat
    read -p "Install hashcat for GPU-accelerated password cracking? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $OS in
            ubuntu|debian|kali)
                sudo apt install -y hashcat
                ;;
            arch|manjaro)
                sudo pacman -S --noconfirm hashcat
                ;;
            fedora|rhel|centos)
                sudo dnf install -y hashcat
                ;;
            macos)
                brew install hashcat
                ;;
        esac
        print_success "hashcat installed"
    fi

    # Ask about Go tools
    read -p "Install Go (required for some tools like Nuclei)? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! command -v go &> /dev/null; then
            case $OS in
                ubuntu|debian|kali)
                    sudo apt install -y golang-go
                    ;;
                arch|manjaro)
                    sudo pacman -S --noconfirm go
                    ;;
                fedora|rhel|centos)
                    sudo dnf install -y golang
                    ;;
                macos)
                    brew install go
                    ;;
            esac
            print_success "Go installed"
        else
            print_success "Go already installed"
        fi
    fi
}

# Create virtual environment
create_venv() {
    print_header "Creating Virtual Environment"

    read -p "Create Python virtual environment? (Recommended) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ ! -d "venv" ]; then
            $PYTHON_CMD -m venv venv
            print_success "Virtual environment created"

            # Activate venv
            source venv/bin/activate
            print_success "Virtual environment activated"
            USE_VENV=true
        else
            print_warning "Virtual environment already exists"
            source venv/bin/activate
            USE_VENV=true
        fi
    else
        USE_VENV=false
    fi
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"

    if [ "$USE_VENV" = true ]; then
        print_info "Installing in virtual environment..."
    else
        print_info "Installing globally..."
    fi

    # Upgrade pip
    $PYTHON_CMD -m pip install --upgrade pip

    # Install fsociety
    $PYTHON_CMD -m pip install -e .

    print_success "Python dependencies installed"
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"

    # Check fsociety import
    if $PYTHON_CMD -c "import fsociety" 2>/dev/null; then
        print_success "fsociety module imports correctly"
    else
        print_error "fsociety module import failed"
        exit 1
    fi

    # Check command availability
    if command -v fsociety &> /dev/null; then
        print_success "fsociety command available"
        FSOCIETY_VERSION=$(fsociety --info 2>/dev/null | grep -i version || echo "unknown")
        print_info "Version: $FSOCIETY_VERSION"
    else
        print_warning "fsociety command not in PATH"
        print_info "You may need to restart your shell or run: source venv/bin/activate"
    fi

    # Check GPU support
    if command -v hashcat &> /dev/null; then
        print_success "GPU acceleration available (hashcat installed)"
    else
        print_warning "GPU acceleration not available (hashcat not installed)"
    fi

    # Check nmap
    if command -v nmap &> /dev/null; then
        print_success "nmap installed"
    else
        print_warning "nmap not installed (required for network scanning)"
    fi
}

# Print next steps
print_next_steps() {
    print_header "Installation Complete!"

    echo ""
    print_success "fsociety has been installed successfully!"
    echo ""
    print_info "Next steps:"
    echo ""

    if [ "$USE_VENV" = true ]; then
        echo "  1. Activate virtual environment:"
        echo "     source venv/bin/activate"
        echo ""
    fi

    echo "  2. Run fsociety:"
    echo "     fsociety"
    echo ""
    echo "  3. Read documentation:"
    echo "     - Quick Start: cat QUICKSTART.md"
    echo "     - Features:    cat MODERN_FEATURES.md"
    echo "     - README:      cat README.md"
    echo ""
    print_info "Configuration:"
    echo "  - Config file: ~/.fsociety/fsociety.cfg"
    echo "  - Tools dir:   ~/.fsociety/"
    echo "  - Logs:        ~/.fsociety/fsociety.log"
    echo ""
    print_warning "Legal Notice:"
    echo "  fsociety is for authorized security testing only."
    echo "  Always obtain written permission before testing any system."
    echo ""
}

# Main installation flow
main() {
    print_header "fsociety Installation Script"
    print_info "Version 4.0.0 - Modern Penetration Testing Framework"
    echo ""

    check_root
    check_python
    detect_os
    install_system_deps
    install_optional_tools
    create_venv
    install_python_deps
    verify_installation
    print_next_steps
}

# Run main
main
