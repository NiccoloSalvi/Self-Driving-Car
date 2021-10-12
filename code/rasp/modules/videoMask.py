# Stop Signal Recognition
    ## Link to yt video: https://youtu.be/6PDmYAtLAKQ?t=179

import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "classes"))

from camera import Camera
from servo import Servo

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "lib"))

import numpy as np
import cv2 as cv
import time

def nothing(x):
    pass

def createTrackbar():
    global trackbarWindowName
    
    trackbarWindowName = "Controls"

    cv.namedWindow(trackbarWindowName)
    cv.createTrackbar("HUE Min", trackbarWindowName, 0, 179, nothing)
    cv.createTrackbar("HUE Max", trackbarWindowName, 179, 179, nothing)
    cv.createTrackbar("SAT Min", trackbarWindowName, 0, 255, nothing)
    cv.createTrackbar("SAT Max", trackbarWindowName, 255, 255, nothing)
    cv.createTrackbar("VALUE Min", trackbarWindowName, 0, 255, nothing)
    cv.createTrackbar("VALUE Max", trackbarWindowName, 255, 255, nothing)

if __name__ == "__main__":
    camera = Camera(6, 4)
    createTrackbar()

    for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):
        image = cv.flip(frame.array, -1)
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

        Hmin = cv.getTrackbarPos("HUE Min", trackbarWindowName)
        Hmax = cv.getTrackbarPos("HUE Max", trackbarWindowName)
        Smin = cv.getTrackbarPos("SAT Min", trackbarWindowName)
        Smax = cv.getTrackbarPos("SAT Max", trackbarWindowName)
        Vmin = cv.getTrackbarPos("VALUE Min", trackbarWindowName)
        Vmax = cv.getTrackbarPos("VALUE Max", trackbarWindowName)
        
        lower = np.array([Hmin, Smin, Vmin])
        upper = np.array([Hmax, Smax, Vmax])
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(image, image, mask=mask)

        mask = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
        hStack = np.hstack([image, mask, result])

        cv.imshow("Images", hStack)
        
        camera.rawCapture.truncate(0)
        
        k = cv.waitKey(1) & 0xFF
        if k == ord("q"):
            cv.destroyAllWindows()
            exit()
