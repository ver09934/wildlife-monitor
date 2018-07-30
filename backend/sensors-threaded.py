# external modules
import RPi.GPIO as GPIO
import time
import subprocess
import os
from picamera import PiCamera
import smbus
import json
import atexit # For exit handling
import threading

# custom modules
import MPL3115A2 as baro
from lameXMLFormatter import *

DATA_DIR = '../data/' # Needs '/' at the end
PIR_PIN = 17
LED_PIN = 4

CONVERT_CMD = "bash videoconvert.sh " + DATA_DIR
YOUTUBE="rtmp://a.rtmp.youtube.com/live2/"
with open("yt-stream-key.txt", "r") as f:
    KEY = f.read()
STREAM_CMD = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE + KEY

HIGHRES_VERT = 1280
HIGHRES_HORIZ = 720
LOWRES_VERT = 480
LOWRES_HORIZ = 360
CAM_FPS = 25

# Define semaphores, events, locks, etc. here so they don't have to be passed to methods as arguments
motionStart = threading.Event()
motionEnd = threading.Event()

# setup camera, GPIO, and start threads
def main():

    # Create camera object
    camera = PiCamera()
    camera.resolution = (HIGHRES_VERT, HIGHRES_HORIZ)
    camera.framerate = CAM_FPS

    # Setup GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)
    GPIO.setup(LED_PIN, GPIO.OUT)

    # Create data directory
    mkdir(DATA_DIR)
    
    # Register exit handler method
    atexit.register(exit_handler, camera)
    # atexit.register(goodbye, 'Donny', 'nice') # Can pass args when registering...

    # Start threads    
    threads = []
    threads.append(threading.Thread(target=motionThread))
    threads.append(threading.Thread(target=cameraRecordThread, args=(camera,))) # Need the "," to make it a list
    threads.append(threading.Thread(target=dataThread))
    # threads.append(threading.Thread(target = cameraStreamThread, args=(camera,)))
    # threads.append(threading.Thread(target = dataIntervalThread))
    
    for thread in threads:
        thread.start()

# method to make directory - give path as argument
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
  
# when motion is detected (based off PIR and camera stream), set the motion detected event, which other threads are listening for
def motionThread():
    
    motionDetected = False
    triggerCount = 0
    
    motionEnd.set()
    
    while True:
        
        # If state changes from low to high
        if motionDetected == False and GPIO.input(PIR_PIN):
            
            motionDetected = True
            triggerCount += 1
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("Motion event detected...")
            
            motionStart.set()
            motionEnd.clear()
            
        # If state changes from high to low
        if motionDetected == True and (not GPIO.input(PIR_PIN)):
            
            motionDetected = False
            GPIO.output(LED_PIN, GPIO.LOW)
            print("Motion event completed...")
            
            motionStart.clear()
            motionEnd.set()


# record data when motion is detected, higher priority than dataIntervalThread
def dataThread():
    
    filePath = DATA_DIR + 'current_log.xml'
    createFile(filePath, 'data')
    
    while True:
        
        motionStart.wait()
        
        # TODO: Get filename from motion thread, so it matches
        
        baroData = baro.getData()
        data = {}
        # See "Mapping Types - dict" in the python3 documentation
        data['time'] = time.strftime('%m/%d/%Y %H:%M:%S %Z')
        data['pressure'] = baroData[0]
        data['temperature'] = baroData[1]
        
        timeString = time.strftime('%Y-%m-%d-%H-%M-%S')
        dataPath = DATA_DIR + 'data_' + timeString + '.json'
        
        fields = ['time', 'pressure', 'temperature']
        values = [data['time'], data['pressure'], data['temperature']]
        appendFile(filePath, 'row', fields, values)        
        
        motionEnd.wait()

# record data at regular interval (data thread has priority - this thread can only grab data if dataThread does not have the lock - just write file with time and null values)
def dataIntervalThread():
    
    while True:
        time.sleep(60)

def cameraStreamThread(cameraIn):
                
    stream_pipe = subprocess.Popen(STREAM_CMD, shell=True, stdin=subprocess.PIPE)

    print("Starting streaming...")
    cameraIn.start_recording(stream_pipe.stdin, format='h264', resize=(LOWRES_VERT, LOWRES_HORIZ))

    while True:
        cameraIn.wait_recording(1)

def cameraRecordThread(cameraIn):
        
    while True:
        
        motionStart.wait()
        
        timeString = time.strftime('%Y-%m-%d-%H-%M-%S')
        videoPath = DATA_DIR + 'video_' + timeString + '.h264'
        
        print("Recording start...")
        cameraIn.start_recording(videoPath, splitter_port=2)
                
        motionEventComplete.wait()
        
        cameraIn.stop_recording(splitter_port=2)
        print("Recording end...\n")
                
        subprocess.Popen(CONVERT_CMD, shell=True)
   
'''
Threads to add:
file transfer using rsync (could just make this a cron job...)
watching disk space and purging local logs / recordings if neccesary
'''

def exit_handler(cameraIn):
    print("Exiting...")
    if motionStart.is_set():
        cameraIn.stop_recording()
        cameraIn.stop_recording(splitter_port=2)
    cameraIn.close()
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()

if __name__ == '__main__':
    main()
