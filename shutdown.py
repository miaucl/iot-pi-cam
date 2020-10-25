#!/usr/bin/python
"""
Raspberry Pi Power Button Script.

Author: miaucl
Description: This script listens to a power button connected on PIN XXX and enables shutdown and reboot functionality for a raspbian dist using python 2/3.
Setup: The PIN XXX is configured with a pull up resistor and should be connected to the GND PIN by a simple interuptor.

(PIN: XXX)          (PIN: GND)
   ___                 ___
    |        ___        |
    |_______/    _______|
             BTN

Standard:
PIN=29/PORT=5
GND=30
"""



import RPi.GPIO as GPIO
import subprocess, time, sys, syslog, os

#####################
### Configuration ###
#####################

# GPIO-Port of the PIN
# GPIO 5, PIN 29 (GND just aside on PIN 30)
PORT = 5

# Max limit for shutdown (in secs), should the button be pressed longer, a reboot takes place
T_REBOOT = 3

# Timeout for the button to disable the action
T_TIMEOUT = 6

# Debounce time for the button (in secs)
T_PRELL = 0.05

###############
### Globals ###
###############

# Timestamp of the button press
timestamp = None

######################
### Initialization ###
######################

# Get the uid to check the permissions
uid = os.getuid()
# Needs root permission to shutdown/reboot
if uid > 0:
    print ("Scripts needs root permission!")
    sys.exit(0)

# GPIO initializing, BMC-Pin number, Pullup-Resistor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

##########################
### Interrupt Routines ###
##########################

# Interrupt-Routine fuer die Taste
def buttonISR(pin):
    """Interrupt routing listening to button."""
    global timestamp

    # Button is pressed down
    if not (GPIO.input(pin)):
        syslog.syslog("Button down")
        # Start the press
        if timestamp is None:
            syslog.syslog("Start press")
            timestamp = time.time()
        # Restart the press
        elif time.time() - timestamp > T_PRELL:
            syslog.syslog("Restart press")
            timestamp = time.time()
        # Skip as it is probably a rebound
        else:
            syslog.syslog("\t--> Skip: Already a press in process and probably a rebound")

    # Button is released up
    else:
        syslog.syslog("Button up")
        # If a press is active
        if timestamp:
            # A press is completed
            if time.time() - timestamp > T_PRELL:
                syslog.syslog("Stop press after: {:.3f}s".format(time.time() - timestamp))

                # Reboot for long press
                if time.time() - timestamp >= T_REBOOT:
                    syslog.syslog('==> System reboot');
                    time.sleep(1)
                    subprocess.call(['shutdown', '-r', 'now'], shell=False)
                # Shutdown for short press
                else:
                    syslog.syslog('==> System shutdown');
                    time.sleep(1)
                    subprocess.call(['shutdown', '-h', 'now'], shell=False)

                # Reset the timestamp
                timestamp = None

            # Skip as it is probably a rebound
            else:
                syslog.syslog("\t--> Skip: Probably a rebound after: {:.3f}s".format(time.time() - timestamp))


# Interrupt for the button PIN
GPIO.add_event_detect(PORT, GPIO.BOTH, callback=buttonISR)

############
### Main ###
############

syslog.syslog('Shutdown.py started');
while True:
    try:
        # Sleep
        time.sleep(1)
        # Reset the timestamp after timeout when active
        if timestamp and time.time() - timestamp > T_TIMEOUT:
            syslog.syslog("Timeout press...")
            timestamp = None
    except KeyboardInterrupt:
        syslog.syslog('Shutdown terminated (Keyboard CTRL+C)');
        print("Bye")
        sys.exit(0)
