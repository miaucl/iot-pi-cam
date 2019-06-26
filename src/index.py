#!/usr/bin/python3
# coding: utf-8

"""The web access to the picture capturing.

Provide a web access to see live and past pictures taken.
"""
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime

from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "pi": generate_password_hash("2778")
}



TMP_FOLDER = "/static/img-tmp/" # The location to stop tmp pictures
TMP_FOLDER_REL = "./static/img-tmp/" # The location to stop tmp pictures
MOTION_FOLDER = "/static/img-motion/" # The location to stop motion pictures
MOTION_FOLDER_REL = "./static/img-motion/" # The location to stop motion pictures
MOTION_LOG_FILE = "./motion-log.txt" # The log file for the motion
LIVE_PICTURE = "./live-pic.txt" # The name of the currently live picture

@auth.verify_password
def verify_password(username, password):
    """Verify the password."""
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.after_request
def add_header(response):
    """Turn off the cache."""
    response.cache_control.no_cache = True
    return response

@app.route('/')
@auth.login_required
def live():
    """Respond to a live picture request."""
    reload = request.args.get('reload')
    now = datetime.now() # Current date and time
    timestampString = now.strftime("%Y-%m-%d-%H-%M-%S") # Convert to string
    with open(LIVE_PICTURE, 'r') as livefile:
        livePic = livefile.read()
    return render_template('index.html', timestamp=timestampString, livePic=livePic, reload=reload)

@app.route('/motion')
@auth.login_required
def motion():
    """Respond to a motion request."""
    with open(MOTION_LOG_FILE, 'r') as motionfile:
        lines = motionfile.read().splitlines()
        lines.reverse()
    return render_template('motion.html', motionTimestamps=lines)

@app.route('/motion-view')
@auth.login_required
def motionView():
    """Respond to a motion view request."""
    timestamp = request.args.get('timestamp')
    motionPic = MOTION_FOLDER + timestamp + ".jpg"
    files = [f for f in listdir(MOTION_FOLDER_REL) if isfile(join(MOTION_FOLDER_REL, f))]
    index = files.index(timestamp + ".jpg")
    next = os.path.splitext(files[index + 1])[0] if index + 1 < len(files) else None
    previous = os.path.splitext(files[index - 1])[0] if index > 0 else None
    return render_template('motion-view.html', motionPic=motionPic, next=next, previous=previous)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


# PRODUCTION
# from waitress import serve
#
# from flask import Flask
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def index():
#     return '<h1>Hello!</h1>'
#
#
# serve(app, host='0.0.0.0', port=8080)
