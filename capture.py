#!/usr/bin/env python3
from picamera import PiCamera

import time,os

def capture( saveto, fps=10, duration=10 ):
    h264_path = saveto + 'capture.h264' 
    mp4_path = saveto + 'capture.mp4'
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = fps
        camera.start_recording( h264_path )
        time.sleep(duration)
        camera.stop_recording()
    cmd = 'avconv -y -loglevel quiet -r {} -f h264 -i {} -vcodec copy {}'.format( fps, h264_path, mp4_path)
    print(cmd)
    os.system(cmd)


if __name__ == '__main__':
    capture( 'img/' )
    
