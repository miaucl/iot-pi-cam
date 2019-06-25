"""Test the camera."""
from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 0
camera.start_preview()
camera.start_recording('/home/pi/Desktop/video.h264')
sleep(10)
camera.stop_recording()
camera.stop_preview()

# Watch with => xomxplayer video.h264
