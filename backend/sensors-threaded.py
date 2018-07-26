import RPi.GPIO as GPIO
import time
import subprocess
import os
from picamera import PiCamera
import smbus
import json
import atexit # For exit handling
import MPL3115A2 as baro

DATA_DIR = '../data/' # Needs '/' at the end
PIR_PIN = 17
LED_PIN = 4

CONVERT_CMD = "bash videoconvert.sh " + DATA_DIR
YOUTUBE="rtmp://a.rtmp.youtube.com/live2/"
KEY = "" # Assigned in setup method
STREAM_CMD = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE + KEY

HIGHRES_VERT = 1280
HIGHRES_HORIZ = 720
LOWRES_VERT = 480
LOWRES_HORIZ = 360
CAM_FPS = 25

# For creating directories
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

# Declare global variables, setup GPIO pins
def setup():

    # Create camera object (needs to be accessible from main method)
    global camera
    camera = PiCamera()
    camera.resolution = (HIGHRES_VERT, HIGHRES_HORIZ)
    camera.framerate = CAM_FPS

    # Count number of times the PIR has triggered to high
    global triggerCount
    triggerCount = 1

    # Whether motion is detected - set inition motion state
    global motionDetected
    motionDetected = False

    # Setup GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)
    GPIO.setup(LED_PIN, GPIO.OUT)

    # Create data directory
    mkdir(DATA_DIR)

    # Register exit handler method
    atexit.register(exit_handler)
    
    # get youtube streaming key from yt-stream-key.txt
    global KEY
    f = open("yt-stream-key.txt", "r")
    if f.mode == 'r':
        KEY = f.read()

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
    
def motionThread():
    
    # Global variables
       global motionDetected
    global triggerCount
    
    while True:
        
        # If state changes from low to high
        if motionDetected == False and GPIO.input(PIR_PIN):
            motionDetected = True
            triggerCount += 1
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("Motion event detected...")
            
        # If state changes from high to low
        if motionDetected == True and (not GPIO.input(PIR_PIN)):
            motionDetected = False
            GPIO.output(LED_PIN, GPIO.LOW)
            print("Motion event completed...")

def cameraStreamThread():
    
    global camera
            
    stream_pipe = subprocess.Popen(STREAM_CMD, shell=True, stdin=subprocess.PIPE)

    print("Starting streaming...")
    camera.start_recording(stream_pipe.stdin, format='h264', resize=(LOWRES_VERT, LOWRES_HORIZ))

    while True:
        camera.wait_recording(1)

def cameraRecordThread():
    
    global camera
    
    while True:
        
        timeString = time.strftime('%Y-%m-%d-%H-%M-%S')
        videoPath = DATA_DIR + 'video_' + timeString + '.h264'
        
        print("Recording start...")
        camera.start_recording(videPath, splitter_port=2)
        camera.wait_recording(5)
        camera.stop_recording(splitter_port=2)
        print("Recording end...")
        
        subprocess.Popen(CONVERT_CMD, shell=True)

        time.sleep(50)

def main():

    # Run setup function
    setup()

    # Start threads
    
    threads = []
    # threads.append(threading.Thread(target = dataThread))
    threads.append(threading.Thread(target = motionThread))
    # threads.append(threading.Thread(target = cameraStreamThread))
    threads.append(threading.Thread(target = cameraRecordThread))
    
    for thread in threads:
        thread.start()

# Could use try/catch
def exit_handler():
    print("Exiting (somewhat) gracefully...")
    if motionDetected == True and (not GPIO.input(PIR_PIN)):
        print("Doing cleanup...")
        GPIO.output(LED_PIN, GPIO.LOW)
        global camera
        camera.stop_recording()
        cmd="bash videoconvert.sh " + DATA_DIR
        subprocess.Popen(cmd, shell=True)
    GPIO.cleanup()

main()
