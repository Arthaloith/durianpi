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
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user, login_required
from db import User
#========================================================================================================#
#========================================================================================================#
#                                                                                                        #
#                                          HARDWARE INITIALIZATIONS                                      #
#                                                                                                        #
#========================================================================================================#
app = Flask(__name__)
app.config["SECRET_KEY"] = "amogussus"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
user_db = User('cache/database.db')
#camera module
try:
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration()
    preview_config['main'] = {"size": (640, 480), "format": "YUV420"}
    picam2.configure(preview_config)
    picam2.start()
except Exception as e:
    print(f"Error initializing Picamera2: {e}")
#DTH22 sensor
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=True)
#========================================================================================================#
#========================================================================================================#
#                                                                                                        #
#                                             ROUTE DEFINITIONS                                          #
#                                                                                                        #
#========================================================================================================#
@app.route('/')
@login_required
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
@login_required
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
@login_required
def force_water():
    os.popen(f"{consts.PYTHON_VENV_LOCATION} pumpcontrol.py runnow")
    return render_template('force_water.html')

@app.route('/skip_water', methods=['POST'])
@login_required
def skip_water():
    os.popen(f"{consts.PYTHON_VENV_LOCATION} pumpcontrol.py skip &")
    return render_template('skip_water.html')

@app.route('/poll', methods=['POST'])
@login_required
def poll():
    os.popen(f"{consts.PYTHON_VENV_LOCATION} pumpcontrol.py check &")
    return render_template('poll.html')
#==============================================PUMP HISTORY================================================#
@app.route('/history', methods=['POST'])
@login_required
def history():
    pump_history = db.get_pump_history()
    return render_template('history.html', pump_history=pump_history)

@app.route('/clear', methods=['POST'])
@login_required
def clearHistory():
    pump_history = db.clear_pump_history()
    return render_template('clear.html', pump_history=pump_history)
#=============================================PROFILE MANAGEMENT============================================#
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    name = request.form['profile_name']
    threshold = int(request.form['soil_moisture_threshold'])
    pump_duration = int(request.form['pump_duration'])
    db.add_or_update_profile(name, threshold, pump_duration)
    return redirect(url_for('profiles'))

@app.route('/select_profile', methods=['POST'])
@login_required
def select_profile():
    profile_id = request.form['profile_id']
    db.set_active_profile(profile_id)
    return redirect(url_for('profiles'))

@app.route('/delete_profile/<int:profile_id>', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def handle_add_predefined_cron_jobs():
    if add_predefined_cron_jobs():
        return redirect(url_for('cron_job_page'), code=302)  
    else:
        return "Failed to add cron jobs", 500

@app.route('/add_cronjob', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def cron_job_page():
    cron_jobs = get_cron_jobs()
    available_commands = ['cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p1', 'cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p2','cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p3', 'cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python pumpcontrol.py p4', '@reboot cd /home/admin/Projects/durianpi && /home/admin/Projects/durianpi/myenv/bin/python webserver.py &', '']
    return render_template('cron.html', available_commands=available_commands,cron_jobs=cron_jobs)

#==============================================ANALYTICS=====================================================#
@app.route('/analytics')
@login_required
def analytics():
    most_active_day, most_active_day_count = db.get_most_active_day()
    most_active_month, most_active_month_count = db.get_most_active_month()
    least_active_day, least_active_day_count = db.get_least_active_day()
    total_events = db.get_total_events()

    return render_template('analytics.html',
                           most_active_day=most_active_day,
                           most_active_day_count=most_active_day_count,
                           most_active_month=most_active_month,
                           most_active_month_count=most_active_month_count,
                           least_active_day=least_active_day,
                           least_active_day_count=least_active_day_count,
                           total_events=total_events)
#==============================================USER AUTHENTICATION===========================================#
class UserLogin(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    user = user_db.get_user_by_id(user_id)
    if user:
        return UserLogin(user.id)
    return None

@app.route("/register", methods=["POST"])
@login_required
def register_user():
    if current_user.role != 'admin':
        return jsonify({"error": "Only admins can create new users"}), 403
    username = request.json["username"]
    password = request.json["password"]
    role = request.json.get("role", "user")
    user_db.create_user(username, password, role)
    return jsonify({"message": "User created successfully"}), 201

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = user_db.get_user(username)
        if user and user.check_password(password):
            login_user(UserLogin(user.id))
            return redirect(url_for("index"))
        return jsonify({"error": "Invalid username or password"}), 401
    return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "POST":
        logout_user()
        return redirect(url_for("login"))
    else:
        return redirect(url_for("logout"))

@app.route("/users", methods=["GET"])
@login_required
def get_users():
    if current_user.role != 'admin':
        return jsonify({"error": "Only admins can view all users"}), 403
    users = user_db.get_all_users()
    return jsonify([{"id": u.id, "username": u.username, "role": u.role} for u in users])

@app.route("/users/<id>", methods=["PUT", "DELETE"])
@login_required
def update_or_delete_user(id):
    if current_user.role != 'admin':
        return jsonify({"error": "Only admins can update or delete users"}), 403
    user = user_db.get_user_by_id(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if request.method == "PUT":
        user_db.update_user(id, request.json.get("username", user.username), request.json.get("role", user.role))
        return jsonify({"message": "User updated successfully"}), 200
    elif request.method == "DELETE":
        user_db.delete_user(id)
        return jsonify({"message": "User deleted successfully"}), 200

@app.route("/admin", methods=["GET"])
@login_required
def admin_page():
    if current_user.role != 'admin':
        return jsonify({"error": "Only admins can access the admin page"}), 403
    return render_template("admin.html")
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