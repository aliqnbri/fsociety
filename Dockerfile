# Multi-stage Dockerfile for fsociety with optional GPU support

# Base stage with common dependencies
FROM python:3.13-slim AS base

LABEL org.opencontainers.image.title="fsociety" \
      org.opencontainers.image.description="AI-Powered High-Performance Penetration Testing Framework" \
      org.opencontainers.image.authors="fsociety-team <contact@fsociety.dev>" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/fsociety-team/fsociety" \
      org.opencontainers.image.version="4.0.0"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nmap \
    nmap-common \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt pyproject.toml ./
COPY fsociety/__version__.py fsociety/__version__.py

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# CPU-only stage
FROM base AS cpu

COPY . .

RUN pip install --no-cache-dir -e .

CMD ["fsociety"]
ENTRYPOINT ["python", "-m", "fsociety"]


# GPU stage with CUDA support
FROM nvidia/cuda:12.3.0-base-ubuntu22.04 AS gpu

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    CUDA_HOME=/usr/local/cuda

# Install Python 3.12 and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-dev \
    python3.12-distutils \
    python3-pip \
    git \
    nmap \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Make Python 3.12 the default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY fsociety/__version__.py fsociety/__version__.py

# Install dependencies with GPU support
RUN pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu121

COPY . .

RUN pip3 install --no-cache-dir -e ".[ai,gpu]"

# Verify CUDA installation
RUN python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

CMD ["--ai"]
ENTRYPOINT ["python3", "-m", "fsociety"]


# Development stage
FROM base AS dev

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest>=7.4.0 \
    pytest-asyncio>=0.21.0 \
    pytest-cov>=4.1.0 \
    pytest-benchmark>=4.0.0 \
    black>=23.12.0 \
    ruff>=0.1.9 \
    mypy>=1.8.0 \
    ipython \
    ipdb

COPY . .

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["/bin/bash"]


# Lightweight Alpine-based image
FROM python:3.13-alpine AS alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache \
    git \
    nmap \
    nmap-scripts \
    curl \
    wget \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY fsociety/__version__.py fsociety/__version__.py

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir -e .

CMD ["--info"]
ENTRYPOINT ["python", "-m", "fsociety"]


# Default to CPU stage
FROM cpu AS final