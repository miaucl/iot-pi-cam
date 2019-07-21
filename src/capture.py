#!/usr/bin/python3
"""Capture continuous pictures and save them."""
import numpy as np
import shutil
import time
from time import sleep
from picamera import PiCamera, Color
from datetime import datetime
from PIL import Image
from scipy import ndimage
from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage import io
from skimage.morphology import closing, square
from skimage.measure import label, regionprops
from skimage.draw import polygon_perimeter



##############
# Parameters #
##############
DELAY = 2 # seconds
MIN_DELAY = 0.5 # seconds
SENSITIVITY_FACTOR = 10 # Sensitivity of difference between image
GRAY_THRESHOLD = 60 # The threshold for the image color differences
AREA_THRESHOLD = 2400 # The threshold for the areas
MOTION_COOLDOWN = 5 # The motion cooldown
FROM = 8 # Time span start
TO = 21 # Time span end
RESX = int(1024)
RESY = int(768)
POINT1 = np.asarray([0 * RESX, 0.4 * RESY], dtype=np.int) # X_LEFT, Y_TOP
POINT2 = np.asarray([0.8 * RESX, 0.9 * RESY], dtype=np.int) # X_RIGHT, Y_BOTTOM
TMP_FOLDER = "./static/img-tmp/" # The location to stop tmp pictures
MOTION_FOLDER = "./static/img-motion/" # The location to stop motion pictures
DET_FOLDER = "./static/img-det/" # The detection pictures
MOTION_LOG_FILE = "./motion-log.txt" # The log file for the motion
PICTURE_LOOP_LENGTH = 9 # The length of the picture loop before restarting at 0
LIVE_PICTURE = "./live-pic.txt" # The name of the currently live picture





########################
# Configure the camera #
########################
print("Configuration …", flush = True)
camera = PiCamera()
#camera.start_preview()
camera.resolution = (RESX, RESY)
camera.annotate_background = Color('black')


##########################
# Detection Algorithm V1 #
##########################
def detectionV1(im1,im2):
    """Detect motion between two consecutive images."""
    k = np.array([[[1,1,1],[1,1,1],[1,1,1]],[[1,1,1],[1,1,1],[1,1,1]],[[1,1,1],[1,1,1],[1,1,1]]])
    im1Conv = ndimage.filters.convolve(im1, k) # Smooth the image
    im2Conv = ndimage.filters.convolve(im2, k) # Smooth the image
    diff = np.sum(np.abs(im1Conv - im2Conv)) # Get difference between the images
    motionDetected = False

    if detectionV1.diffOld is not None: # If already an old difference to compare
        print(diff/detectionV1.diffOld, detectionV1.diffOld/diff, flush = True)
        motionDetected = diff/detectionV1.diffOld > SENSITIVITY_FACTOR or detectionV1.diffOld/diff > SENSITIVITY_FACTOR # Check if difference in image is large

    detectionV1.diffOld = diff # Keep last difference

    return motionDetected, np.abs(im1 - im2)
detectionV1.diffOld = None

##########################
# Detection Algorithm V2 #
##########################
def detectionV2(im1,im2):
    """Detect motion between two consecutive images."""
    im1Gray = rgb2gray(im1) # Convert to gray, as motion is color independent
    im2Gray = rgb2gray(im2)

    im1Gaussian = gaussian(im1Gray, sigma=1) # Blur the image for noise reduction
    im2Gaussian = gaussian(im2Gray, sigma=1)

    imAbsDiff = np.abs(im1Gaussian - im2Gaussian) # Calculate the difference between the images

    imThresh = (imAbsDiff > GRAY_THRESHOLD).astype(int) # Threshold the differences

    imDilated = closing(imThresh, square(6)) # Close gaps and holes

    labels, num  = label(imDilated, return_num=True) # Get the regions detected in the thresholds

    im1Box = im1.copy()
    motionDetected = False
    #print(list(map(lambda x: x.area, regionprops(labels))))
    for region in regionprops(labels): # Loop the regions
        if region.area > AREA_THRESHOLD: # Filter out the region by size
            box = region.bbox # Draw a bounding box around the region indicating motion
            r = [box[0],box[2],box[2],box[0]]
            c = [box[3],box[3],box[1],box[1]]
            rr, cc = polygon_perimeter(r, c, imDilated.shape, clip=True)
            im1Box[rr, cc] = 255
            motionDetected = True


    return motionDetected, im1Box.astype(np.uint8)


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
motionCooldown = 0
t = time.time()
i = 0

for filename in camera.capture_continuous(TMP_FOLDER + 'pic.jpg'):

    im = np.array(Image.open(filename), dtype=np.float32) # Read new image

    im = im[POINT1[1]:POINT2[1],POINT1[0]:POINT2[0]] # Crop image

    if imOld is not None: # If already an old image to compare
        motionDetected, imageDet = detectionV2(im, imOld) # Call motion detection algorithm
        #io.imsave(DET_FOLDER + 'pic%d.jpg' % i, imageDet)

        if motionDetected:
            if motionCooldown == 0: # Check if already a new motion can be registered
                motionCooldown = MOTION_COOLDOWN # Set motion cooldown
                datetime.now()
                print("Motion detected: %s" % camera.annotate_text, flush = True)
                with open(MOTION_LOG_FILE, "a") as logfile:
                    logfile.write(camera.annotate_text + "\n")

    imOld = im # Keep last image
    if motionCooldown > 0: # If a motion was detected
        print("Save image: %d" % motionCooldown, flush = True)
        io.imsave(DET_FOLDER + camera.annotate_text + ".jpg", imageDet)
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
    while (now.hour < FROM or now.hour >= TO): # Wait during night time
        sleep(60)
        now = datetime.now()


    now = datetime.now() # Current date and time
    timestampString = now.strftime("%Y-%m-%d-%H-%M-%S") # Convert to string
    camera.annotate_text = timestampString # Update annotation
