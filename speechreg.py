import os
import sys
import speech_recognition as sr
import subprocess 
import sounddevice

r = sr.Recognizer()

mic = sr.Microphone(device_index=1)

print("Start talking...")

while True:
    with mic as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source)
    try:
        words = r.recognize_google(audio, language='vi-VN')
        print(words)
        if words.lower() == "activate":
            print("executing pumpcontrol.py...")
            subprocess.run(["python", "durianpi/pumpcontrol.py", "runnow"])
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing pumpcontrol.py; {e}")


