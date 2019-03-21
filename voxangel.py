import os
import sys
import pyaudio
import audioop
import datetime
from ctypes import *
from contextlib import contextmanager

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.025

last_1 = 0
last_2 = 0
last_3 = 0
is_PTT = False

print ("=============================================================================================")
print ("voxangel v 0.1 --- A simple pyAudio-based VOX utility for SDRAngel                           ")
print ("---------------------------------------------------------------------------------------------")
print ("Opening PortAudio default device... (warnings below usually may be ignored.)")
print ("---------------------------------------------------------------------------------------------")
pa = pyaudio.PyAudio()
print ("---------------------------------------------------------------------------------------------")
print ("Now listening for audio... Press CTRL + C to exit.                                          ")
print ("---------------------------------------------------------------------------------------------")

try:
    stream = pa.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=None)

    while True:
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
             data = stream.read(CHUNK)
             rms = audioop.rms(data, 2)    # here's where you calculate the volume

        if (rms > 0) and is_PTT == False :
            print (str(datetime.datetime.now())+" -- START")
            is_PTT = True

        if (rms + last_1 + last_2 + last_3 == 0) and is_PTT == True:
            print (str(datetime.datetime.now())+" -- STOP")
            is_PTT = False

        last_3 = last_2
        last_2 = last_1
        last_1 = rms


except KeyboardInterrupt:
    print ("\n")
    print ("---------------------------------------------------------------------------------------------")
    print ("Bye.")
    stream.stop_stream()
    stream.close()
    pa.terminate()
