# external modules
import RPi.GPIO as GPIO
import time
import subprocess
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
import atexit # For exit handling
import threading
import queue
import datetime
import xml.etree.ElementTree as ElementTree
import imutils
import cv2
import warnings

# custom modules
import MPL3115A2 as baro
from lameXMLFormatter import *

# To ignore warnings from PiCamera that it is "using alpha-stripping to convert to non-alpha format"
warnings.filterwarnings("ignore")

# Define pins
LED_PIN = 4

 # Data parameters
TMP_DATA_DIR = '../tmpdata' # Needs '/' at the end
DATA_DIR = '../data/' # Needs '/' at the end
VIDEO_SUBDIR = 'videos/' # Needs '/' at the end
DATALOG_SUBDIR = 'datalogs/' # Needs '/' at the end
INFO_FILE = '../info.xml'
PREVIEW_IMG = 'preview-img.jpg'

# OpenCV parameters
MIN_MOTION_FRAMES = 10
MIN_NOMOTION_FRAMES = 10
DELTA_THRESH = 5
CVRES = [640, 480]
CV_FPS = 25
MIN_AREA = 700

# Camera parameters
HIGHRES = [1280, 960]
LOWRES = [640, 480]
CAM_FPS = 25

tree = ElementTree.parse(INFO_FILE)
root = tree.getroot()
info = {}
for child in root:
    info[child.tag] = child.text

# insure server data dir ends with "/"
if not info['serverdatadir'].endswith('/'):
    info['serverdatadir'] += '/'

if 'sshid' in info:
    key_addition = "-e " + str(info['sshid']) + " "
else:
    key_addition = ""

CP_CMD = 'cp ' + INFO_FILE + ' ' + DATA_DIR
SYNC_CMD = "rsync -az --delete --exclude '*.h264' --exclude '.*' " + key_addition + DATA_DIR + " " + info['serveruser'] + "@" + info['serverdomain'] + ":" + info['serverdatadir'] + info['name']
CONVERT_CMD = "bash videoconvert.sh " + DATA_DIR + VIDEO_SUBDIR

# --- Define semaphores, events, locks, queues, etc. here so they don't have to be passed to methods as arguments ---

# events
motionStart = threading.Event() # Set during motion, clear when no motion
motionEnd = threading.Event() # Set when no motion, clear during motion
minutely = threading.Event() # Set and immediately cleared every minute
sync = threading.Event() # Set when the remote files should be synchronized
vidconvert = threading.Event() # Set when the video conversion should run

# queues
timeQueue = queue.Queue() # To insure video + xml files have corresponding filenames

# locks
baroLock = threading.Lock()

# setup camera, GPIO, and start threads
def main():

    # Create camera object
    camera = PiCamera()
    camera.resolution = tuple(HIGHRES)
    camera.framerate = CV_FPS

    # Setup GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

    # Create data directories
    mkdir(DATA_DIR)
    mkdir(DATA_DIR + VIDEO_SUBDIR)
    mkdir(DATA_DIR + DATALOG_SUBDIR)

    # copy xml info file into data dir
    subprocess.Popen(CP_CMD, shell=True, stdout=subprocess.DEVNULL).wait()

    # Register exit handler method
    atexit.register(exit_handler, camera)

    # Start threads
    threads = []
    threads.append(threading.Thread(target=timerThread))
    threads.append(threading.Thread(target=motionThread, args=(camera,)))
    threads.append(threading.Thread(target=cameraRecordThread, args=(camera,))) # Need the "," to make it a list
    threads.append(threading.Thread(target=dataMotionThread))
    threads.append(threading.Thread(target = dataIntervalThread, args=(camera,)))
    threads.append(threading.Thread(target = videoconvertThread))
    threads.append(threading.Thread(target = filesyncThread))

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
            
def timerThread():
    
    print("--- Timer Thread Started ---")
    
    minFreq = 1
    locker = False
    
    while True:
    
        x = datetime.datetime.now()
        second = x.second
        minute = x.minute
        
        if second == 0 and minute % minFreq == 0 and locker == False:
            locker = True
            minutely.set()
            # minutely.clear() # Let the waiting thread clear instead
        
        elif second != 0:
            locker = False
        
        time.sleep(0.001)

# when motion is detected (based off PIR and camera stream), set the motion detected event, which other threads are listening for
def motionThread(cameraIn):

    print('--- Motion Detection Thread Started ---')

    rawCapture = PiRGBArray(cameraIn, size=tuple(CVRES))
    time.sleep(0.2)
    
    avg = None

    motionCounter = 0
    noMotionCounter = 0

    motionDetected = False    

    # If neccesary: ...use_video_port=True, splitter_port=3, resize=tuple(CVRES)...
    for f in cameraIn.capture_continuous(rawCapture, format="bgr", use_video_port=True, resize=tuple(CVRES)):
        
        # grab raw numpy array representing image
        frame = f.array

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if average frame is None, initialize it
        if avg is None:
            avg = gray.copy().astype("float")
            rawCapture.truncate(0)
            continue

        # accumulate weighted average between current frame and previous frames, then compute difference between current frame and running average
        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

        # threshold delta image, dilate thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, DELTA_THRESH, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if imutils.is_cv2():
            cnts = cnts[0]
        else:
            cnts = cnts[1]

        # whether the current frame has motion
        currentMotion = False

        # loop over contours - if contour large enough, draw contour's bounding box, update currentMotion state
        for c in cnts:
            if cv2.contourArea(c) >= MIN_AREA:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                currentMotion = True

        # if frame has motion
        if currentMotion:
            noMotionCounter = 0
            motionCounter += 1

            # check to see if the number of frames with consistent motion is high enough
            if motionCounter >= MIN_MOTION_FRAMES:

                if (motionDetected == False):
                    motionDetected = True

                    GPIO.output(LED_PIN, GPIO.HIGH)
                    print("\nMotion event detected...")

                    motionEnd.clear()
                    motionStart.set()

                motionCounter = 0

        # otherwise, frame has no motion
        else:
            motionCounter = 0
            noMotionCounter += 1

            if noMotionCounter >= MIN_NOMOTION_FRAMES:

                if (motionDetected == True):
                    motionDetected = False
                    
                    GPIO.output(LED_PIN, GPIO.LOW)
                    print("Motion event completed...")
            
                    motionStart.clear()
                    motionEnd.set()

                noMotionCounter = 0

        # clear the stream in preparation for next frame
        rawCapture.truncate(0)

# record data when motion is detected (waits for lock on baro), higher priority than dataIntervalThread
# Creates a separate file for each event, with name corresponding to the created video file
def dataMotionThread():
   
    print("--- Motion Trigger Data Thread Started ---")
    
    while True:
        
        motionStart.wait()

        startTime = time.time()
                
        # See "Mapping Types - dict" in the python3 documentation
        data = {}
        
        # Run the two calls to time.strftime at the same time, so the times are the same (excluding the unlikely border condition)
        # TODO: Figure out a way to create a time object for the specific time, and then call strftime using that twice, to avoid border condition
        data['time'] = time.strftime('%m/%d/%Y %H:%M:%S %Z')
        timeString = time.strftime('%Y-%m-%d-%H-%M-%S')
        
        dataPath = DATA_DIR + VIDEO_SUBDIR + 'data_' + timeString + '.xml'
        # Send filename to video thread, so they are guaranteed to match
        timeQueue.put(timeString)
        
        baroLock.acquire()
        baroData = baro.getData()
        baroLock.release()
        
        data['pressure'] = baroData[0]
        data['temperature'] = baroData[1]
        
        fields = ['time', 'pressure', 'temperature']
        values = [data['time'], data['pressure'], data['temperature']]
        
        createFile(dataPath, 'data') # 'data' is a string, not the variable data
        appendFileChildren(dataPath, 'row', fields, values)
        
        motionEnd.wait()

        endTime = time.time()
        diff = round(endTime - startTime, 3)
        diffStr = str(datetime.timedelta(seconds=diff))
        appendFile(dataPath, 'length', diffStr, True)

# record data at regular interval (waits for lock on baro)
def dataIntervalThread(cameraIn):
   
    print("--- Regular Interval Data Thread Started ---")
    
    while True:
      
        # Log data to file

        filePath = DATA_DIR + DATALOG_SUBDIR + 'current_log-' + time.strftime('%Y-%m-%d') + '.xml'
        if not os.path.isfile(filePath):
            createFile(filePath, 'data')

        minutely.wait()
        minutely.clear()

        baroLock.acquire()
        baroData = baro.getData()
        baroLock.release()

        data = {}
        # See "Mapping Types - dict" in the python3 documentation
        data['time'] = time.strftime('%m/%d/%Y %H:%M:%S %Z')
        data['pressure'] = baroData[0]
        data['temperature'] = baroData[1]

        fields = ['time', 'pressure', 'temperature']
        values = [data['time'], data['pressure'], data['temperature']]
        appendFileChildren(filePath, 'row', fields, values)

        # Take minutely image, overwriting previous image

        imgPath = DATA_DIR + PREVIEW_IMG
        cameraIn.capture(imgPath, resize=tuple(LOWRES))

        sync.set()

def cameraRecordThread(cameraIn):
        
    print("--- Motion Camera Thread Started ---")

    while True:
        
        motionStart.wait()
        
        timeString = timeQueue.get() # get timeString from motion data thread
        
        videoPath = DATA_DIR + VIDEO_SUBDIR + 'video_' + timeString + '.h264'
        
        cameraIn.start_recording(videoPath, splitter_port=2)
        print("Recording start...")

        motionEnd.wait()
        
        cameraIn.stop_recording(splitter_port=2)
        print("Recording end...")
  
        vidconvert.set()
        
def videoconvertThread():
    
    print("--- Video Conversion Thread Started ---")
    
    while True:
        
        vidconvert.wait()
        sp = subprocess.Popen(CONVERT_CMD, shell=True, stdout=subprocess.DEVNULL)
        sp.wait()
        vidconvert.clear()

        sync.set()
        
def filesyncThread():

    print("--- Filesync Thread Started ---")
      
    while True:
        
        sync.wait()
        print("- Started sync -")
        sp = subprocess.Popen(SYNC_CMD, shell=True, stdout=subprocess.DEVNULL)
        sp.wait()
        print("- Ended sync -")
        sync.clear()

# Watch disk space and pure local logs / recordings if neccesary
def fileManagementThread():

    print("--- File Management Thread Started ---")
    
    while True:
        time.sleep(1)

def exit_handler(cameraIn):
    print("Exiting...")
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
    if motionStart.is_set():
        cameraIn.stop_recording(splitter_port=2)
    cameraIn.close()
    print("Finished cleanup.")

if __name__ == '__main__':
    main()
