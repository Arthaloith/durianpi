import os
import sys
import speech_recognition as sr
import subprocess 
import sounddevice

r = sr.Recognizer()

mic = sr.Microphone(device_index=1)

while True:
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        audio = r.listen(source)
    try:
        words = r.recognize_google(audio)
        print(words)
        if words.lower() == "hello":
            print("executing pumpcontrol.py...")
            subprocess.run(["python", "/home/admin/Projects/durianpi/pumpcontrol.py", "runnow"])
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing pumpcontrol.py; {e}")


