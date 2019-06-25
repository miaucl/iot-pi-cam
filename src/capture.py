#!/usr/bin/python3
"""Capture continuous pictures and save them."""
import numpy as np
import shutil
import time
from time import sleep
from picamera import PiCamera
from datetime import datetime
from PIL import Image



##############
# Parameters #
##############
DELAY = 2 # seconds
MIN_DELAY = 0.5 # seconds
SENSITIVITY_FACTOR = 10 # Sensitivity of difference between image
MOTION_COOLDOWN = 5 # The motion cooldown
MOTION_FOLDER = "../img-motion/" # The location to stop motion pictures





########################
# Configure the camera #
########################
print("Configuration …")
camera = PiCamera()
#camera.start_preview()
camera.resolution = (1024, 768)






#######################
# Start the capturing #
#######################
print("Warm up …")
sleep(2) # Wait a bit before starting

print("Starting …")
now = datetime.now() # Current date and time
timestampString = now.strftime("%Y-%m-%d-%H-%M-%S") # Convert to string
camera.annotate_text = timestampString # Update annotation

imOld = None
diffOld = None
motionCooldown = MOTION_COOLDOWN
t = time.time()

for filename in camera.capture_continuous('../img-temp/pic.jpg'):
    print('Captured %s' % filename)

    im = np.array(Image.open(filename), dtype=np.float32) # Read new image

    if imOld is not None: # If already an old image to compare
        diff = np.sum(np.square(im - imOld)) # Get difference between the images

        if diffOld is not None: # If already an old difference to compare
            print(diff/diffOld, diffOld/diff)
            if diff/diffOld > SENSITIVITY_FACTOR or diffOld/diff > SENSITIVITY_FACTOR: # Check if difference in image is large
                if motionCooldown == 0: # Check if already a new motion can be registered
                    motionCooldown = MOTION_COOLDOWN # Set motion cooldown
                    datetime.now()
                    print("Motion detected")

        diffOld = diff # Keep last difference

    imOld = im # Keep last image
    if motionCooldown > 0: # If a motion was detected
        print("Save image")
        shutil.copy2(filename, MOTION_FOLDER + camera.annotate_text + ".png")
        motionCooldown -= 1 # Cool down from last motion





    elapsed = time.time() - t # Calculate time used for processing
    print("Step time: %f" % elapsed)

    sleep(max(MIN_DELAY, DELAY - elapsed)) # Wait for next picture
    t = time.time() # Start timer


    now = datetime.now() # Current date and time
    timestampString = now.strftime("%Y-%m-%d-%H-%M-%S") # Convert to string
    camera.annotate_text = timestampString # Update annotation
