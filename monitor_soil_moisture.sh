#!/bin/bash

while true; do
    python3 pumpcontrol.py bandaid
    echo "Soil moisture reached 100 for the second time. Restarting monitoring..."
    sleep 5  # Wait for 5 seconds before restarting
done
