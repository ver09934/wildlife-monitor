import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

while True:

	if GPIO.input(17):
		print("HIGH")
	else:
		print("low")

	time.sleep(0.1)

# https://pinout.xyz - BCM 17 is pin 11

# GPIO.cleanup()
