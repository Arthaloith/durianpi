import os
import sys
import speech_recognition as sr
import subprocess  # Import subprocess module

# Create a recognizer instance
r = sr.Recognizer()

# Specify the device index of the microphone you wish to use
mic = sr.Microphone(device_index=1)

print("Start talking...")

while True:
    with mic as source:
        # Optionally adjust for ambient noise
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source)
    try:
        # Recognize speech using Google's speech recognition service
        words = r.recognize_google(audio)
        print(words)
        if words.lower() == "activate":  # Check if the recognized word is "hello"
            print("executing pumpcontrol.py...")
            subprocess.run(["python", "durianpi/pumpcontrol.py", "runnow"])  # Execute pumpcontrol.py
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing pumpcontrol.py; {e}")


