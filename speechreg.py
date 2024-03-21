import speech_recognition as sr

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

# Specify the microphone to use by its card and device index
# According to `arecord -l`, your USB Audio Device is card 3, device 0
mic = sr.Microphone(device_index=3)

with mic as source:
    print("Adjusting noise...")
    # Adjust the recognizer sensitivity to ambient noise
    r.adjust_for_ambient_noise(source, duration=1)
    print("Recording, speak now...")
    # Listen for the first phrase and extract it into audio data
    audio = r.listen(source)

print("Recognizing...")
try:
    # Recognize speech using Google Web Speech API
    print("You said: " + r.recognize_google(audio))
except sr.UnknownValueError:
    # Error handling for unrecognized speech
    print("Google Web Speech API could not understand audio")
except sr.RequestError as e:
    # Error handling for API request errors
    print(f"Could not request results from Google Web Speech API; {e}")
