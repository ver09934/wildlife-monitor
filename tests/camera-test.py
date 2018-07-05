import time
from picamera import PiCamera

camera = PiCamera()

camera.start_recording('/home/pi/video2.h264')
time.sleep(5)
camera.stop_recording()


