# Use Python 3.12 Slim as base image
FROM python:3.12-slim

# Set a non-root user for security
RUN useradd -ms /bin/bash fsociety_user

# Update Repos and Install Necessary Packages
RUN apt-get update \
  && apt-get install -qq -y --no-install-recommends \
     build-essential \
     sudo \
     git \
     wget \
     curl \
     nmap \
     ruby \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the working directory
WORKDIR /home/fsociety_user

# Install Python dependencies (pin versions to ensure consistency)
RUN pip install --no-cache-dir requests==2.31.0

# Clone fsociety repository and install
RUN git clone https://github.com/Manisso/fsociety.git \
  && cd fsociety \
  && chmod +x install.sh \
  && ./install.sh

# Change ownership of the fsociety folder to the non-root user
RUN chown -R fsociety_user:fsociety_user /home/fsociety_user/fsociety

# Switch to non-root user
USER fsociety_user

# Set the working directory for fsociety
WORKDIR /home/fsociety_user/fsociety

# Hack to keep the container running
CMD python -c "import signal; signal.pause()"
