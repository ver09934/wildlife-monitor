# external modules
import RPi.GPIO as GPIO
import time
import subprocess
import os
from picamera import PiCamera
import atexit # For exit handling
import threading
import queue
import datetime
import xml.etree.ElementTree as ElementTree

# custom modules
import MPL3115A2 as baro
from lameXMLFormatter import *

PIR_PIN = 17
LED_PIN = 4

DATA_DIR = '../data/' # Needs '/' at the end
VIDEO_SUBDIR = 'videos/' # Needs '/' at the end
DATALOG_SUBDIR = 'datalogs/' # Needs '/' at the end
INFO_FILE = '../info.xml'
PREVIEW_IMG = 'preview-img.jpg'

tree = ElementTree.parse(INFO_FILE)
root = tree.getroot()
info = {}
for child in root:
    info[child.tag] = child.text

# insure server data dir ends with "/"
if not info['serverdatadir'].endswith('/'):
    info['serverdatadir'] += '/'

CP_CMD = 'cp ' + INFO_FILE + ' ' + DATA_DIR
SYNC_CMD = "rsync -az --delete --exclude '*.h264' --exclude '.*' " + DATA_DIR + " " + info['serveruser'] + "@" + info['serverdomain'] + ":" + info['serverdatadir'] + info['name']
CONVERT_CMD = "bash videoconvert.sh " + DATA_DIR + VIDEO_SUBDIR

HIGHRES_VERT = 1280
HIGHRES_HORIZ = 720
LOWRES_VERT = 640
LOWRES_HORIZ = 360
CAM_FPS = 25

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
    camera.resolution = (HIGHRES_VERT, HIGHRES_HORIZ)
    camera.framerate = CAM_FPS

    # Setup GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)
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
    threads.append(threading.Thread(target=motionThread))
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
def motionThread():
    
    print('--- Motion Detection Thread Started ---')

    motionDetected = False
    triggerCount = 0
    
    motionEnd.set()

    # Give all the threads time to start
    time.sleep(1)
 
    while True:
        
        # If state changes from low to high
        if motionDetected == False and GPIO.input(PIR_PIN):
            
            motionDetected = True
            triggerCount += 1
            GPIO.output(LED_PIN, GPIO.HIGH)
            print() # print('\n', end='')
            print("Motion event detected...")
            
            motionEnd.clear()
            motionStart.set()
            
        # If state changes from high to low
        if motionDetected == True and (not GPIO.input(PIR_PIN)):
            
            motionDetected = False
            GPIO.output(LED_PIN, GPIO.LOW)
            print("Motion event completed...")
            
            motionStart.clear()
            motionEnd.set()

        time.sleep(0.001)

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
        cameraIn.capture(imgPath, resize=(LOWRES_VERT, LOWRES_HORIZ))

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
        sync.set()
        
def videoconvertThread():
    
    print("--- Video Conversion Thread Started ---")
    
    while True:
        
        vidconvert.wait()
        sp = subprocess.Popen(CONVERT_CMD, shell=True, stdout=subprocess.DEVNULL)
        sp.wait()
        vidconvert.clear()
        
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
