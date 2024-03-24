import speech_recognition as sr
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print("Microphone with name \"{0}\" found for `Microphone(device_index={1})`".format(name, index))