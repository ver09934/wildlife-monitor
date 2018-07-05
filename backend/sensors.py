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
- PIR Sensor connected to GND, +5V, and Pin (TODO) (regulates 5V power to a 3.3V logic level for the signal)
- Barometric pressure sensor connected to (TODO)
- Raspi camera module connected to the camera connector slot

Notes:
- To make a python script executable: put "#!/usr/bin/env python" (no quotes) at the top, and of course, run chmod +x filename.py
- Take still shot w/ camera in bash: raspistill -o cam.jpg
- If using external battery, create a separate script to run at boot that monitors battery voltage and creates alert (text/email?) on low battery using a voltage sensor on a gpio pin

TODO:
- Baro reading with I2C
- Check at end of loop: If ~/.sensors-running contains 0 instead of 1 (writes 1 at startup), then break main loop and run GPIO.cleanup()

'''

import RPi.GPIO as GPIO
import time
import subprocess

# Set initial sensor state
state=False
if GPIO.input(17):
	state=True

# TODO: Figure out how to gracefully exit this loop externally to un 
while True:

	# If state changes from low to high
	if state == False and GPIO.input(17):
    
		state=True
		print("State changed to high")

		cmd = "raspistill -o ~/Pictures/test" + str(picCount) + ".jpg" # TODO: Can this be run as a background task so we don't have to wait for it?
		print(cmd)

		# subprocess.Popen(cmd)

		# subprocess.check_output(['bash','-c', cmd])

		subprocess.check_output(cmd, shell=True)

		picCount += 1

	# If state changes from high to low
	if state == True and (not GPIO.input(17)):
    
		state=False
		print("State changed to low")

	# Looptime (time between PIR reads) assuming no sensor activity
	time.sleep(0.1)




