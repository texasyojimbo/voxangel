import os
import sys
import math
import pyaudio
import audioop
import datetime
import httplib
import socket
import json
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.025

is_PTT = False

report_time = datetime.datetime.now()
last_exceeded_threshold = datetime.datetime.now()

def testAPI(host, port, dev):
    conn = httplib.HTTPConnection(host,port)
    try:
        conn.request("GET","/sdrangel/deviceset/"+str(dev)+"/device/report")
    except (httplib.HTTPException, socket.error):
        print ("Could not create connection. Exiting...")
        print ("----------------------------------------------------------------------------")
        print ("Bye.")
        sys.exit()		
    resp = conn.getresponse()
    if resp.status != 200:
        if resp.status == 404:
            print ("Error 404 returned... Does specified SDRAngel device exist?")
        else:
            print ("Exiting after error response: "+str(resp.status)+" "+str(resp.reason))
        print ("----------------------------------------------------------------------------")
        print ("Bye.")
        sys.exit()
    else:
        sdrangel_json = json.loads(resp.read(4096))
        if sdrangel_json["tx"] != 1:
            print "Selected device is not a sink / transmitter!"
            print ("----------------------------------------------------------------------------")
            print ("Bye.")
            sys.exit()
        else:
            print (sdrangel_json["deviceHwType"]+" found...")
            conn.request("GET","/sdrangel/deviceset/"+str(dev)+"/device/run")
            resp = conn.getresponse()
            sdrangel_json = json.loads(resp.read(4096))
            if sdrangel_json["state"] != "idle":
                print ("Selected device is already transmitting (state is not idle)!")
                print ("----------------------------------------------------------------------------")
                print ("Bye.")
                sys.exit()
            else:
                print ("Device is ready.")

	
def activateDevice(host, port, dev):
    conn = httplib.HTTPConnection(host,port)
    try:
        conn.request("POST","/sdrangel/deviceset/"+str(dev)+"/device/run")
    except (httplib.HTTPException, socket.error):
        print (str(datetime.datetime.now())+"-- ERROR -- Could not create connection. Exiting...")
        print ("----------------------------------------------------------------------------")
        print ("Bye.")
        sys.exit()		
    resp = conn.getresponse()
    print (str(datetime.datetime.now())+" -- >>> "+str(resp.status))

def deactivateDevice(host, port, dev):
    conn = httplib.HTTPConnection(host,port)
    try:
        conn.request("DELETE","/sdrangel/deviceset/"+str(dev)+"/device/run")
    except (httplib.HTTPException, socket.error):
        print (str(datetime.datetime.now())+" -- ERROR -- Could not create connection. Exiting...")
        print ("----------------------------------------------------------------------------")
        print ("Bye.")
        sys.exit()		
    resp = conn.getresponse()
    print (str(datetime.datetime.now())+" -- >>> "+str(resp.status))

def getDevice(host, port, dev):
    conn = httplib.HTTPConnection(host,port)
    try:
        conn.request("GET","/sdrangel/deviceset/"+str(dev)+"/device/run")
    except (httplib.HTTPException, socket.error):
        print (str(datetime.datetime.now())+"Could not create connection. Exiting...")
        print ("----------------------------------------------------------------------------")
        print ("Bye.")
        sys.exit()
    resp = conn.getresponse()
    if resp.status != 200:
        return False
    else:
        sdrangel_json = json.loads(resp.read(4096))
        if sdrangel_json["state"] == "idle":
            return False
        else:
            return True


print ("============================================================================")
print ("voxangel v 0.1 --- A simple pyAudio-based VOX utility for SDRAngel          ")
print ("----------------------------------------------------------------------------")
if len(sys.argv) < 7:
    print ("$ python voxangel.py <level> <delay_in_ms> <channel> <host> <port> <device>")
    print ("----------------------------------------------------------------------------")
    print ("\n")
    print ("      <level> is the VOX threshold expressed as an integer ")
    print ("      corresponding to percent of maximum possible loudness")
    print ("           (5 is probably a good value).")
    print ("\n")
    print ("      <delay_in_ms> is delay for VOX to turn off in milliseconds.")
    print ("\n")
    print ("      <channel> is the listen channel.")
    print ("           0 = left, 1 = right, 2 = stereo")
    print ("\n")
    print ("      <host> is the hostname or IP address of the SDRAngel server.")
    print ("           (usually 127.0.0.1)")
    print ("\n")
    print ("      <port> is the port of the SDRAngel server (usually 8091).")
    print ("\n")
    print ("      <device> is the SDRAngel device number of the device to control.")
    print ("\n")
    print ("----------------------------------------------------------------------------")
    print ("Bye.")
    sys.exit()
rms_threshold = int(sys.argv[1])
off_delay = datetime.timedelta(milliseconds=int(sys.argv[2]))
sdrangel_host = str(sys.argv[4])
sdrangel_port = int(sys.argv[5])
sdrangel_dev  = int(sys.argv[6])
audio_channel = int(sys.argv[3])
if audio_channel == 2:
    audio_channel_tag = "(stereo)"
elif audio_channel == 1:
    audio_channel_tag = ".(right)"
elif audio_channel == 0:
    audio_channel_tag = "..(left)"
else:
    audio_channel = 2
    audio_channel_tag = "stereo"
print ("Opening PortAudio default device... \n...(warnings below usually may be ignored.)")
pa = pyaudio.PyAudio()
print ("----------------------------------------------------------------------------")
print ("Testing SDRAngel REST API @ "+str(sdrangel_host)+":"+str(sdrangel_port)+"...")
testAPI(sdrangel_host,sdrangel_port,sdrangel_dev)
print ("----------------------------------------------------------------------------")
print ("Now listening for audio..."+audio_channel_tag+"... VOX RMS Threshold is: "+str(rms_threshold))+"%"
print ("Press CTRL + C to exit............... VOX Release Delay is: "+str(int(sys.argv[2])))+"ms"
print ("----------------------------------------------------------------------------")

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
            if audio_channel != 2:
                data = np.fromstring(data, dtype=np.int16)
                data = np.reshape(data, (CHUNK,2))
                data = data[:, audio_channel].flatten().astype(np.int16).tostring()
            rms = math.floor(( audioop.rms(data, 2) / 32768.00 ) * 100)
				
        if (rms > rms_threshold) and is_PTT == True:
            last_exceeded_threshold = datetime.datetime.now()
		
        if (rms > rms_threshold) and is_PTT == False :
            print (str(datetime.datetime.now())+" -- STARTING....( "+str(rms)+"% )")
            report_time = datetime.datetime.now()
            is_PTT = True
            activateDevice(sdrangel_host, sdrangel_port, sdrangel_dev)
		
        if (rms < rms_threshold) and is_PTT == True:
            if last_exceeded_threshold + off_delay < datetime.datetime.now():
                print (str(datetime.datetime.now())+" -- STOPPING....( "+str(rms)+"% )")
                report_time = datetime.datetime.now()
                is_PTT = False
                deactivateDevice(sdrangel_host, sdrangel_port, sdrangel_dev)
		
        if datetime.datetime.now() > (report_time + datetime.timedelta(seconds=5)):
            if is_PTT == True:
                if (getDevice(sdrangel_host, sdrangel_port, sdrangel_dev)):
                    print (str(datetime.datetime.now())+" -- PTT ON......( "+str(rms)+"% )") 
                else:
                    activateDevice(sdrangel_host, sdrangel_port, sdrangel_dev)
                report_time = datetime.datetime.now()
            if is_PTT == False: 
                print (str(datetime.datetime.now())+" -- LISTENING...( "+str(rms)+"% )")
                report_time = datetime.datetime.now()
		

except KeyboardInterrupt:
    print ("\n")
    if is_PTT == True:
        print (str(datetime.datetime.now())+" -- STOPPING....( "+str(rms)+"% )")
        deactivateDevice(sdrangel_host, sdrangel_port, sdrangel_dev)
    print ("----------------------------------------------------------------------------")
    print ("Bye.")
    stream.stop_stream()
    stream.close()
    pa.terminate()
