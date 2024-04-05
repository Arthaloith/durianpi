import sys
import gpiozero
import time
from datetime import datetime
import db
import consts
import busio
import adafruit_mcp3xxx.mcp3008 as MCP
from digitalio import DigitalInOut
import board
import math
from adafruit_mcp3xxx.analog_in import AnalogIn
from consts import RELAY_GPIO

def get_soil_moisture():
    soil_value = chan.value 
    moisture_percentage = 100 - math.ceil((soil_value / 1024) * 100)
    return soil_value

#setup relay
pumpRelay = gpiozero.OutputDevice(RELAY_GPIO, active_high = False, initial_value = False)

# Setup SPI
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Setup chip select (CS)
cs = DigitalInOut(board.CE0)

# Create MCP3008 object
mcp = MCP.MCP3008(spi, cs)

# Set up analog input channel
chan = AnalogIn(mcp, MCP.P0)
while True:
    print(get_soil_moisture())
    time.sleep(1)