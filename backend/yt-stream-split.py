#!/usr/bin/env python3

import subprocess
import picamera

YOUTUBE="rtmp://a.rtmp.youtube.com/live2/"

# get youtube streaming key from yt-stream-key.txt
f = open("yt-stream-key.txt", "r")
if f.mode == 'r':
    KEY = f.read()

stream_cmd = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE + KEY

stream_pipe = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE, stdout=None)

with picamera.PiCamera() as camera:

    try:
        camera.resolution = (1280, 720)
        camera.framerate = 30
        
        print("Streaming command starting...")
        camera.start_recording(stream_pipe.stdin, format='h264', resize=(960, 540))
        print("Streaming command started...")
        
        iter = 1
        
        while True:
            
            camera.wait_recording(10)
            
            print("Recording " + str(iter) + " start...")
            camera.start_recording('highres-' + str(iter) + '.h264', splitter_port=2)
            camera.wait_recording(5)
            camera.stop_recording(splitter_port=2)
            print("Recording " + str(iter) + " end...")
            
            camera.wait_recording(10)
            iter += 1

    except KeyboardInterrupt:
        camera.stop_recording(splitter_port=2)
        camera.stop_recording()

    finally:
        camera.close()
        stream_pipe.stdin.close()
        stream_pipe.wait()
        print("Camera safely shut down")
        print("Good bye")
