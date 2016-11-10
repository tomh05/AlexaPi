import RPi.GPIO as GPIO
import time
import random

_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}

def rgb(triplet):
	return _HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]]


class RgbLed:
	def __init__(self,redPin,greenPin,bluePin, freq):
		self.pins = [redPin,greenPin,bluePin]
		self.freq = freq

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pins, GPIO.OUT)
		GPIO.output(self.pins, GPIO.LOW)
		
		self.r = GPIO.PWM(self.pins[0],self.freq)
		self.g = GPIO.PWM(self.pins[1],self.freq)
		self.b = GPIO.PWM(self.pins[2],self.freq)

		self.r.start(0)
		self.g.start(0)
		self.b.start(0)

	def setRGB(self,rVal,gVal,bVal):
		self.r.ChangeDutyCycle(rVal/2.55)
		self.g.ChangeDutyCycle(gVal/2.55)
		self.b.ChangeDutyCycle(bVal/2.55)

	def setHex(self,hex):
		self.setRGB(*rgb(hex))

if __name__ == "__main__":
	led = RgbLed(14,15,18,200)
	while True:
		r = random.randrange(255)
		g = random.randrange(255)
		b = random.randrange(255)
		led.setRGB(r,g,b)
		time.sleep(.5)
