import time
import board
import adafruit_dht
from pulseio import PulseIn

# Initialize the DHT sensor
dhtDevice = adafruit_dht.DHT22(board.D4,use_pulseio=True)  # Replace board.D4 with the actual GPIO pin you're using

while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temp: {temperature_c:.1f} C    Humidity: {humidity}% ")

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])

    time.sleep(1.0)
