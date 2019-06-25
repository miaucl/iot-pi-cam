#!/usr/bin/python
"""Control hardware shutdown behaviour."""

import RPi.GPIO as GPIO
import subprocess, time, sys, syslog, os

# GPIO-Port, an dem die Taste gegen GND angeschlossen ist
# GPIO 5, Pin 29 (GND waere daneben auf Pin 30)
PORT = 5

# Schwelle fuer Shutdown (in Sekunden), wird die Taste laenger
# gedruckt, erfolgt ein Reboot
T_REBOOT = 3

# Schwelle fuer timeout
T_TIMEOUT = 10

# Entprellzeit fuer die Taste
T_PRELL = 0.05

uid = os.getuid()
if uid > 0:
    print ("Programm benoetigt root-Rechte!")
    sys.exit(0)

# GPIO initialisieren, BMC-Pinnummer, Pullup-Widerstand
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PORT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Zeitdauer des Tastendrucks
duration = 0

# Interrupt-Routine fuer die Taste
def buttonISR(pin):
    """Interrupt routing listening to button."""
    global duration

    if not (GPIO.input(pin)):
        # Taste gedrueckt
        if duration == 0:
            duration = time.time()
        else:
        # Taste losgelassen
            if duration > 0:
                elapsed = (time.time() - duration)
                duration = 0
                if elapsed > T_TIMEOUT:
                    duration = 0
                if elapsed >= T_REBOOT:
                    syslog.syslog('Shutdown: System rebooted');
                    subprocess.call(['shutdown', '-r', 'now'], shell=False)
                elif elapsed >= T_PRELL:
                    syslog.syslog('Shutdown: System halted');
                    subprocess.call(['shutdown', '-h', 'now'], shell=False)

# Interrupt fuer die Taste einschalten
GPIO.add_event_detect(PORT, GPIO.BOTH, callback=buttonISR)

syslog.syslog('Shutdown.py started');
while True:
    try:
        time.sleep(300)
        if time.time() - duration > T_TIMEOUT:
            duration = 0
    except KeyboardInterrupt:
        syslog.syslog('Shutdown terminated (Keyboard)');
        print ("Bye")
        sys.exit(0)
