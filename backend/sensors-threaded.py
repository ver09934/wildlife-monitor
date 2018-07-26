import RPi.GPIO as GPIO
import time
import subprocess
import os
from picamera import PiCamera
import smbus
import json
import atexit # For exit handling
import MPL3115A2 as baro

import threading

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
    
    # motion events
    motionStart = threading.Event()
    motionEnd = threading.Event()

    # Start threads    
    threads = []
    threads.append(threading.Thread(target = motionThread, args=(motionStart, motionEnd)))
    threads.append(threading.Thread(target = cameraRecordThread, args=(camera, motionStart, motionEnd)))
    # threads.append(threading.Thread(target = dataThread))
    # threads.append(threading.Thread(target = cameraStreamThread))
    
    for thread in threads:
        thread.start()

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

def dataThread():
    
    while True:
        
        baroData = baro.getData()
        data = {}
        data['time'] = time.strftime('%m/%d/%Y %H:%M:%S %Z')
        data['pressure'] = baroData[0]
        data['temperature'] = baroData[1]
        
        timeString = time.strftime('%Y-%m-%d-%H-%M-%S')
        dataPath = DATA_DIR + 'data_' + timeString + '.json'
        
        try:
            with open(dataPath, 'w+') as f: # f = open(dataPath, 'w+')
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
                f.close()
        except:
            print("Could not create file: " + dataPath)
        
        time.sleep(5)
    
def motionThread(motionEvent, motionEventComplete):
    
    motionDetected = false
    triggerCount = 0
    
    while True:
        
        # If state changes from low to high
        if motionDetected == False and GPIO.input(PIR_PIN):
            
            motionDetected = True
            triggerCount += 1
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("Motion event detected...")
            
            motionEvent.set()
            
        # If state changes from high to low
        if motionDetected == True and (not GPIO.input(PIR_PIN)):
            
            motionDetected = False
            GPIO.output(LED_PIN, GPIO.LOW)
            print("Motion event completed...")
            
            motionEventComplete.set()

def cameraStreamThread(cameraIn):
                
    stream_pipe = subprocess.Popen(STREAM_CMD, shell=True, stdin=subprocess.PIPE)

    print("Starting streaming...")
    cameraIn.start_recording(stream_pipe.stdin, format='h264', resize=(LOWRES_VERT, LOWRES_HORIZ))

    while True:
        cameraIn.wait_recording(1)

def cameraRecordThread(cameraIn, motionEvent, motionEventComplete):
        
    while True:
        
        motionEvent.wait()
        
        timeString = time.strftime('%Y-%m-%d-%H-%M-%S')
        videoPath = DATA_DIR + 'video_' + timeString + '.h264'
        
        print("Recording start...")
        cameraIn.start_recording(videoPath, splitter_port=2)
        
        motionEvent.clear()
        motionEventComplete.wait()
        
        cameraIn.stop_recording(splitter_port=2)
        print("Recording end...")
        
        motionEventComplete.clear()
        
        subprocess.Popen(CONVERT_CMD, shell=True)

def exit_handler(cameraIn):
    print("Exiting...")
    cameraIn.stop_recording()
    cameraIn.stop_recording(splitter_port=2)
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()

if __name__ == '__main__':
    main()
