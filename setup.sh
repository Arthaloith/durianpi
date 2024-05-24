#!/bin/bash

# Create a virtual environment
python -m venv myenv

# Activate the virtual environment on terminal open
echo "source myenv/bin/activate" >> ~/.bashrc

# Install required Python packages
source myenv/bin/activate
pip install adafruit-circuitpython-mcp3xxx adafruit-blinka gpiozero flask spidev psutil response rpi-kms rpi-libcamera pyqt5 pyopengl imutils speechrecognition adafruit-circuitpython-dht sounddevice

# Run the cron job script
sh cronjob.sh

# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt full-upgrade

# Install Visual Studio Code
sudo apt install code -y
