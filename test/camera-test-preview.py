"""Test the camera."""
from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 0
#camera.resolution = (64, 64)
#camera.framerate = 15
camera.annotate_text = "Hello world!"
camera.start_preview(alpha=255)
sleep(10)
camera.stop_preview()
