# Traffic Light Recognition
    ## Link to yt video: 

import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "classes"))

from romi import Romi
from camera import Camera
from servo import Servo

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "lib"))

from tlLib import tlRec
from a_star import AStar

from threading import Thread
import numpy as np
import cv2 as cv
import time
    
def analyseImage():
    ##
    stoppedTL = False
    font = cv.FONT_HERSHEY_SIMPLEX
    
    ##
    camera = Camera(6, 4)
    if moveCamera:
        camera.toPositionBase(50, 80)
        time.sleep(1)
        camera.toPositionTop(10, 20)
    
    for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):
        image = cv.flip(frame.array, -1)
        
        colorTL, distanceTL = tlRec(image)
        
        if colorTL:
            if colorTL == 1:
                if stoppedTL:
                    if move:
                        camera.toPositionBase(50, 80)
                        time.sleep(0.3)
                        romi.setSpeed(vel)
                    stoppedTL = False

                    
            if colorTL > 1 and not stoppedTL:
                stoppedTL = True
                prevVel = romi.CentralSpeedRef
                if move:
                    romi.decellerateStop(int(distanceTL) - 20)
                
                    time.sleep(0.5)
                    camera.toPositionBase(80, 50)
                
        print("Color: {} Distance: {}".format(colorTL, distanceTL))
        
        if colorTL:
            if colorTL == 1:
                col = "green"
            elif colorTL == 2:
                col = "yellow"
            elif colorTL == 3:
                col = "red"
                
            printable = "Color: " + col
            if distanceTL:
                printable += " | Distance: " + str(int(distanceTL)) + " cm"
            cv.putText(image, printable, (25, 25), font, 0.75, (255, 0, 0), 2)
        
        cv.imshow("Original Image", image)
        
        camera.rawCapture.truncate(0)
        
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            cv.destroyAllWindows()
            exit()

move = False
moveCamera = False
vel = 8

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
        romi.setSpeed(vel)