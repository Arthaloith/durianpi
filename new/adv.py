from gpiozero import OutputDevice
import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import math

# Relay pin is connected to GPIO18 (Pin 12)
relay_pin = 18
relay = OutputDevice(relay_pin, active_high=False, initial_value=False)  # Set initial state to off

# Setup SPI
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Setup chip select (CS)
cs = digitalio.DigitalInOut(board.CE0)

# Create MCP3008 object
mcp = MCP.MCP3008(spi, cs)

# Set up analog input channel
chan = AnalogIn(mcp, MCP.P0)

def get_soil_moisture():
    soil_value = chan.value / 64
    moisture_percentage = 100 - math.ceil((soil_value / 1024) * 100)
    return moisture_percentage

def monitor_soil_moisture(threshold, pump_duration):
    while True:
        soil_moisture = get_soil_moisture()
        print(f"Current soil moisture: {soil_moisture}%")
        if soil_moisture < threshold:
            print("Soil is dry. Activating pump...")
            relay.on()
            time.sleep(pump_duration)
            relay.off()
            print("Pump deactivated.")
        time.sleep(1)  # Check soil moisture every second

def monitor_soil_moisture_stop_at_threshold(threshold):
    while True:
        soil_moisture = get_soil_moisture()
        print(f"Current soil moisture: {soil_moisture}%")
        if soil_moisture < threshold:
            if not relay.is_active:
                print("Soil is dry. Activating pump...")
                relay.on()
        else:
            if relay.is_active:
                print("Soil moisture threshold reached. Deactivating pump...")
                relay.off()
        time.sleep(1)  # Check soil moisture every second

try:
    print("Options:")
    print("1: Turn ON the relay")
    print("2: Turn OFF the relay")
    print("3: Monitor soil moisture and activate pump for a set duration")
    print("4: Monitor soil moisture and stop pump at threshold")
    print("5: Quit")

    while True:
        choice = input("Enter your choice (1, 2, 3, 4, or 5): ")

        if choice == '1':
            relay.on()
            print("Relay ON")

        elif choice == '2':
            relay.off()
            print("Relay OFF")

        elif choice == '3':
            threshold = int(input("Enter the soil moisture threshold (1-100): "))
            pump_duration = int(input("Enter the pump duration (in seconds): "))
            print("Monitoring soil moisture...")
            monitor_soil_moisture(threshold, pump_duration)

        elif choice == '4':
            threshold = int(input("Enter the soil moisture threshold (1-100): "))
            print("Monitoring soil moisture...")
            monitor_soil_moisture_stop_at_threshold(threshold)

        elif choice == '5':
            print("Exiting program...")
            break

        else:
            print("Invalid choice. Please try again.")

except KeyboardInterrupt:
    print("Exiting program...")
finally:
    relay.off()  # Ensure the relay is turned off

