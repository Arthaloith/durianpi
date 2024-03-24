import speech_recognition as sr

r=sr.Recognizer()
mic=sr.Microphone()

print("start talking")

while True:
    with mic as source:
        audio = r.listen(source)
    words = r.recognize_google(audio)
    print(words)
