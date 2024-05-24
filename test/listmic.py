import speech_recognition as sr

# Create a recognizer object
r = sr.Recognizer()

# Get the list of available microphones
microphone_list = sr.Microphone.list_microphone_names()

# Print the list of microphones
for i, microphone_name in enumerate(microphone_list):
    print(f"Microphone {i}: {microphone_name}")