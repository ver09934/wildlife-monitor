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
- Check at end of loop: If ~/.sensors-running contains 0 instead of 1 (writes 1 at startup), then break main loop and run GPIO.cleanup()

'''

import RPi.GPIO as GPIO
import time
import subprocess
from picamera import PiCamera
import smbus

dataDir = "~/wildlife_videos/" # Needs '/' at the end
pirPin = 17
ledPin = 4

def mkdir(pathIn):
    if not os.path.exists(pathIn):
        print('Directory exists: ' + os.path.abspath(pathIn))
    else:
		try:
			os.mkdir(pathIn)
			print('Created directory: ' + os.path.abspath(pathIn))
		except:
			print('Could not create directory: ' + pathIn)

def setup():
	
	# Create camera object (needs to be accessible from main method)
	global camera = PiCamera()
	
	# Count number of videos recorded
	# Alternatively, timestamp the video names
	global vidCount = 1

	# Setup GPIO pins
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pirPin, GPIO.IN)
	GPIO.setup(ledPin, GPIO.OUT)
	
	# Setup I2C bus (TODO)
	
	# Create data directory
	mkdir(dataDir)
	
def main():
	
	setup()
	
	# Set initial motion state
	motionDetected = False
	
	while True:

		# --- If state changes from low to high ---
		if motionDetected == False and GPIO.input(pirPin):
			
			motionDetected = True
			print("State changed to high")
			GPIO.output(ledPin, GPIO.HIGH)
			camera.start_recording(dataDir + 'video_capture_' + str(vidCount) + '.')
			vidCount += 1

		# --- If state changes from high to low ---
		if motionDetected == True and (not GPIO.input(pirPin)):
			
			motionDetected = False
			print("State changed to low")
			GPIO.output(ledPin, GPIO.LOW)
			camera.stop_recording()
			# TODO: Start backgroun task to convert h264 stream to mp4

		time.sleep(0.01) # Looptime if no sensor activity
		
	# if we break from the loop... somehow
	GPIO.cleanup()

main()
