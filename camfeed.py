from flask import Flask, Response
from picamera2 import Picamera2, Preview
import cv2
import numpy as np

app = Flask(__name__)

# Initialize Picamera2
# Initialize Picamera2
picam2 = Picamera2()

# Start the preview (adjust according to the Picamera2 API)
picam2.start_preview(Preview.QTGL)

# Create a preview configuration
# The method to get or create a configuration might be different, so adjust as necessary
preview_config = picam2.create_preview_configuration()  # Hypothetical method, use the correct one

# Assuming preview_config is a dictionary or similar structure, directly adjusting its content
# If Picamera2 uses a different approach for setting configuration, adapt accordingly
preview_config['main'] = {"size": (640, 480),
                          "format": "YUV420"}

# Apply the preview configuration to the camera
picam2.configure(preview_config)

# Start capturing with the applied configuration
picam2.start()

def generate_camera_feed():
    """
    Generator function to capture camera frames and encode them as JPEG
    images. This stream of images can be consumed by a client to display
    a live video feed.
    """
    while True:
        # Capture frame from the camera
        frame = picam2.capture_array()
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Yield the binary data for the frame, properly formatted for HTTP
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/camera')
def camera_feed():
    """
    Route to serve the live feed from the camera. It uses server-sent events
    to continuously stream the camera feed to the client.
    """
    return Response(generate_camera_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
