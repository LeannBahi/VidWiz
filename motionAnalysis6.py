#!/usr/bin/env python

# Leann Bahi, lbahi , 15-112 CC

###########################################
#Code Artifacts + Technology Demonstration
###########################################
# analyses mouvement in video
# creates file that keeps track of how much movement occured at a certain time



'''
SYNOPSIS

    movement.py [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

    This is a tool that will watch the output of a video camera. It will
    highlight any movement that it sees. It also detects the relative amount of
    motion and stillnes and indicates significant changes on stdout.
    During period of movement the individual camera frames will be saved.

    THIS IS A ROUGH DRAFT, BUT EVERYTHING WORKS.

    On OS X:
        brew tap homebrew/science
        brew install opencv  # or, "brew install opencv --env=std"
        export PYTHONPATH=/usr/local/lib/python2.7/site-packages:${PYTHONPATH}

    Video playback on OS X:
        brew install mplayer  # takes a long time (~ 5 minutes)
        brew install mencoder
        mplayer -vo corevideo "mf://movement*.png" -mf type=png:fps=30 -loop 0

    Video encoding on OS X:
        mencoder "mf://*.png" -mf type=png:fps=25 -ovc lavc -lavcopts 
        vcodec=mpeg4 -o output.mov

    This docstring will be printed by the script if there is an error or
    if the user requests help (-h or --help).

EXAMPLES

    The following are some examples of how to use this script.
    $ movement.py --version
    1

EXIT STATUS

    This exits with status 0 on success and 1 otherwise.
    This exits with a status greater than 1 if there was an
    unexpected run-time error.

AUTHOR

    Noah Spurrier <noah@noah.org>

LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2015, Noah Spurrier
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

VERSION

    Version 4 - modified by Leann Bahi
'''

__version__ = 'Version 4'
__date__ = '2015-11-23 15:46:55:z'
__author__ = 'Leann Bahi <leannbahi@gmail.com' 
            #inspired by Noah Spurrier <noah@noah.org>

"""
parts inspired by Noah Spurrier's version  :
 - use of t_minus, t_now, t_plus
 - use of threshold and delta_count to find pixels in movement
    (keeping track of counting pixels not included)
    (writing file with movement based on time not included)
"""

import sys
import os
import traceback
import optparse
import time
import logging
import cv2
import numpy
import sys
import time
#from pexpect import run, spawn

DELTA_COUNT_THRESHOLD = 1000
MOTION_FILE = "./motionFile.txt"

def delta_images(t0, t1, t2):
    #return difference between the two times
    d1 = cv2.absdiff(t2, t0)
    return d1

def writeFile(path, contents):
    #write out file with desired content in it
    with open(path, "a") as f:
        f.write(contents)


def getVideoState(delta_count_last, delta_count,path) :
    #get Video state
    record_video_state = False
    if (delta_count_last < DELTA_COUNT_THRESHOLD and 
        delta_count >= DELTA_COUNT_THRESHOLD):
        record_video_state = True
        timeRoundedToS = time.time()//1
        contents = "(%d, %d)\n"%(timeRoundedToS, delta_count)
        writeFile(path, contents)
        sys.stdout.flush()
    elif (delta_count_last >= DELTA_COUNT_THRESHOLD and 
        delta_count < DELTA_COUNT_THRESHOLD):
        record_video_state = False
        sys.stdout.flush()
    return record_video_state

def analyseVideo(cam, path, t_minus, t_now, t_plus, delta_count_last, 
    start_time) :
    delta_view = delta_images(t_minus, t_now, t_plus)
    retval, delta_view = cv2.threshold(delta_view, 16, 255, 3)
    cv2.normalize(delta_view, delta_view, 0, 255, cv2.NORM_MINMAX)
    img_count_view = cv2.cvtColor(delta_view, cv2.COLOR_RGB2GRAY)
    #colors in black pixels not in motion
    delta_count = cv2.countNonZero(img_count_view)
    #count non black pixels
    record_video_state = False
    record_video_state = getVideoState(delta_count_last, delta_count,path)
    now=time.time()
    delta_count_last = delta_count
    # move images through the queue.
    t_minus = t_now
    t_now = t_plus
    t_plus = cam.read()[1]
    t_plus = cv2.blur(t_plus,(8,8))
    try :
        t_plus = cv2.resize(t_plus, (640, 480))
    except :
        cam.release()
        cv2.destroyAllWindows()
    return (t_minus, t_now, t_plus)

#test video : videoTester.MP4
def motionData(videoPath) :
    # set info
    cam = cv2.VideoCapture(videoPath)
    cam.set(3,640)
    cam.set(4,480)
    t_minus = cam.read()[1]
    t_now = cam.read()[1]
    t_plus = cam.read()[1]
    t_now = cv2.resize(t_now, (640, 480))
    t_minus = cv2.resize(t_minus, (640, 480))
    t_plus = cv2.resize(t_plus, (640, 480))
    delta_count_last = 1
    start_time = time.time()
    record_video_state = False

    while(cam.isOpened()):
        #for each frame
        solution = (analyseVideo(cam, MOTION_FILE, t_minus, t_now, t_plus, 
            delta_count_last, start_time))
        t_minus, t_now, t_plus = solution[0], solution[1], solution[2]
        # Wait up to 10ms for a key press.
        # If the key is the ESC or 'q' then quit.
        key = cv2.waitKey(10)
        if key == 0x1b or key == ord('q'): break
