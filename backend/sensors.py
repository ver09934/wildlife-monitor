# Note: To make a python script executable: put "#!/usr/bin/env python" (no quotes) at the top, and of course, run chmod +x filename.py

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

- If using external battery, create a separate script to run at boot that monitors battery voltage and creates alert (text/email?) on low battery using a voltage sensor on a gpio pin

- Take still shot w/ camera in bash: raspistill -o cam.jpg

PINOUT:
- PIR Sensor connected to GND, +5V, and Pin (TODO) (regulates 5V power to a 3.3V logic level for the signal)
- Barometric pressure sensor connected to (TODO)
- Raspi camera module connected to the camera connector slot

'''


