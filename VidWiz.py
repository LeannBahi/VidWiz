# Leann Bahi, lbahi , 15-112 CC

# getVideo

from Tkinter import *
import os
import tkMessageBox
import tkSimpleDialog
import cv2
import numpy
import subprocess
from song_api2 import downloadSong
from motionAnalysis6 import motionData
from colorAnalysis4 import averageColorOfVideo
import bisect
import tkFileDialog
from PIL import Image, ImageTk
import threading
import time

class motionThread (threading.Thread):
    def __init__(self, threadID, name, path):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.path = path
    def run(self):
        print "Starting " + self.name
        motionData(self.path)
        print "Exiting " + self.name

class colorThread (threading.Thread):
    def __init__(self, threadID, name, video):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.video = video
    def run(self):
        print "Starting " + self.name
        averageColorOfVideo(self.video)
        print "Exiting " + self.name

def init(data):
    data.mode = "uploadScreen"
    data.topMargin = 50
    data.numVideos = 1
    data.videos = []
    data.videoPath = None
    data.videoLength = 15
    data.tags = 170
    data.motionTag = None
    data.colorTag = None
    data.waitingIndex = 0
    data.waitingImages=([PhotoImage(file="dancing0.gif"),
        PhotoImage(file="dancing1.gif"),
        PhotoImage(file="dancing2.gif"),PhotoImage(file="dancing3.gif")])
    data.videoName = "av"
    if data.mode == "showParameters" :
        showParametersInit(data)
    data.homeWidth, data.homeHeight = 100, 50
    data.homeOffset = 20
    data.helpOn = False

def uploadScreenInit(data) :
    #uploadButton info : x, y, width. height
    data.uploadX = data.width/2
    data.uploadY = data.height/2+data.topMargin
    data.uploadWidth = 400
    data.uploadHeight = 140

def showParamColorsInit(data) :
    txt = readColorFile()
    #returns main color characteristics for video
    data.colorTag = txt
    # put color type and temp in data to make accessible throughout code
    if (txt[0] in data.colorTypes) : 
        data.currentColorTypeIndex = data.colorTypes.index(txt[0])
    if (txt[1] in data.colorTemp) :
        data.currentColorTempIndex = data.colorTemp.index(txt[1])

def doneInit(data) :
    # open video button info : x, y, width. height
    data.openWidth = 400
    data.openHeight = 140
    data.openX = data.width/2
    data.openY = data.height/2-data.topMargin

def showParametersInit(data) :
    # generate music button info
    data.widthGenerateMusicButton = 200
    data.heightGenerateMusicButton = 60
    data.xGenerateMusicButton = data.width - data.widthGenerateMusicButton
    data.yGenerateMusicButton = data.height - data.heightGenerateMusicButton
    # motion graph info
    data.graphWidth = 400
    data.graphHeight = 250
    data.graphTopLeft = (data.topMargin*2*2, data.topMargin*2*2)
    data.graphBottomRight = (data.topMargin*2*2+data.graphWidth, 
        data.topMargin*2*2+data.graphHeight)
    # important points in graph
    data.dictPoints = dict()
    data.listXs = []
    data.graphPointSelected = False
    data.selectedPoint = None 
    # get color information 
    data.colorTypes = ["bright", "light", "dull"]
    data.currentColorTypeIndex = 0
    data.colorTemp = ["warm", "cold"]
    data.currentColorTempIndex = 0
    showParamColorsInit(data)
    
def buttonPressed(event, data, x, y, width, height) :
    # x, y, width, and height of any button
    # determines if button was pressed based on properties
    minX, maxX= x - width/2, x + width/2
    minY, maxY = y - height/2, y + height/2
    if ((event.x>=minX) and (event.x<=maxX) and 
        (event.y>=minY) and (event.y<=maxY)) :
        return True
    return False

#muxing ffmpeg call  from stackoverflow.com written by user Fahadkalis
def muxing(data) :
    # merges video with generated music
    cmd = '''ffmpeg -y -i generatedSong.mp3  -r 30 -i %s  -filter:a aresample=\
async=1 -c:a flac -c:v copy %s.mkv'''%(str(data.videoPath),data.videoName)
    subprocess.call(cmd, shell=True)                            # "Muxing Done
    print('Muxing Done')

def getTags(data) :
    #returns tag for desired music arrangement based on video characteristics
    #numbers correspond to different music arrangements
    mapping = ({"slow": [161,161,167,164,171,171], 
        "med":[168,160,162,162,165,165], "fast":[169,169,168,166,170,163]})
    # 0 and 1 : bright, warm then cold
    # 2 and 3 : light, warm then cold
    # 4 and 5 : dull, warm then cold
    if data.colorTag[0] == "bright" : i = 0
    elif data.colorTag[0] == "light" : i = 1
    elif data.colorTag[0] == "dull" : i = 2
    if data.colorTag[1] == "warm" : i *= 2
    elif data.colorTag[1] =="cold" : i = (i*2) + 1
    return mapping[data.motionTag][i]

def generateMousePressed(event,data) :
    data.mode = "waiting"
    #delete any existing generated music file
    os.system("rm generatedSong.mp3")
    redrawAll(canvas, data)
    #ask user for video title
    message = "Please input video title"
    title = "Video title"
    videoTitle = tkSimpleDialog.askstring(title, message)
    data.videoName = videoTitle
    data.tags = getTags(data)
    videoLength = data.videoLength/2
    if videoLength>10 : videoLength -= 4
    #download song with same length as video
    downloadSong(videoTitle, data.tags, videoLength)
    #merge video and song
    muxing(data)
    #go to done screen
    data.mode = "done"

def pressInGraph(event, data) :
    #returns True if press was in motion graph
    x1, y1 = data.graphTopLeft[0], data.graphTopLeft[1]
    x2, y2 = data.graphBottomRight[0], data.graphBottomRight[1]
    if ((event.x >x1) and (event.x <x2) and (event.y >y1) and (event.y <y2)): 
        return True
    return False 

def findSelectedPoint(event, data):
    #finds what point has been selected in the graph
    r = 6
    #check for each point in graph
    for x in data.dictPoints:
        y = data.dictPoints[x]
        d = ((event.x-x)**2 + (event.y-data.dictPoints[x])**2)**0.5
        if d <= r : return [x, y]
    return None

def updatePoints(event, data) :
    #when point in graph moved : 
    #updates moved point location and dict/list for points
    d = event.y - (data.selectedPoint[1])
    data.selectedPoint[1] = event.y
    i = data.listXs.index(data.selectedPoint[0])
    x = data.listXs[i]
    data.dictPoints[x] += d
  
def showParamMouseColors(event, data) :
    #updates color characteristics when pressed
    width, height = 100, 30
    textSize = 50
    delta = 6
    x = data.topMargin*delta + textSize/2
    y = data.topMargin*2 + width*2*2+height/2
    #updates color type
    if buttonPressed(event, data, x, y, width, height) :
        data.currentColorTypeIndex = (data.currentColorTypeIndex + 1)%(delta/2)
    x1 = x + width+width/2
    #updates color temp (warm and cold)
    if buttonPressed(event, data, x1, y, width, height) :
        data.currentColorTempIndex = (data.currentColorTempIndex + 1)%2

def paramMousePressed(event, data) :
    try : x = data.xGenerateMusicButton 
    except : showParametersInit(data)
    # if generate music button pressed : generate music
    if buttonPressed(event, data,data.xGenerateMusicButton, 
        data.yGenerateMusicButton, data.widthGenerateMusicButton, 
        data.heightGenerateMusicButton) :
        generateMousePressed(event,data)
    # if pressed in graph : move necessary point
    if pressInGraph(event, data) :
        solution = findSelectedPoint(event, data)
        oldSelectedPoint = data.selectedPoint
        if solution != None :
            data.selectedPoint = solution
        elif oldSelectedPoint == None :
            pass
        else :
            updatePoints(event, data)
    # modifie color characteristics when pressed
    showParamMouseColors(event, data)

def numIsLegal(data) :
    #if input invalid, ask for new input
    try:
        data.numVideos = int(data.numVideos)
    except :
        message = "Invalid input. Please input a valid number"
        title = "Invalid input"
        #tell user input is invalid
        tkMessageBox.showwarning(title, message)
        getVideoFiles(data)

def videoIsLegal(data, response,i) :
    #if input invalid, ask for new input
    end = -3
    if (response[end:] == "mp4") or (response[end:] == "MP4") :
        if data.numVideos == 1 :
            data.videos = [response]
        else :
            cmd = "ffmpeg -y -i %s -vf scale=640:360 %s%d.mp4"%(response,response,i)
            subprocess.call(cmd, shell=True)
            data.videos += ["%s%d.mp4"%(response,i)]
            # data.videos += [response]
    else : 
        message = "Invalid input. Please only upload .mp4 video files"
        title = "Invalid input"
        #tell user input is invalid
        tkMessageBox.showwarning(title, message)
        #ask again
        response = tkFileDialog.askopenfilename()
        videoIsLegal(data, response,i)

def getNumVideos(data) :
    #ask for number of desired videos
    message = """If you desire to add music to a single video input 1.
To create a montage, input the number of videos that will be uploaded."""
    title = "Number of videos"
    data.numVideos = tkSimpleDialog.askstring(title, message)
    numIsLegal(data)

def mergeVideos(data, videos) :
    # merges all uploaded videos into one video
    #delete previously existing merged video
    os.system("rm output.mp4")
    if len(data.videos) == 1 :
        return data.videos[0]
    addVideos = ""
    for i in range(len(data.videos)) :
        addVideos += str(data.videos[i]) + " -cat "
    end = -6
    addVideos = addVideos[:end]
    cmd = "mp4box -add %s output.mp4"%addVideos
    os.system(cmd)
    return "output.mp4"

def getVideoFiles(data) :
    #get number of desired videos from user
    getNumVideos(data)
    #ask which file for desired number of videos
    for i in range(data.numVideos) :
        response = tkFileDialog.askopenfilename()
        videoIsLegal(data, response,i)
        #merge videos into one video
    data.videoPath = mergeVideos(data, data.videos)
    #get characteristics (color, motion) of video
    getVideoCharacteristics(data, data.videoPath)

def doneMousePressed(event, data) :
    #if open video button is pressed : open file
    try : x = data.openX
    except : doneInit(data)
    if buttonPressed(event, data, data.openX, data.openY,
        data.openWidth, data.openHeight) :
        os.system("open %s.mkv"%data.videoName)

def mousePressed(event, data):
    # determine action depending on mode
    global canvas
    if buttonPressed(event, data, data.width-data.homeOffset, data.homeOffset,
        data.homeWidth, data.homeHeight):
        init(data)
        data.mode = "uploadScreen"
    if buttonPressed(event, data, data.homeOffset, data.homeOffset,
        data.homeWidth, data.homeHeight):
        data.helpOn = not data.helpOn
    if data.mode == "uploadScreen" :
        if buttonPressed(event, data, data.uploadX, data.uploadY, 
            data.uploadWidth, data.uploadHeight) :
            data.mode = "waiting"
            getVideoFiles(data)
            redrawAll(canvas, data)
    if data.mode == "showParameters" :
        paramMousePressed(event, data)
    if data.mode == "done" :
        doneMousePressed(event, data)


def getVideoCharacteristics(data, path):
    global canvas
    video = cv2.VideoCapture(path)
    # remove previous existing files if necessary
    os.system("rm motionFile.txt")
    os.system("rm -rfv FRAMES/*")
    os.system("rm colorFile.txt")
    # get length of video
    cmd = "ffprobe -i %s -show_format -v quiet | sed -n 's/duration=//p'"%path
    try :
        data.videoLength = int(float(subprocess.check_output(cmd, shell=True)))
    except :
        data.helpOn = True
        drawHelpScreen(canvas, data)
    #use threading to make analysing faster
    motionThread1 = motionThread(1, "motionThread", path)
    motionThread1.start()
    colorThread1 = colorThread(2, "colorThread", video)
    colorThread1.start()
    threads = [motionThread1, colorThread1]
    #when motion and color analysis completed, proceed
    for t in threads:
        t.join()
    #show parameters when done analysing
    data.mode = "showParameters"

def keyPressed(event, data):
    pass

def timerFired(data):
    #update index for gif image
    step = 4
    data.waitingIndex = (data.waitingIndex + 1)%step

def drawButtons(canvas, data) :
    # draw upload screen / home screen
    if data.mode == "uploadScreen" :
        x, y = data.uploadX, data.uploadY
        buttonWidth, buttonHeight = data.uploadWidth, data.uploadHeight
        canvas.create_rectangle(x-buttonWidth/2, y-buttonHeight/2,
            x+buttonWidth/2, y+buttonHeight/2,fill="blue",width=0)
        textSize = 60
        canvas.create_text(x,y, text="Upload", fill="white", 
            font="Helvetica %d"%textSize)
        step1, step2 = 120, 170
        canvas.create_text(x,y-step2, 
            text="Create a video montage with generated music", fill="white", 
            font="Helvetica %d"%(textSize/2))
        canvas.create_text(x,y-step1, 
            text="Upload videos to start the process", fill="white", 
            font="Helvetica %d"%(textSize/2))
        
def drawWaitingScreen(canvas, data) :
    # draw loading/analysing screen
    x = data.width/2
    y = data.height/2+data.topMargin*2*2
    textSize = 60
    canvas.create_text(x,y, text="Analysing...", fill="white", 
            font="Helvetica %d"%textSize)
    canvas.create_image(data.width/2, data.height/2, 
        image=data.waitingImages[data.waitingIndex])

def readMotionFile() :
    #read file with all info about motion created in analysis of video
    listOfFileTuples = list()
    txt = open("motionFile.txt")
    txtStr = str(txt.read())
    t0 = None
    #go through each set of values
    for values in txtStr.split("\n"):
        # for each recorded time, create tuple (time, motion)
        createListForTuple = []
        for num in values.split(","):
            createListForTuple += [num]
        if len(createListForTuple)==2 : 
            if t0 == None : t0 = int(createListForTuple[0][1:])
            newTuple = (int(createListForTuple[0][1:])-t0, 
                createListForTuple[1][:-1])
        # create list of all tuples
        listOfFileTuples += [newTuple]
    #return list of all tuples (time, motion)
    return listOfFileTuples

def averageOfList(listToAverage) :
    #returns the average of a list
    length = len(listToAverage)
    if length == 0 : return 0
    summ = 0
    for num in listToAverage :
        summ += int(num)
    return summ/length

def condenseMotionFile(listOfTuples) :
    listOfTuples += [(0,0)]
    newList = list()
    #keep track previous time
    previousTime = None
    listToAverage = list()
    for tup in listOfTuples :
        #initiate
        if (previousTime == None) :
            listToAverage = [tup[1]]
            previousTime = tup[0]
        elif (previousTime != tup[0]) :
            #if previous time is different, new second has started
            #make average of all data for previous second
            averagedList = averageOfList(listToAverage)
            #add to list
            newList += [(previousTime, averagedList)]
            #reset list
            listToAverage = list()
            previousTime = tup[0]
        elif (previousTime == tup[0]) :
            #if previous time is the same : add to list to then get average
            listToAverage += [tup[1]]
    return newList
    # returns Tuple of motion averages for each individual second

def drawGraphAxisDescription(canvas, data) :
    #draws axis for motion graph
    graphWidth = 400
    graphHeight = 250
    arrowDelta = 10
    textSize = 20
    lineWidth = 3
    x1, y1 = data.topMargin*2*2,data.topMargin*2*2
    x2, y2 = x1+graphWidth, y1+graphHeight
    #draws lines
    canvas.create_line(x1,y1-arrowDelta,x1,y2,x2+arrowDelta,y2, fill="green", 
        width=lineWidth)
    canvas.create_line(x2,y2-arrowDelta,x2+arrowDelta,y2,x2,y2+arrowDelta,
        fill="green", width=lineWidth)
    canvas.create_text(x2,y2+arrowDelta, text="time", anchor=NW, fill="green", 
        font="Helvetica %d"%textSize)
    #draws axis description
    canvas.create_line(x1-arrowDelta,y1,x1,y1-arrowDelta,x1+arrowDelta,y1,
        fill="green", width=lineWidth)
    canvas.create_text(x1+arrowDelta,y1, text="motion", anchor=SW,fill="green", 
        font="Helvetica %d"%textSize)

def drawSelectedPoint(canvas, data):
    # draws out points that can be moved in graph
    r = 3
    #draws normal points
    for pointX in data.dictPoints :
        cx = pointX
        cy = data.dictPoints[pointX]
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="red",width=0)
    #draws currently selected point
    if data.selectedPoint != None :
        r = 5
        cx = data.selectedPoint[0]
        cy = data.selectedPoint[1]
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="red")

def updateMotionTag(data):
    # update motion tag when points in graph moved
    total = 0
    for key in data.dictPoints :
        total += data.dictPoints[key]
    averageMotion = total/len(data.dictPoints)
    bound1 = 120  # fast
    bound2 = 190  # med
    bound3 = 250  # slow
    # determine tag based off of different bounds
    if averageMotion < data.topMargin*2*2 + bound1 :
        data.motionTag = "fast"
    elif averageMotion < data.topMargin*2*2 + bound2 :
        data.motionTag = "med"
    else : 
        data.motionTag = "slow"

def createDict(canvas, data, motionOverTime,x1,y2,graphWidth,
    graphHeight,maximumTime,maximumMotion) :
    # create dict of all points in graph
    initX = x1 + (int(motionOverTime[0][0]) * graphWidth / maximumTime)
    initY = y2 - (int(motionOverTime[0][1]) * graphHeight / maximumMotion)
    if len(data.dictPoints) == 0 :
        data.dictPoints[initX] = initY
        data.listXs = [initX]
        #adds each x as a key to dict, maps to y-coordinate
        #also create list of only x-coordinates
        for tup in range(len(motionOverTime)-1) :
            x3 = x1 + (int(motionOverTime[tup][0]) * graphWidth / maximumTime)
            y3 = y2 - (int(motionOverTime[tup][1]) * graphHeight/maximumMotion)
            x4 = x1 + (int(motionOverTime[tup+1][0]) * graphWidth /maximumTime)
            y4 = y2 - (int(motionOverTime[tup+1][1])*graphHeight/maximumMotion)
            data.dictPoints[x4] = y4
            data.listXs += [x4]

def drawMotionGraph(canvas, data) :
    # draw motion graph
    graphWidth, graphHeight = data.graphWidth, data.graphHeight
    x1, y1 = data.graphTopLeft[0], data.graphTopLeft[1]
    x2, y2 = data.graphBottomRight[0], data.graphBottomRight[1]
    canvas.create_rectangle(x1, y1, x2, y2, fill="white", width=0)
    drawGraphAxisDescription(canvas, data)
    # bottom left corner : x1, y2  => graph origin
    listOfFileTuples = readMotionFile()
    motionOverTime = condenseMotionFile(listOfFileTuples)
    maximumTime = int(motionOverTime[-1][0])
    maximumMotion = 200000
    createDict(canvas, data, motionOverTime,x1,y2,graphWidth,
        graphHeight,maximumTime,maximumMotion)
    #draw line connecting all the points
    for i in range(len(data.listXs) - 1):
        x5, x6 = data.listXs[i], data.listXs[i+1]
        y5, y6 = data.dictPoints[x5], data.dictPoints[x6]
        lineWidth = 2
        canvas.create_line(x5, y5, x6, y6, fill="red", width=lineWidth)
    #update tog if points moved
    updateMotionTag(data)
    #draw all points that can be moved in graph
    drawSelectedPoint(canvas, data)

def readColorFile() :
    # read file with color information
    result = []
    colorTypeDict = {"bright":0,"light":0,"dull":0,"warm":0,"cold":0}
    txt = open("colorFile.txt")
    txtStr = str(txt.read())
    # whenever one of the color types found, add one in dictionary
    for values in txtStr.split("\n"): 
        if len(values) > 0 :
            colorTypeDict[values[:-1]] += 1
    #determine which type and which temp is most common
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
    else : result += ["cold"]
    # return most frequent color type and temp, list form [type, temp]
    return result

def drawColorType(canvas, data) :
    # draw color charcteristics
    textSize = 50
    step = 6
    x = data.topMargin*step
    y = data.topMargin*10
    # draw color type and temp
    averageColorType = (str(data.colorTypes[data.currentColorTypeIndex]) + 
        "   and   " + str(data.colorTemp[data.currentColorTempIndex]))
    canvas.create_text(x,y, text="%s"%averageColorType, 
        anchor=NW, fill="red", font="Helvetica %d"%(textSize/2))

def drawGenerateMusicButton(canvas, data) :
    # draws button that generates button
    x, y = data.xGenerateMusicButton, data.yGenerateMusicButton
    midX = x + data.widthGenerateMusicButton/2
    midY = y + data.heightGenerateMusicButton/2
    textSize = 25
    canvas.create_rectangle(x,y,data.width, data.height, fill="blue", width=0)
    canvas.create_text(midX,midY, text="Generate music", 
        fill="white", font="Helvetica %d bold"%(textSize))

def drawSelectedMoment(canvas, data) :
    # draw frame corresponding to selected point on graph
    textSize, shift1, shift2 = 20, 100, 40
    x1, y1 = data.graphBottomRight[0]+shift1, data.graphTopLeft[1]
    canvas.create_text(x1,y1, text="Selected moment in video :",anchor=NW, 
        fill="white", font="Helvetica %d"%textSize)
    x2, y2 = x1 + textSize, y1 + shift2
    # determine needed frame based on selected point in graph
    frameNeeded = data.listXs.index(data.selectedPoint[0])
    filename = "./FRAMES/%d.jpg"%frameNeeded
    #open then draw image on canvas
    try : img = Image.open(filename)
    except : 
        filename = "./FRAMES/%d.jpg"%(len(data.listXs)-1)
        img = Image.open(filename)
    if float(img.size[0]) > float(img.size[1]) : imageWidth = 300
    else : 
        imageWidth = 200
        x1 += shift2
    k = imageWidth/float(img.size[0])
    im = img.resize((int(img.size[0]*k),int(img.size[1]*k)), Image.ANTIALIAS)
    canvas.image = ImageTk.PhotoImage(im)
    canvas.create_image(x1-shift2, y2, image=canvas.image, anchor='nw')

def drawGraphAxis(canvas, data) :
    # draw axis for tag graph
    cellWidth, cellHeight = 130, 40
    margin, cells = 170, 3
    textSize, arrowDelta, = 15, 10
    x2, y1 = 250, data.height-margin
    x1, y2 = x2 + cellWidth*cells, y1 + cellHeight*cells
    graphWidth, graphHeight = cellWidth*cells, cellHeight*cells
    # draw lines and arrows
    canvas.create_line(x1,y1-arrowDelta,x1,y2,x2-arrowDelta,y2, fill="green", 
        width=cells)
    canvas.create_line(x2,y2-arrowDelta,x2-arrowDelta,y2,x2,y2+arrowDelta,
        fill="green", width=cells)
    canvas.create_line(x1-arrowDelta,y1,x1,y1-arrowDelta,x1+arrowDelta,y1,
        fill="green", width=cells)
    color, motion = ["bright", "light", "dull"], ["slow", "med", "fast"]
    # draw axis descptition, color on motion
    for i in range(cells) :
        canvas.create_text(x1+textSize*2,y1+cellHeight*i+cellHeight/2, 
            text=color[i], fill="dimgray", font="Helvetica %d"%textSize)
        canvas.create_text(x2+cellWidth/2+(cellWidth*i),y2+textSize,
            text=motion[i], fill="dimgray", font="Helvetica %d"%textSize)

def getColorScheme(data) :
    # determine color or tag rectangle and tagName
    #if color is warm
    if data.currentColorTempIndex == 0 :
        colors = (["coral", "salmon", "yellow", 
            "red", "tomato", "orange",
            "dark red", "orange red", "dark orange", "warm"])
        tagNames = (["tv", "rock 3", "dance", 
            "rock 1", "funk", "rock3",
            "intro", "earth", "ghetto"])
    # if color is cold
    else :
        colors = (["light steel blue", "medium aquamarine", "yellow green", 
            "medium slate blue", "royal blue", "aquamarine",
            "purple", "dark blue", "deep sky blue", "cold"])
        tagNames = (["tv", "acid", "dance", 
            "rock 2", "funk", "house",
            "intro", "earth", "trip"])
    return colors, tagNames

def getIndex(data) :
    # get index for lists based on motion and color characteristics / tag
    i = data.currentColorTypeIndex
    if data.motionTag == "slow" : j = 0
    elif data.motionTag == "med" : j = 1
    elif data.motionTag == "fast" : j = 2
    numCells = 3
    return ((j%numCells) + (i*numCells))

def createGrid(canvas, data, colors, index, cellWidth, cellHeight, tagNames) :
    # draw grid with all tags drawn out
    initX = 250
    margin = 170
    y = data.height-margin
    textSize = 15
    numCells = 3
    # for each possible tag (3x3) draw with corresponding color if selected tag
    for i in range(len(colors)-1):
        if i == index : 
            color = colors[i]
            textColor = "black"
        else : 
            color = "black"
            textColor = "white"
        x1, y1 = initX + cellWidth*(i%numCells), y + cellHeight*((i)/numCells)
        x2, y2 = x1+cellWidth, y1 + cellHeight
        canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        canvas.create_text(x1+cellWidth/2,y1+cellHeight/2,
            text=tagNames[i], fill=textColor, font="Helvetica %d"%textSize)
    # draw graph axis for tags
    drawGraphAxis(canvas, data)

def drawTagRep(canvas, data):
    # draw visual representation of seelcted tags
    index = getIndex(data)
    textSize = 50
    if data.colorTag != None :
        margin = 150
        y = data.height-margin
        canvas.create_text(data.topMargin,y, 
            text="""View currently 
selected tag : """, 
            anchor=NW, fill="white", font="Helvetica %d"%(textSize/2))
        colors, tagNames = getColorScheme(data)
        cellWidth, cellHeight = 130, 40
        # draw grid for each tag
        createGrid(canvas, data, colors, index, cellWidth, cellHeight,tagNames)
            

def drawDiffParam(canvas, data) :
    # draw different visual representatios for each characteristic / tag
    drawColorType(canvas, data)
    drawGenerateMusicButton(canvas, data)
    drawTagRep(canvas, data)
    if data.selectedPoint != None :
        drawSelectedMoment(canvas, data)

def drawShowParameters(canvas, data) :
    # draw show parameters screen
    textSize = 50
    smallTextS = 20
    x = data.topMargin
    y = data.topMargin*2
    # heading
    canvas.create_text(x,y-smallTextS*2,text="We just finished analysing your \
video :", 
        anchor=NW, fill="white", font="Helvetica %d"%textSize)
    canvas.create_text(0,y+smallTextS,text="""\
          Click on characteristics to modifie motion and color parameters""", 
        anchor=NW, fill="white", font="Helvetica %d"%smallTextS)
    motionText = """Motion
in video :"""
    canvas.create_text(x,y+textSize*2, text=motionText, anchor=NW, 
        fill="white", font="Helvetica %d"%(textSize/2))
    # draw motion graph
    drawMotionGraph(canvas, data)
    canvas.create_text(x,data.topMargin*10, text="Main color types : ", 
        anchor=NW, fill="white", font="Helvetica %d"%(textSize/2))
    # draw all characteristic visual representations
    drawDiffParam(canvas, data)

def drawDoneScreen(canvas, data) :
    # draw download / open file screen
    x, y = data.openX, data.openY
    buttonWidth, buttonHeight = data.openWidth, data.openHeight
    textSize = 50
    # draw button
    canvas.create_text(x,y+buttonHeight, 
        text="Your video with music has been downloaded to your files",
        fill="white", font="Helvetica %d"%(textSize/2))
    canvas.create_rectangle(x-buttonWidth/2, y-buttonHeight/2,
        x+buttonWidth/2, y+buttonHeight/2,fill="blue",width=0)
    canvas.create_text(x,y - data.topMargin/2, text="Completed!", fill="white", 
        font="Helvetica %d"%textSize)
    offset = 40
    #draw text
    canvas.create_text(x,y+offset, 
        text="Click here to open video with music", fill="white", 
        font="Helvetica %d"%(textSize/2))

def drawHelpScreen(canvas, data) :
    # draw help screen when help button pressed
    canvas.create_rectangle(0,data.topMargin,data.width,data.height,
        fill="black",width=0)
    textSize = 50
    smallTextS = 20
    x = data.topMargin
    y = smallTextS*10 - textSize
    canvas.create_text(x,y-smallTextS*2,text="HELP!", 
        anchor=NW, fill="red", font="Helvetica %d"%textSize)
    text = """\n
VidWiz generates a polished video with a sound track from your selected videos.

VidWiz will first ask you to select videos from your hard drive.

It will then analyse the video and extract its main characteristics. These \
characteristics\nare then used to generate a matching sound track. 

You will be given the opportunity to modify these characteristics to your \
liking. The videos \nand soundtrack will then be merged and saved to your \
folders.

If you run into errors please make sure that all uploaded videos are:
    - saved in an mp4 format 
    - of the same scale
    - using the same encoder

It may take some time to analyse and generate the new video. 
Please be patient :) 

Please send us your feedback or questions

         - VidWiz Team
            leannbahi+VidWiz@gmail.com
    """ 
    canvas.create_text(x,y,text=text, 
        anchor=NW, fill="white", font="Helvetica %d"%smallTextS)

def allRedraws(canvas, data) :
    # all redraws based on different modes
    if data.mode == "uploadScreen" :
        uploadScreenInit(data)
        drawButtons(canvas, data)
    if data.mode == "waiting" :
        drawWaitingScreen(canvas, data)
    if data.mode == "showParameters" :
        try : x = data,data.xGenerateMusicButton 
        except : showParametersInit(data)
        drawShowParameters(canvas, data)
    if data.mode == "done" :
        doneInit(data)
        drawDoneScreen(canvas, data)
    if data.helpOn == True :
        drawHelpScreen(canvas, data)

def redrawAll(canvas, data):
    # present in all different screens / modes
    canvas.create_rectangle(0,0,data.width, data.height, fill="black", width=0)
    canvas.create_rectangle(0,0,data.width, data.topMargin,fill="blue", width=0)
    textSize = 25
    sText = 15
    canvas.create_text(data.width-data.homeOffset,data.homeOffset, 
        text="Home", anchor=NE, fill="white", font="Helvetica %d"%(sText))
    canvas.create_text(data.width/2,data.homeOffset + sText/2, 
        text="VidWiz", fill="white", font="Helvetica %d"%(textSize))
    canvas.create_text(data.homeOffset,data.homeOffset, 
        text="Help", anchor=NW, fill="white", font="Helvetica %d"%(sText))
    allRedraws(canvas, data)

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 200 # milliseconds
    #create the root
    root = Tk()
    init(data)
    # create the canvas
    global canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1000, 730)

