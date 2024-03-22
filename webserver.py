from flask import Flask, Response, redirect, render_template, jsonify, request, url_for
import db
import os
import pumpcontrol
import psutil
import consts
import math
import cv2
import response
app = Flask(__name__)

@app.route('/')
def index():
    latest_pump_run = db.get_latest_pump_run()
    
    pump_history = db.get_pump_history_only_5()
    
    soil_moisture = pumpcontrol.get_soil_moisture()

    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent()
    cpu_temp = psutil.sensors_temperatures().get('cpu_thermal', [None])[0]
    
    # Render the template with the data
    return render_template('index.html', soil_value=soil_moisture, latest_pump_run=latest_pump_run, pump_history=pump_history, soil_moisture=soil_moisture, ram_usage=ram_usage, cpu_usage=cpu_usage, cpu_temp=cpu_temp)

@app.route('/profiles')
def profiles():
    profiles = db.get_all_profiles()
    active_profile = db.get_active_profile()
    return render_template('profiles.html', profiles=profiles, active_profile=active_profile)

@app.route('/get_values', methods=['GET'])
def get_values():
    soil_moisture = pumpcontrol.get_soil_moisture()
    rounded_soil_moisture = math.ceil(soil_moisture)

    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent()
    cpu_temp = psutil.sensors_temperatures().get('cpu_thermal', [None])[0]
    
    if cpu_temp and cpu_temp.current != 'N/A':
        cpu_temp_current = int(float(cpu_temp.current))
    else:
        cpu_temp_current = 'N/A'
        
    return {
        'soil_moisture': rounded_soil_moisture,
        'ram_usage': ram_usage,
        'cpu_usage': cpu_usage,
        'cpu_temp': cpu_temp_current
    }



@app.route('/force_water', methods=['POST'])
def force_water():
    os.popen(f"{consts.PYTHON_VENV_LOCATION} pumpcontrol.py runnow")
    return render_template('force_water.html')

@app.route('/skip_water', methods=['POST'])
def skip_water():
    os.popen(f"{consts.PYTHON_VENV_LOCATION} pumpcontrol.py skip &")
    return render_template('skip_water.html')

@app.route('/poll', methods=['POST'])
def poll():
    os.popen(f"{consts.PYTHON_VENV_LOCATION} pumpcontrol.py &")
    return render_template('poll.html')

@app.route('/history', methods=['POST'])
def history():
    pump_history = db.get_pump_history()
    return render_template('history.html', pump_history=pump_history)

@app.route('/clear', methods=['POST'])
def clearHistory():
    pump_history = db.clear_pump_history()
    return render_template('clear.html', pump_history=pump_history)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    name = request.form['profile_name']
    threshold = int(request.form['soil_moisture_threshold'])
    db.add_or_update_profile(name, threshold)
    return redirect(url_for('profiles'))


@app.route('/select_profile', methods=['POST'])
def select_profile():
    profile_id = request.form['profile_id']
    db.set_active_profile(profile_id)
    return redirect(url_for('profiles'))

@app.route('/delete_profile/<int:profile_id>', methods=['POST'])
def delete_profile(profile_id):
    db.delete_profile(profile_id)
    return redirect(url_for('profiles'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')