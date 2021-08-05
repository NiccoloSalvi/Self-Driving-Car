# Lane Detection & Following - Subtraction
    ## Link to yt video:  

import sys

sys.path.append("../classes")
sys.path.append("../lib")

from romi import Romi
from camera import Camera
from servo import Servo

from lSubtractionLib import laneRec
from a_star import AStar

from threading import Thread
import cv2 as cv
import time

def analyseImage():
    camera = Camera(6, 4)
    camera.toPositionBase(50, 80)
    time.sleep(1)
    camera.toPositionTop(10, 20)
    
    for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):
        image = cv.flip(frame.array, -1)
        
        if speed == 12:
            const = 10000
        angleCurve = laneRec(const, image)
        romi.rotateClockwise(angleCurve)
        
        cv.putText(image, "Angle: " + str(angleCurve), (260, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
        cv.imshow("Original Image", image)
        
        camera.rawCapture.truncate(0)
        
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            cv.destroyAllWindows()
            exit()

move = True
speed = 12

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