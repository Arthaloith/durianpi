#========================================================================================================#
#                                                                                                        #
#                                               LIBRARY IMPORTS                                          #
#                                                                                                        #
#========================================================================================================#
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
from consts import RELAY_GPIO, PUMP_DURATION, PUMP_RUN_INTERVAL
#========================================================================================================#
#========================================================================================================#
#                                                                                                        #
#                                               HARDWARE SETUPS                                          #
#                                                                                                        #
#========================================================================================================#
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
#========================================================================================================#

def poll():
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
    duration_str = f'{consts.PUMP_DURATION} seconds'
    entry = (readable_timestamp, 'Pump Run', duration_str)

    db.log_pump_run(entry)

def get_soil_moisture():
    soil_value = chan.value / 64
    moisture_percentage = 100 - math.ceil((soil_value / 1024) * 100)
    return moisture_percentage

def test():
    print( get_soil_moisture())


def activateChecknPump():
    profile = db.get_active_profile()
    if not profile:
        soil_moisture_threshold = 50
    else:
        soil_moisture_threshold = profile['soil_moisture_threshold']
    
    soil_value = get_soil_moisture()
    if soil_value < soil_moisture_threshold:
        runPump()
    else:
        readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        duration_str = 'N/A'

        entry = (readable_timestamp, 'Pump Run Failed due too moisture still too high', duration_str)
        db.log_pump_run(entry)
            
def heartBeat():
    readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = (readable_timestamp, 'Heartbeat', '1')
    
    db.log_pump_run(entry)
#========================================================================================================#
#                                                                                                        #
#                                               DURIAN PROFILES                                          #
#                                                                                                        #
#========================================================================================================#
# Phase 1: small plant
def phaseOne():
    soil_value = get_soil_moisture()
    if soil_value < 70:
        pumpRelay.on()
        time.sleep(14)
        pumpRelay.off()
        
        readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = (readable_timestamp, 'Pump Run', '14 seconds')
        db.log_pump_run(entry)
    else:
        readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = (readable_timestamp, 'Pump Run (failed, too wet)', 'N/A')
        db.log_pump_run(entry)
# Phase 2: blooming plant
def phaseTwo():
    soil_value = get_soil_moisture()
    if soil_value < 60:
        pumpRelay.on()
        time.sleep(14)
        pumpRelay.off()
        
        readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = (readable_timestamp, 'Pump Run', '14 seconds')
        db.log_pump_run(entry)
    else:
        readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = (readable_timestamp, 'Pump Run (failed, too wet)', 'N/A')
        db.log_pump_run(entry)
# Phase 3: fruiting plant
def phaseThree():
    soil_value = get_soil_moisture()
    if soil_value < 50:
        pumpRelay.on()
        time.sleep(14)
        pumpRelay.off()
        
        readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = (readable_timestamp, 'Pump Run', '14 seconds')
        
        db.log_pump_run(entry)
    else:
        readable_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = (readable_timestamp, 'Pump Run (failed, too wet)', 'N/A')
        db.log_pump_run(entry)
        
if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'runnow':
            runPump()
        elif sys.argv[1] == 'createdb':
            db.create_tables()
        elif sys.argv[1] == 'createpf':
            db.create_tables_profile()
        elif sys.argv[1] == 'check':
            activateChecknPump()
        elif sys.argv[1] == 'skip':
            skipPump()
        elif sys.argv[1] == 'bump':
            heartBeat()
        elif sys.argv[1] == 'p1':
            phaseOne()
        elif sys.argv[1] == 'p2':
            phaseTwo()
        elif sys.argv[1] == 'p3':
            phaseThree()
        else:
            print("Invalid argument. Available options are 'runnow' or 'createdb'.")
    else:
        heartBeat()
        poll()
