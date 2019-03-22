# voxangel v. 0.1
VOX trigger for SDRAngel using PyAudio and SDRAngel REST API

============================================================================
voxangel v 0.1 --- A simple pyAudio-based VOX utility for SDRAngel
----------------------------------------------------------------------------
$ python voxangel.py <level> <delay_in_ms> <channel> <host> <port> <device>
----------------------------------------------------------------------------


      <level> is the VOX threshold expressed as an integer
      corresponding to percent of maximum possible loudness
           (5 is probably a good value).


      <delay_in_ms> is delay for VOX to turn off in milliseconds.


      <channel> is the listen channel.
           0 = left, 1 = right, 2 = stereo


      <host> is the hostname or IP address of the SDRAngel server.
           (usually 127.0.0.1)


      <port> is the port of the SDRAngel server (usually 8091).


      <device> is the SDRAngel device number of the device to control.


----------------------------------------------------------------------------


Requirements:

Python 2.7 (tested on both Ubuntu 18.04 and Windows 7; should work on any operating system that supports PortAudio)

Python modules (install using pip):
      * pyaudio
      * audioop
      * numpy
      * (standard modules including os, sys, mah, datetime, httplib, socket, json).
      
To use voxangel, you will need to loop audio into your microphone jack if you are using digital mode software (e.g. fldigi or wsjtx).
You can do this in Windows using Virtual Audio Cable ( see: https://www.vb-audio.com/Cable/)
and in Linux using Pulse and pavucontrol (once voxangel appears as a recording device, set it to use "monitor").

Of course you can also use a "real" microphone (for real voice-activated switching).


Instructions:

1. Open SDRAngel and set up your sink device, channel plug-in, etc.

2. Make sure audio settings are correct (e.g. audio loopback).

3. Start voxangel



