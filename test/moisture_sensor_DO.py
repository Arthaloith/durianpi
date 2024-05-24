import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(4, GPIO.IN)  # Set GPIO4 as input to read the soil moisture sensor

try:
    print("Detecting soil moisture levels. Press CTRL+C to exit.")
    while True:
        # Read the soil moisture sensor
        if GPIO.input(4):
            print("Soil is Wet")
        else:
            print("Soil is Dry")
        time.sleep(1)  # Wait for 1 second before reading again

except KeyboardInterrupt:
    # Clean up GPIO on CTRL+C exit
    GPIO.cleanup()

GPIO.cleanup()  # Clean up GPIO on normal exit
