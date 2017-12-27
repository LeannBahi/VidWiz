# Leann Bahi, lbahi , 15-112 CC

 ###################
 #Color analysis
 ###################

import cv2
import numpy as np
import os
import time


VIDEO_FILE = "./colorFile.txt"


def findBrights(img):
	# find number of bright colored pixels
	total = 0
	brightMin = np.array([0, 60, 75])
	brightMax = np.array([360, 100, 100])
	dstBright = cv2.inRange(img, brightMin, brightMax)
	numBright = cv2.countNonZero(dstBright)
	return numBright

def findLights(img):
	# find number of light colored pixels
	total = 0
	lightMin = np.array([0, 0, 60])
	lightMax = np.array([360, 35, 100])
	dstLight = cv2.inRange(img, lightMin, lightMax)
	numLight = cv2.countNonZero(dstLight)
	return numLight
	
def findDulls(img):
	# find number of dull colored pixels
	total = 0
	dullMin = np.array([0, 74, 0])
	dullMax = np.array([360, 100, 30])
	dstDull = cv2.inRange(img, dullMin, dullMax)
	numDull = cv2.countNonZero(dstDull)
	return numDull

def findWarms(img):
	# find number of warm colored pixels
	total = 0
	warmMin1 = np.array([0, 35, 35])
	warmMax1 = np.array([75, 100, 100])
	dstWarm1 = cv2.inRange(img, warmMin1, warmMax1)
	numWarm = cv2.countNonZero(dstWarm1)
	warmMin2 = np.array([285, 35, 35])
	warmMax2 = np.array([360, 100, 100])
	dstWarm2 = cv2.inRange(img, warmMin2, warmMax2)
	numWarm += cv2.countNonZero(dstWarm2)
	return numWarm

def findColds(img):
	# find number of cold colored pixels
	total = 0
	coldMin = np.array([75, 35, 35])
	coldMax = np.array([285, 100, 100])
	dstCold = cv2.inRange(img, coldMin, coldMax)
	numCold = cv2.countNonZero(dstCold)
	return numCold

def getColorType(frame) :
	#returns dict of num of pixels colored in each of the following color types
	colorTypeDict = {"bright":0,"light":0,"dull":0,"warm":0,"cold":0}
	try :
		img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		colorTypeDict["bright"] = findBrights(img)
		colorTypeDict["light"] = findLights(img)
		colorTypeDict["dull"] = findDulls(img)
		colorTypeDict["warm"] = findWarms(img)
		colorTypeDict["cold"] = findColds(img)
	except : pass
	return colorTypeDict

def averagePerFrame(frame) :
	# returns most frequent color type and temp for specific frame
	result = []
	colorTypeDict = getColorType(frame)
	# find which color type/temp has most pixels
	if ((colorTypeDict["bright"] > colorTypeDict["light"]) and 
		(colorTypeDict["bright"] > colorTypeDict["dull"])):
		result += ["bright"]
	elif ((colorTypeDict["light"] > colorTypeDict["bright"]) and 
		(colorTypeDict["light"] > colorTypeDict["bright"])):
		result += ["light"]
	elif ((colorTypeDict["dull"] > colorTypeDict["bright"]) and 
		(colorTypeDict["dull"] > colorTypeDict["light"])):
		result += ["dull"]
	if (colorTypeDict["warm"] > colorTypeDict["cold"]) : result += ["warm"]
	elif (colorTypeDict["warm"] < colorTypeDict["cold"]) : result += ["cold"]
	#returns list [type, temps] most frequent of each
	return result

def writeFile(path, contents):
	#write out file with desired content in it
    with open(path, "a") as f:
        f.write(contents)

def averageColorOfVideo(video) :
	try : os.mkdir("FRAMES")
	except : pass
	start_time = time.time()
	success = True
	# go through each frame to find most frequent color types for each frame
	# results saved into txt document
	while success:
		success, frame = video.read()
		now=time.time()
		# find time in video to save as filename
		timeName = str(int((now-start_time)*2))
		#save frame with time as name into FRAMES directory
		cv2.imwrite('FRAMES/%s.jpg' %(timeName),frame)
		#find color types for that frame
		colorTypes = averagePerFrame(frame)
		for colorType in colorTypes :
			# for each time add to txt file
			contents = "%s \n" % colorType
			writeFile(VIDEO_FILE, contents)




