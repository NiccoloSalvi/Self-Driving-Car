# Stop Signal Recognition
    ## Link to yt video:  

import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "classes"))

from romi import Romi
from camera import Camera
from servo import Servo

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "lib"))

from stopLib import stopRec
from a_star import AStar

from threading import Thread
import cv2 as cv
import time
import queue

def analyseImage():
    # #
    laneQueue = queue.Queue()
    font = cv.FONT_HERSHEY_SIMPLEX
    count = 0
    stopped = False
    foundTH = False
    laneTH = None
    
    ##
    camera = Camera(6, 4)
    camera.toPositionBase(50, 80)
    time.sleep(1)
    camera.toPositionTop(10, 20)
    
    for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):
        image = cv.flip(frame.array, -1)
        
        distance = stopRec(image)
        if distance and distance < 40 and foundTH is False:
            if move:
                foundTH = True
                
                laneTH = Thread(target=lambda laneQueue, arg: laneQueue.put(romi.decelerateStop(arg)), args=(laneQueue, distance))
                laneTH.start()
        
        if romi.CentralSpeedRef == 0:
            stopped = True
        
        cv.putText(image, "Distance: " + str(distance) + " cm", (25, 25), font, 0.75, (255,0,0), 2)
        # print("Distance: {}".format(distance))
        
        if stopped:
            if count == 10:
                if move:
                    romi.setSpeed(speed)
                
                stopped = False
                count = 0
            count += 1
        
        cv.imshow("Original Image", image)
        
        camera.rawCapture.truncate(0)
        
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            cv.destroyAllWindows()
            exit()

move = False
speed = 10

if __name__ == "__main__":
    global romi
    
    """ Computer Vision """
    CV = Thread(target=analyseImage)
    CV.start()
    
    """ Romi """
    romi = Romi(AStar())
    romiThread = Thread(target=romi.run)
    romiThread.start()
    
    if move:
        time.sleep(3)    
        romi.setSpeed(speed)