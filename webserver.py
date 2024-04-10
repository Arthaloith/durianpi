#========================================================================================================#
#                                                                                                        #
#                                               LIBRARY IMPORTS                                          #
#                                                                                                        #
#========================================================================================================#
from flask import Flask, Response,redirect, render_template, jsonify, request, url_for
import db
import os
import pumpcontrol
import psutil
import consts
import math
from picamera2 import Picamera2, Preview
import cv2
import numpy as np
import subprocess
import adafruit_dht
import board
#========================================================================================================#
#========================================================================================================#
#                                                                                                        #
#                                          HARDWARE INITIALIZATIONS                                      #
#                                                                                                        #
#========================================================================================================#
app = Flask(__name__)
#camera module
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
preview_config['main'] = {"size": (640, 480), "format": "YUV420"}
picam2.configure(preview_config)
picam2.start()
#DTH22 sensor
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=True)
#========================================================================================================#
#========================================================================================================#
#                                                                                                        #
#                                             ROUTE DEFINITIONS                                          #
#                                                                                                        #
#========================================================================================================#
@app.route('/')
def index():
    latest_pump_run = db.get_latest_pump_run()
    pump_history = db.get_pump_history_only_5()
    
    soil_moisture = pumpcontrol.get_soil_moisture()

    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent()
    cpu_temp = psutil.sensors_temperatures().get('cpu_thermal', [None])[0]
    
    temperature_c = dhtDevice.temperature
    humidity = dhtDevice.humidity
    
    return render_template('index.html', soil_value=soil_moisture, latest_pump_run=latest_pump_run, pump_history=pump_history, soil_moisture=soil_moisture, ram_usage=ram_usage, cpu_usage=cpu_usage, cpu_temp=cpu_temp,temperature=temperature_c, humidity=humidity)

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
    
    temperature_c = dhtDevice.temperature
    humidity = dhtDevice.humidity
    
    if cpu_temp and cpu_temp.current != 'N/A':
        cpu_temp_current = int(float(cpu_temp.current))
    else:
        cpu_temp_current = 'N/A'
        
    return {
        'soil_moisture': rounded_soil_moisture,
        'ram_usage': ram_usage,
        'cpu_usage': cpu_usage,
        'cpu_temp': cpu_temp_current,
        'temperature': temperature_c,
        'humidity': humidity
    }

#==============================================PUMP CONTROL================================================#

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
#==============================================PUMP HISTORY================================================#
@app.route('/history', methods=['POST'])
def history():
    pump_history = db.get_pump_history()
    return render_template('history.html', pump_history=pump_history)

@app.route('/clear', methods=['POST'])
def clearHistory():
    pump_history = db.clear_pump_history()
    return render_template('clear.html', pump_history=pump_history)
#=============================================PROFILE MANAGEMENT============================================#
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

#==============================================CAMERA FUNCTIONS===============================================#
def generate_camera_feed():
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YV12)
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/camera')
def camera_feed():
    return Response(generate_camera_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')
#==============================================CRON MANAGEMENT================================================#
def add_cron_job(cron_job):
    try:
        # Capture the current user's crontab into a temporary file
        subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        crontab_output = subprocess.run(['crontab', '-l'], capture_output=True, text=True).stdout

        # Append the new cron job to the captured crontab output
        new_crontab = crontab_output.strip() + '\n' + cron_job + '\n'

        # Load the modified crontab from the temporary file
        subprocess.run(['crontab'], input=new_crontab, text=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error adding cron job: {e}")
        return False
    
def add_predefined_cron_jobs():
    script_path = "/home/admin/Projects/durianpi/cronjob.sh"  
    try:
        subprocess.run(["sh", script_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running cronjob script: {e}")
        return False

@app.route('/add_predefined_cronjob', methods=['POST'])
def handle_add_predefined_cron_jobs():
    if add_predefined_cron_jobs():
        return redirect(url_for('cron_job_page'), code=302)  
    else:
        return "Failed to add cron jobs", 500

@app.route('/add_cronjob', methods=['POST'])
def handle_add_cron_jobs():
    minute = request.form['minute']
    hour = request.form['hour']
    day_month = request.form['day_month']
    month = request.form['month']
    day_week = request.form['day_week']
    custom_command = request.form['custom_command']
    command = request.form['command']

    cron_job = f"{minute} {hour} {day_month} {month} {day_week} {custom_command} {command}"
    if add_cron_job(cron_job):
        return redirect(url_for('cron_job_page'), code=302)
    else:
        return "Failed to add cron job", 500
    
@app.route('/clear_cronjob', methods=['POST'])
def clear_cronjob():
    try:
        subprocess.run("crontab -r", shell=True, check=True)
        return redirect(url_for('cron_job_page'), code=302)
    except subprocess.CalledProcessError as e:
        print(f"Error clearing cronjobs: {e}")
        return "Failed to clear cronjobs", 500
    
def get_cron_jobs():
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        cron_jobs = result.stdout.strip()
        return cron_jobs
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving cron jobs: {e}")
        return None
    
@app.route('/cron')
def cron_job_page():
    cron_jobs = get_cron_jobs()
    available_commands = ['cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p1', 'cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p2','cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p3','@reboot cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python webserver.py &', '']
    return render_template('cron.html', available_commands=available_commands,cron_jobs=cron_jobs)
#==============================================SYSTEM CONTROL================================================#
@app.route('/shutdown', methods=['POST'])
def shutdown():
    os.system('sudo shutdown now')
    return 'Shutting down...'

@app.route('/reboot', methods=['POST'])
def reboot():
    os.system('sudo reboot')
    return 'Rebooting...'
#============================================================================================================#
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')