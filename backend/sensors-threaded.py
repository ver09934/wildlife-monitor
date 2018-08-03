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

DATA_DIR = '../data/' # Needs '/' at the end
VIDEO_SUBDIR = 'videos/' # Needs '/' at the end
DATALOG_SUBDIR = 'datalogs/' # Needs '/' at the end

PIR_PIN = 17
LED_PIN = 4

INFO_FILE = '../info.xml'

tree = ElementTree.parse(INFO_FILE)
root = tree.getroot()
info = {}
for child in root:
    info[child.tag] = child.text

# insure server data dir ends with "/"
if not info['serverdatadir'].endswith('/'):
    info['serverdatadir'] += '/'

SYNC_CMD = "rsync -az --delete --exclude '*.h264' --exclude '.*' " + DATA_DIR + " " + info['serveruser'] + "@" + info['serverdomain'] + ":" + info['serverdatadir'] + info['name']

#with open("yt-stream-key.txt", "r") as f:
#    KEY = f.read()
KEY = info['ytstreamkey']

CONVERT_CMD = "bash videoconvert.sh " + DATA_DIR + VIDEO_SUBDIR
YOUTUBE="rtmp://a.rtmp.youtube.com/live2/"
STREAM_CMD = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE + KEY

HIGHRES_VERT = 1280
HIGHRES_HORIZ = 720
LOWRES_VERT = 480
LOWRES_HORIZ = 360
CAM_FPS = 25

#print(SYNC_CMD)
#time.sleep(1000)

# Define semaphores, events, locks, queues, etc. here so they don't have to be passed to methods as arguments

# events
motionStart = threading.Event() # Set during motion, clear when no motion
motionEnd = threading.Event() # Set when no motion, clear during motion
minutely = threading.Event() # Set and immediately cleared every minute
sync = threading.Event() # Set and cleared when the remote files should be synchronized

# queues
timeQueue = queue.Queue() # To insure video + xml files have corresponding filenames

# locks
baroLock = threading.Lock()

# setup camera, GPIO, and start threads
def main():

    # ----- To move outside main -----
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
    # --------------------------------

    # Register exit handler method
    atexit.register(exit_handler, camera)
    # atexit.register(goodbye, 'Donny', 'nice') # Can pass args when registering...

    # Start threads
    threads = []
    threads.append(threading.Thread(target=timerThread))
    threads.append(threading.Thread(target=motionThread))
    threads.append(threading.Thread(target=cameraRecordThread, args=(camera,))) # Need the "," to make it a list
    threads.append(threading.Thread(target=dataMotionThread))
    # threads.append(threading.Thread(target = cameraStreamThread, args=(camera,)))
    threads.append(threading.Thread(target = dataIntervalThread))
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
            minutely.clear()
        
        elif second != 0:
            locker = False
        
        else:
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


# record data when motion is detected (waits for lock on baro), higher priority than dataIntervalThread
# Creates a separate file for each event, with name corresponding to the created video file
def dataMotionThread():
   
    print("--- Motion Trigger Data Thread Started ---")
    
    while True:
        
        motionStart.wait()
                
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
        appendFile(dataPath, 'row', fields, values)
        
        motionEnd.wait()

# record data at regular interval (waits for lock on baro)
def dataIntervalThread():
   
    print("--- Regular Interval Data Thread Started ---")
    
    # print() # print('\n', end='')
    # print("Data interval thread got lock (not really)")
    # print("Data interval thread collecting data (not really)")
    # TODO: Check if logfile already exists...
    # Idea: 1 log per day? Check if it exists, if not, make it...
    
    filePath = DATA_DIR + DATALOG_SUBDIR + 'current_log-' + time.strftime('%Y-%m-%d') + '.xml'
    if not os.path.isfile(filePath):
        createFile(filePath, 'data')
    
    while True:
            
            minutely.wait()
            
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
            appendFile(filePath, 'row', fields, values)
            
            sync.set()

def cameraStreamThread(cameraIn):
    
    print("--- Streaming Thread Started ---")

    # NOTE: If there are streaming issues and the avconv/ffmpeg output is needed, remove the stdout=subprocess.DEVNULL argument, which silences the command
    stream_pipe = subprocess.Popen(STREAM_CMD, shell=True, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)

    # print("Starting streaming...")
    cameraIn.start_recording(stream_pipe.stdin, format='h264', resize=(LOWRES_VERT, LOWRES_HORIZ))

    while True:
        cameraIn.wait_recording(1)

def cameraRecordThread(cameraIn):
        
    print("--- Motion Camera Thread Started ---")

    while True:
        
        motionStart.wait()
        
        # get timeString from motion data thread
        timeString = timeQueue.get()
        timeQueue.queue.clear() # Clear the queue, just for kicks...
        
        videoPath = DATA_DIR + VIDEO_SUBDIR + 'video_' + timeString + '.h264'
        
        print("Recording start...")
        cameraIn.start_recording(videoPath, splitter_port=2)
        
        motionEnd.wait()
        
        cameraIn.stop_recording(splitter_port=2)
        print("Recording end...")
         
        subprocess.Popen(CONVERT_CMD, shell=True, stdout=subprocess.DEVNULL)
        
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
        # This thread clears sync, since multiple other threads could set it

'''
Threads to add:
- file transfer using rsync (could just make this a cron job...)
- watching disk space and purging local logs / recordings if neccesary
'''

def exit_handler(cameraIn):
    print("Exiting...")
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
    if motionStart.is_set():
        subprocess.Popen(CONVERT_CMD, shell=True)
        cameraIn.stop_recording()
        cameraIn.stop_recording(splitter_port=2)
    cameraIn.close()
    print("Finished cleanup.")
    '''
    Idea: Instead of using while True in all the threads, use while <boolean var>
    This var is set to true at beginning of program, and exit handler sets it to false, 
    and then for thread in threads: thread.join()
    Time notes:
    - time.time()
    - datetime.datetime.now(), datetime.datetime.now().second, etc.
    '''

if __name__ == '__main__':
    main()
