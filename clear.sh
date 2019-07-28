#!/bin/bash

# Clear log entries
rm -f $PWD/src/motion-log.txt
touch $PWD/src/motion-log.txt

# Remove images
rm -f $PWD/src/static/img-motion/*.jpg
rm -f $PWD/src/static/img-det/*.jpg
