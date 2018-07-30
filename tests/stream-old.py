#!/usr/bin/env python3

import subprocess
import picamera

# rtmp://a.rtmp.youtube.com/live2/2p11-bswc-5jmq-82c2

YOUTUBE="rtmp://a.rtmp.youtube.com/live2/"
KEY="2p11-bswc-5jmq-82c2"

# stream_cmd = 'ffmpeg -f h264 -r 25 -i - -itsoffset 5.5 -fflags nobuffer -f alsa -ac 1 -i hw:1,0 -vcodec copy -acodec aac -ac 1 -ar 8000 -ab 32k -map 0:0 -map 1:0 -strict experimental -f flv ' + YOUTUBE + KEY 
# stream_cmd = 'ffmpeg -f h264 -r 30 -i - -fflags nobuffer -vcodec copy -strict experimental -f flv ' + YOUTUBE + KEY
# stream_cmd = 'ffmpeg -fh264 -re -i - -vcodec copy -strict experimental -f flv ' + YOUTUBE + KEY
# (WORKING) stream_cmd = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE + KEY

stream_cmd = 'avconv -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv ' + YOUTUBE + KEY

stream_pipe = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE)

camera = picamera.PiCamera()

try:
    # camera.resolution = (1280, 720)
    # camera.resolution = (858/848, 480)
    # camera.resolution = (640, 480/360)
    camera.resolution = (960, 540)
    camera.framerate = 25
    # camera.vflip = True
    # camera.hflip = True
    camera.start_recording(stream_pipe.stdin, format='h264')
    while True:
        camera.wait_recording(1)

except KeyboardInterrupt:
    camera.stop_recording()

finally:
    camera.close()
    stream_pipe.stdin.close()
    stream_pipe.wait()
    print("Camera safely shut down")
    print("Good bye")
