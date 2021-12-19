#!/bin/bash

echo "Installing base dependencies"
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-pil \
    python3-numpy \
    gcc \
    make \
    build-essential \
    libopenjp2-7 \
    libtiff5 \
    libatlas-base-dev

sudo python3 -m pip install src/requirements.txt
