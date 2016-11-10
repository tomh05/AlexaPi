#! /usr/bin/env python

import os
import random
import time
import alsaaudio
import pyaudio
import wave
import random
from creds import *
import requests
import json
import re
import rgbled
from memcache import Client
import speech_recognition as sr

#Settings
device = "plughw:0" # Name of your microphone/soundcard in arecord -L
led = rgbled.RgbLed(14,15,18,200)

#Setup
recorded = False
servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))

colReady = '000811'
colSuccess = '00ff33'
colError = 'ff0000'
colListening = 'ff00ff'
colSpeaking = '0099ff'
colThinking = '5500b3'

lastEnergy = 0

def energyCallback(energy):
	global lastEnergy
	energy /= 10.0
	energy += 30
	if energy < 0:
		energy = 0
	if energy > 100:
		energy = 100
	smoothedEnergy = max(energy,lastEnergy)
	lastEnergy = energy
	led.setRGB(smoothedEnergy,0,smoothedEnergy);


def internet_on():
    print "Checking Internet Connection"
    try:
        r =requests.get('https://api.amazon.com/auth/o2/token')
	print "Connection OK"
        return True
    except:
	print "Connection Failed"
    	return False

	
def gettoken():
	token = mc.get("access_token")
	refresh = refresh_token
	if token:
		return token
	elif refresh:
		payload = {"client_id" : Client_ID, "client_secret" : Client_Secret, "refresh_token" : refresh, "grant_type" : "refresh_token", }
		url = "https://api.amazon.com/auth/o2/token"
		r = requests.post(url, data = payload)
		resp = json.loads(r.text)
		mc.set("access_token", resp['access_token'], 3570)
		return resp['access_token']
	else:
		return False
		

def playWav(path):
	chunkSize = 1024
	waveform = wave.open(path,'rb')
	pyAudio = pyaudio.PyAudio()
	stream = pyAudio.open(format = pyAudio.get_format_from_width(waveform.getsampwidth()),
					channels = waveform.getnchannels(),
					rate = waveform.getframerate(),
					output = True)
	data = waveform.readframes(chunkSize)
	while data != '':
		stream.write(data)
		data = waveform.readframes(chunkSize)
	stream.stop_stream()
	stream.close()
	pyAudio.terminate()

def alexa():
	print "Alexa function"

	url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
	headers = {'Authorization' : 'Bearer %s' % gettoken()}
	d = {
   		"messageHeader": {
       		"deviceContext": [
           		{
               		"name": "playbackState",
               		"namespace": "AudioPlayer",
               		"payload": {
                   		"streamId": "",
        			   	"offsetInMilliseconds": "0",
                   		"playerActivity": "IDLE"
               		}
           		}
       		]
		},
   		"messageBody": {
       		"profile": "alexa-close-talk",
       		"locale": "en-us",
       		"format": "audio/L16; rate=16000; channels=1"
   		}
	}
	with open(path+'recording.wav') as inf:
		files = [
				('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
				('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
				]	
		r = requests.post(url, headers=headers, files=files)

	print "status code is"
	print r.status_code
	if r.status_code == 200:
		print r.headers
		with open("dump", "wb") as fh:
			fh.write( r.content )
		for v in r.headers['content-type'].split(";"):
			if re.match('.*boundary.*', v):
				boundary =  v.split("=")[1]
		data = r.content.split(boundary)
		for d in data:
			if (len(d) >= 1024):
				audio = d.split('\r\n\r\n')[1].rstrip('--')
		if audio:
			with open(path+"response.mp3", 'wb') as f:
				f.write(audio)

		led.setHex(colSpeaking)

		print 'playing response'
		#os.system('mpg123 -q {}response.mp3'.format(path))
		os.system('mpg123 -q -w {}response.wav {}response.mp3'.format(path,path))
		playWav(path+'response.wav')
		led.setHex(colReady)
	else:
		playWav(path+'error.wav')
		for x in range(0, 3):
			led.setHex(colError)
			time.sleep(.2)
			led.setHex(colReady)
			time.sleep(.1)
		

def startRecog():
	r = sr.Recognizer()
	while True:
		print 'Listening out for keyphrase'
		gotKeyphrase = r.wait_for_keyphrase('alexa','1e-50')

		'''
		with sr.Microphone() as source:
			print ("say something")
			audio = r.listen(source,energyCallback)
			print ("finished listening")
		gotKeyphrase= False
		# recognize speech using Sphinx
		try:
			gotKeyphrase = r.match_keyphrase_sphinx(audio, "alexa","10e-10")
		except sr.UnknownValueError:
			print("Sphinx could not understand audio")
		except sr.RequestError as e:
			print("Sphinx error; {0}".format(e))

		'''
		if gotKeyphrase:
			print "Keyphrase found. Start recording ..."

			led.setHex(colListening)
			print ("say something")
			playWav(path+'bing1.wav')
			with sr.Microphone() as source:
				audio = r.listen(source,energyCallback)
			playWav(path+'bing2.wav')
			led.setHex(colThinking)
			print ("finished listening")

			rf = open(path+'recording.wav', 'w')
			rf.write(audio.get_wav_data())
			rf.close()
			alexa()
		else:
			print "no keyphrase detected"
		
	

if __name__ == "__main__":
	led.setHex(colThinking)
	
	while internet_on() == False:
		print "."
	token = gettoken()
	#os.system('mpg123 -q {}1sec.mp3 {}hello.mp3'.format(path, path))
	for x in range(0, 3):
		time.sleep(.1)
		led.setHex(colSuccess)
		time.sleep(.1)
		led.setHex('000000')
	led.setHex(colReady)
	startRecog()
