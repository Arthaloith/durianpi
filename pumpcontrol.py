import sys
import gpiozero
import time
from datetime import datetime
import db
import threading
import sqlite3
import consts
import busio
import gpiozero
import adafruit_mcp3xxx.mcp3008 as MCP
import time
from digitalio import DigitalInOut
import board
from adafruit_mcp3xxx.analog_in import AnalogIn

from consts import RELAY_GPIO, PUMP_DURATION, PUMP_RUN_INTERVAL

#setup relay
pumpRelay = gpiozero.OutputDevice(RELAY_GPIO, active_high = False, initial_value = False)

# Setup SPI
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Setup chip select (CS)
cs = DigitalInOut(board.CE0)

# Create MCP3008 object
mcp = MCP.MCP3008(spi, cs)

chan = AnalogIn(mcp, MCP.P0)

def poll():
    # Example interval in seconds, adjust as needed
    lastLog = db.get_latest_pump_run()
    interval = 0

    if lastLog is not None:
        lastTimestamp = datetime.strptime(lastLog['timestamp'], '%Y-%m-%d %H:%M:%S')
        interval = (datetime.now() - lastTimestamp).total_seconds()
        print(interval)
    else:
        interval = PUMP_RUN_INTERVAL + 1

    if interval > PUMP_RUN_INTERVAL:
        activateChecknPump()

def runPump():
    pumpRelay.on()
    time.sleep(PUMP_DURATION)
    pumpRelay.off()
    
    readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    duration_str = f'{consts.PUMP_DURATION} seconds'

    entry = (readable_timestamp, 'Pump Run', duration_str)
    
    db.log_pump_run(entry)

def skipPump():
    readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = (readable_timestamp, 'Skip Pump', 'N/A')

    db.log_pump_run(entry)

def get_soil_moisture():
    soil_value = chan.value / 64
    print("Soil moisture: ", soil_value)
    print('ADC Voltage: ' + str(chan.voltage) + 'V')
    
def activateChecknPump():
    # Read from the MCP3008 ADC
    soil_value = chan.value / 64
    print("Soil moisture: ", soil_value)
    print('ADC Voltage: ' + str(chan.voltage) + 'V')
    
    if soil_value >= 700:
        print("soil too sus, watering...")
        runPump()
    else:
        print("Soil is still too wet.")
            
def heartbeat():
    readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = (readable_timestamp, 'Heartbeat', '1')
    
    db.log_pump_run(entry)
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'runnow':
            runPump()
        elif sys.argv[1] == 'createdb':
            db.create_tables()
        elif sys.argv[1] == 'check':
            activateChecknPump()
        elif sys.argv[1] == 'skip':
            skipPump()
        else:
            print("Invalid argument. Available options are 'runnow' or 'createdb'.")
    else:
        heartbeat()
        poll()
