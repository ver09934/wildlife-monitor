import socket
import time
import picamera

with picamera.PiCamera() as camera:

    camera.resolution = (1024, 768)
    camera.framerate = 30

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(0)

    # Accept a single connection and make a file-like object out of it
    connection = server_socket.accept()[0].makefile('wb')
    try:
        print("Streaming start...")
        camera.start_recording(connection, format='h264', resize=(320, 240))
        iter = 1
        while True:
            time.sleep(5)
            print("Recording " + str(iter) + " start...")
            camera.start_recording('highres-' + str(iter) + '.h264', splitter_port=2)
            camera.wait_recording(5)
            camera.stop_recording(splitter_port=2)
            print("Recording " + str(iter) + " end...")
            time.sleep(5)
            iter += 1
    finally:
        connection.close()
        server_socket.close()
        print("---- CLOSED CLEANLY ----")
