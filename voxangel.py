import os
import sys
import math
import pyaudio
import audioop
import datetime
import httplib
import socket

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
        print (resp.read(4096))
		
	
def activateDevice(host, port, dev):
    conn = httplib.HTTPConnection(host,port)
    try:
        conn.request("POST","/sdrangel/deviceset/"+str(dev)+"/device/run")
    except (httplib.HTTPException, socket.error):
        print ("Could not create connection. Exiting...")
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
        print ("Could not create connection. Exiting...")
        print ("----------------------------------------------------------------------------")
        print ("Bye.")
        sys.exit()		
    resp = conn.getresponse()
    print (str(datetime.datetime.now())+" -- >>> "+str(resp.status))

print ("============================================================================")
print ("voxangel v 0.1 --- A simple pyAudio-based VOX utility for SDRAngel          ")
print ("----------------------------------------------------------------------------")
if len(sys.argv) < 5:
    print ("usage -- python voxangel.py <level> <delay_in_ms> <host> <port> <device>")
    print ("----------------------------------------------------------------------------")
    print ("\n")
    print ("      <level> is the VOX threshold expressed as an integer ")
    print ("      corresponding to percent of maximum possible loudness")
    print ("      ( 5 is probably a good value).")
    print ("\n")
    print ("      <delay_in_ms> is delay for VOX to turn off in milliseconds.")
    print ("\n")
    print ("      <host> is the hostname or IP address of the SDRAngel server.")
    print ("\n")
    print ("      <port> is the port of the SDRAngel server.")
    print ("\n")
    print ("      <device> is the SDRAngel device number of the device to control.")
    print ("\n")
    print ("----------------------------------------------------------------------------")
    print ("Bye.")
    sys.exit()
rms_threshold = int(sys.argv[1])
off_delay = datetime.timedelta(milliseconds=int(sys.argv[2]))
sdrangel_host = str(sys.argv[3])
sdrangel_port = int(sys.argv[4])
sdrangel_dev  = int(sys.argv[5])
print ("Opening PortAudio default device... \n...(warnings below usually may be ignored.)")
pa = pyaudio.PyAudio()
print ("----------------------------------------------------------------------------")
print ("Testing SDRAngel REST API @ "+str(sdrangel_host)+":"+str(sdrangel_port)+"...")
testAPI(sdrangel_host,sdrangel_port,sdrangel_dev)
print ("----------------------------------------------------------------------------")
print ("Now listening for audio... RMS Threshold is: "+str(rms_threshold))+"%"
print ("Press CTRL + C to exit...  Delay is: "+str(int(sys.argv[2])))+"ms"
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
                print (str(datetime.datetime.now())+" -- PTT ON......( "+str(rms)+"% )") 
                report_time = datetime.datetime.now()
            if is_PTT == False: 
                print (str(datetime.datetime.now())+" -- LISTENING...( "+str(rms)+"% )")
                report_time = datetime.datetime.now()
		

except KeyboardInterrupt:
    print ("\n")
    print ("----------------------------------------------------------------------------")
    print ("Bye.")
    stream.stop_stream()
    stream.close()
    pa.terminate()
