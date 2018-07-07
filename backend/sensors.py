'''
Structure:
- read the PIR sensor
- if (PIR Condition)
  - record start time
  - start camera recording for set time or until PIR signal drops to low for more than a few seconds
  - take baro reading every n seconds, average at end of camera period
  - (potentially) record end time
- sleep (set time) - or use watchdog timer/interrupt pin for lower power / faster response...

PIR Condition:
- PIR has been low for at least 10 seconds
- PIR has been high for at least 1 second (assuming time the output signal stays high when object is detected is only when there is active motion)
- TODO: Improve this filtering system

PINOUT:
- PIR Sensor (with retriggering enabled) connected to GND, +5V, and Signal to BCM 17 (it regulates 5V power to a 3.3V logic level for the signal)
- Barometric pressure sensor connected to +3.3V (or +5V), GND, BCM 2 (SDA - I2C Data), and BCM 3 (SCL - I2C Clock)
- Raspi camera module connected to the camera connector slot
- (Optional) Motion indicator LED connected to GND and BCM 4 with a 100 ohm resistor 

TODO:
- Check at end of loop: If ~/.sensors-running contains 0 instead of 1 (writes 1 at startup), then break main loop and run GPIO.cleanup(), or come up with some other way to cleanl break from the main loop
- Decide if the data file should be created when motion is detectd and filled with instantaneous data, or if the file should be created when the motion is stopped, and filled wih averaged data over the period of motion... (simpler is better, for now - multithreading can come later)
- To convert vars to strings, use str(var)
- May have separate directories for the data and videos, or else a separate dir for each instance, each containing one video and file... whatever makes the php easier, unil I can learn SQL
- Test importing the MPL file and create methods to call (setup on import, with data method, and the potential to re-call the setup method)

'''

import RPi.GPIO as GPIO
import time
#import subprocess
import os
from picamera import PiCamera
import smbus
import json
import MPL3115A2 as baro

DATA_DIR = '/home/pi/wildlife-files/' # Needs '/' at the end, and '~/wildlife-files' didn't work...
PIR_PIN = 17
LED_PIN = 4

def mkdir(pathIn):
	if os.path.exists(pathIn):
		print("Directory exists: " + os.path.abspath(pathIn))
	else:
		try:
			os.mkdir(pathIn)
			print("Created directory: " + os.path.abspath(pathIn))
		# except Exception as e: print(e)
		except:
			print("Could not create directory: " + pathIn)

def setup():

	# Create camera object (needs to be accessible from main method)
	global camera
	camera = PiCamera()

	# Count number of times the PIR has triggered to high
	global triggerCount
	triggerCount = 1

	# Setup GPIO pins
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIR_PIN, GPIO.IN)
	GPIO.setup(LED_PIN, GPIO.OUT)

	# Create data directory
	mkdir(DATA_DIR)

def main():

	setup()

	# Set initial motion state
	motionDetected = False

	while True:

		# --- If state changes from low to high ---
		if motionDetected == False and GPIO.input(PIR_PIN):

			timeString = time.strftime('%Y-%m-%d-%H-%M-%S')
			videoPath = DATA_DIR + 'video_' + timeString + '.h264'
			dataPath = DATA_DIR + 'data_' + timeString + '.json'

			motionDetected = True
			print("State changed to high")
			GPIO.output(LED_PIN, GPIO.HIGH)

			global camera
			camera.start_recording(videoPath)

			global triggerCount
			triggerCount += 1

			baroData = baro.getData()

			data = {}
			data['time'] = time.strftime('%m/%d/%Y %H:%M:%S %Z')
			data['pressure'] = baroData[0]
			data['temperature'] = baroData[1]

			try:
				with open(dataPath, 'w+') as f: # f = open(dataPath, 'w+')
					json.dump(data, f, ensure_ascii=False, indent=2)
					f.write('\n')
					f.close()
			except:
				print("Could not create file: " + dataPath)

		# --- If state changes from high to low ---
		if motionDetected == True and (not GPIO.input(PIR_PIN)):

			motionDetected = False
			print("State changed to low")
			GPIO.output(LED_PIN, GPIO.LOW)

			global camera
			camera.stop_recording()

			# TODO: Start thread to convert h264 stream to mp4 (likely calling a bash script)

		time.sleep(0.01) # Looptime if no sensor activity

	# if we break from the loop... somehow
	GPIO.cleanup()




main()
