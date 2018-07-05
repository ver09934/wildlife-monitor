import RPi.GPIO as GPIO
import time
import subprocess

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.setup(4, GPIO.OUT)

picCount = 1

GPIO.output(4, GPIO.LOW)
state=False
if GPIO.input(17):
	state=True
	GPIO.output(4, GPIO.HIGH)

while True:

	if state == False and GPIO.input(17):
		state=True
		print("State changed to high")
		GPIO.output(4, GPIO.HIGH)

	if state == True and (not GPIO.input(17)):
		state=False
		print("State changed to low")
		GPIO.output(4, GPIO.LOW)

	time.sleep(0.1)

