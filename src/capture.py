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
TMP_FOLDER = "./static/img-tmp/" # The location to stop tmp pictures
MOTION_FOLDER = "./static/img-motion/" # The location to stop motion pictures
MOTION_LOG_FILE = "./motion-log.txt" # The log file for the motion
PICTURE_LOOP_LENGTH = 9 # The length of the picture loop before restarting at 0
LIVE_PICTURE = "./live-pic.txt" # The name of the currently live picture





########################
# Configure the camera #
########################
print("Configuration …", flush = True)
camera = PiCamera()
#camera.start_preview()
camera.resolution = (1024, 768)






#######################
# Start the capturing #
#######################
print("Warm up …", flush = True)
sleep(2) # Wait a bit before starting

print("Starting …", flush = True)
now = datetime.now() # Current date and time
timestampString = now.strftime("%Y-%m-%d-%H-%M-%S") # Convert to string
camera.annotate_text = timestampString # Update annotation

imOld = None
diffOld = None
motionCooldown = 0
t = time.time()
i = 0

for filename in camera.capture_continuous(TMP_FOLDER + 'pic.jpg'):

    im = np.array(Image.open(filename), dtype=np.float32) # Read new image

    if imOld is not None: # If already an old image to compare
        diff = np.sum(np.square(im - imOld)) # Get difference between the images

        if diffOld is not None: # If already an old difference to compare
            #print(diff/diffOld, diffOld/diff)
            if diff/diffOld > SENSITIVITY_FACTOR or diffOld/diff > SENSITIVITY_FACTOR: # Check if difference in image is large
                if motionCooldown == 0: # Check if already a new motion can be registered
                    motionCooldown = MOTION_COOLDOWN # Set motion cooldown
                    datetime.now()
                    print("Motion detected: %s" % camera.annotate_text, flush = True)
                    with open(MOTION_LOG_FILE, "a") as logfile:
                        logfile.write(camera.annotate_text + "\n")

        diffOld = diff # Keep last difference

    imOld = im # Keep last image
    if motionCooldown > 0: # If a motion was detected
        print("Save image: %d" % motionCooldown, flush = True)
        shutil.copy2(filename, MOTION_FOLDER + camera.annotate_text + ".jpg")
        motionCooldown -= 1 # Cool down from last motion


    shutil.move(filename, TMP_FOLDER + 'pic%d.jpg' % i) # Move picture
    with open(LIVE_PICTURE, "w") as livefile: # Save current live picture
        livefile.write('/static/img-tmp/pic%d.jpg' % i) # Absolute path
    i += 1 # Next index
    if i > PICTURE_LOOP_LENGTH: # Restart at 0
        i = 0


    elapsed = time.time() - t # Calculate time used for processing
    #print("Step time: %f" % elapsed)

    sleep(max(MIN_DELAY, DELAY - elapsed)) # Wait for next picture
    t = time.time() # Start timer


    now = datetime.now() # Current date and time
    timestampString = now.strftime("%Y-%m-%d-%H-%M-%S") # Convert to string
    camera.annotate_text = timestampString # Update annotation
