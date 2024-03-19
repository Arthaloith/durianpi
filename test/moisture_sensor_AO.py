import busio
import digitalio
import board
import time
import RPi.GPIO as GPIO
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

cs = digitalio.DigitalInOut(board.CE0)

mcp = MCP.MCP3008(spi, cs)

chan = AnalogIn(mcp, MCP.P0)



while True:
    soil_value = chan.value / 64
    print("Raw ADC Value: ", soil_value)
    print('ADC Voltage: ' + str(chan.voltage) + 'V') 
    time.sleep(2)
