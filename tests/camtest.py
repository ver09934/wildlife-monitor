import RPi.GPIO as GPIO
import time
import subprocess

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

picCount = 1

state=False
if GPIO.input(17):
	state=True

while True:

	if state == False and GPIO.input(17):
		state=True
		print("State changed to high")

		cmd = "raspistill -o ~/Pictures/test" + str(picCount) + ".jpg"
		print(cmd)

		# subprocess.Popen(cmd)

		# subprocess.check_output(['bash','-c', cmd])

		subprocess.check_output(cmd, shell=True)

		picCount += 1

	if state == True and (not GPIO.input(17)):
		state=False
		print("State changed to low")

	time.sleep(0.1)

# https://pinout.xyz - BCM 17 is pin 11

# GPIO.cleanup()

'''
import subprocess
subprocess.Popen("cwm --rdf test.rdf --ntriples > test.nt")
raspistill -o test3.jpg
'''
