# Speed Limit Signal Recognition
    ## Link to yt video: https://youtu.be/6PDmYAtLAKQ?t=148

import sys
import os

sys.path.append("../classes")
sys.path.append("../lib")

from camera import Camera
from servo import Servo
from romi import Romi

from slLib import *
from a_star import AStar

from threading import Thread
import numpy as np
import cv2 as cv
import time

def analyseImage():
    ##
    camera = Camera(6, 4)
    """camera.toPositionBase(50, 80)
    time.sleep(1)
    camera.toPositionTop(10, 20)"""
    
    for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):
        image = cv.flip(frame.array, -1)
        
        distSL, speedLimit = slRec(image)
        if distSL:
            if speedLimit == 50:
                print(speedLimit)
                if move:
                    romi.accellerate(distSL, 6)
            elif speedLimit == 90:
                print(speedLimit)
                if move:
                    romi.accellerate(distSL, 10)
            else:
                print("no")
        else:
            print("no")
                
        cv.imshow("image", image)
        
        camera.rawCapture.truncate(0)
        
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            cv.destroyAllWindows()
            exit()
    
vel = 10
move = False

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