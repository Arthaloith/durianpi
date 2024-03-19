import RPi.GPIO as GPIO
import time

# Relay pin is connected to GPIO18 (Pin 12)
relay_pin = 18

# Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numberings
GPIO.setup(relay_pin, GPIO.OUT)  # Set the relay pin as an output

try:
    print("Testing the relay. Press CTRL+C to exit.")
    
    while True:
        # Turn the relay ON
        GPIO.output(relay_pin, GPIO.HIGH)  # Or use GPIO.LOW depending on your relay's logic
        print("Relay OFF")
        time.sleep(2)  # Wait 2 seconds
        
        # Turn the relay OFF
        GPIO.output(relay_pin, GPIO.LOW)  # Or use GPIO.HIGH depending on your relay's logic
        print("Relay ON")
        time.sleep(2)  # Wait 2 seconds

except KeyboardInterrupt:
    # Clean up GPIO on CTRL+C exit
    GPIO.cleanup()

GPIO.cleanup()  # Clean up GPIO on normal exit

