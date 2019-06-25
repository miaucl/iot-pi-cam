"""Test the camera."""
from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 0
camera.start_preview()
sleep(3)
for i in range(5):
    sleep(1)
    camera.capture('/home/pi/Desktop/image%s.jpg' % i)
camera.stop_preview()
