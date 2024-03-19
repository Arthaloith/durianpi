from flask import Flask, redirect, render_template, jsonify, request
import db
import os
import pumpcontrol
import psutil

app = Flask(__name__)

@app.route('/')
def index():
    # Get the latest pump run event
    latest_pump_run = db.get_latest_pump_run()
    
    # Get the pump history
    pump_history = db.get_pump_history_only_5()
    
    # Get the soil moisture value from pumpcontrol
    soil_moisture = pumpcontrol.get_soil_moisture()

    # Get system information
    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent()
    cpu_temp = psutil.sensors_temperatures().get('cpu_thermal', [None])[0]
    
    # Render the template with the data
    return render_template('index.html', soil_value=soil_moisture, latest_pump_run=latest_pump_run, pump_history=pump_history, ram_usage=ram_usage, cpu_usage=cpu_usage, cpu_temp=cpu_temp)

@app.route('/force_water', methods=['POST'])
def force_water():
    # Run the pump
    os.popen("python3 pumpcontrol.py runnow &")
    
    # Redirect back to the homepage after running the pump
    return render_template('force_water.html')

@app.route('/skip_water', methods=['POST'])
def skip_water():
    os.popen("python3 pumpcontrol.py skip &")
    return render_template('skip_water.html')

@app.route('/poll', methods=['POST'])
def poll():
    os.popen("python3 pumpcontrol.py &")
    return render_template('poll.html')

@app.route('/history', methods=['POST'])
def history():
    pump_history = db.get_pump_history()
    return render_template('history.html', pump_history=pump_history)

@app.route('/clear', methods=['POST'])
def clearHistory():
    pump_history = db.clear_pump_history()
    return render_template('clear.html', pump_history=pump_history)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')