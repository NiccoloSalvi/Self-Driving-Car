import sys

sys.path.append("classes")
sys.path.append("lib")

from romi import Romi
from camera import Camera
from servo import Servo

# from lSubtractionLib import laneRec # lane detection & following module - subtraction
from lDivisionLib import laneRec # lane detection & following module - division
from stopLib import stopRec # stop recognition module
from slLib import slRec # speed limit signal module
from tlLib import tlRec # traffic light recognition module

from a_star import AStar

from threading import Thread
import cv2 as cv
import time

def analyseImage():
    global speed, move, maxSpeed, minSpeed, moveCamera, romi
    
    countStop = 0
    stopped = False
    stoppedTL = False
    
    camera = Camera(6, 4)
    if moveCamera:
        camera.toPositionBase(50, 80)
        time.sleep(1)
        camera.toPositionTop(10, 20)

    for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):
        image = cv.flip(frame.array, -1)
        
        foundStop = False
        foundTL = False
        foundSL = False
        foundTH = False
        distStop = ""
        valueSL = ""
        distTL = ""
        colTL = ""
        
        if not stoppedTL:
            if speed == maxSpeed:
                # const = 15000 # subtraction algo
                const = 13 # division algo
            if speed == minSpeed:
                # const = 10000 # subtraction algo
                const = 8 # division algo
                
        colorTL, distanceTL = tlRec(image)
        
        if not stopped and not stoppedTL:
            angle = laneRec(const, image)
    
            if angle < 0:
                dire = "L"
            elif angle == 0:
                dire = "F"
            else:
                dire = "R"
                
            if move:
                romi.rotateClockwise(angle)
            
            distanceS = stopRec(image)
            if distanceS:
                if distanceS < 40 and foundTH is False:
                    distStop = str(distanceS) + " cm"
                    if move:
                        foundTH = True
                
                        decelerateTH = Thread(target=romi.decelerateStop, args=(distanceS,))
                        decelerateTH.start()
                foundStop = True
            
            if romi.CentralSpeedRef == 0:
                stopped = True

            distSL, speedLimit = slRec(image)
            if distSL:
                if speedLimit == 50 or speedLimit == 90:
                    if move:
                        if speedLimit == 50:
                            speed = minSpeed
                            accelerateTH = Thread(target=romi.accelerate, args=(distSL, speed))
                            accelerateTH.start()
                        
                        else:
                            speed = maxSpeed
                            accelerateTH = Thread(target=romi.accelerate, args=(distSL, speed))
                            accelerateTH.start()

                    valueSL = str(speedLimit) + " km/h"
                foundSL = True
        
        if colorTL:
            foundTL = True
            distTL = str(distanceTL) + " cm"
            if colorTL == 1:
                colTL = "G"
                if stoppedTL:
                    if move:
                        camera.toPositionBase(50, 80)
                        time.sleep(0.5)
                        romi.setSpeed(speed)
                    stoppedTL = False
            
            if colorTL > 1:
                if colorTL == 2:
                    colTL = "Y"
                else:
                    colTL = "R"
                if not stoppedTL:
                    stoppedTL = True
                    if move:
                        decelerateTH = Thread(target=romi.decelerateStop, args=(distanceTL - 20,))
                        decelerateTH.start()
                        
                        time.sleep(0.5)
                        camera.toPositionBase(80, 50)
     
        if stopped:
            if countStop == 10 and move:
                if move:
                    romi.setSpeed(speed)
                
                foundTH = False
                stopped = False
                countStop = 0
            countStop += 1
            
        if not stopped and not stoppedTL:
            cv.putText(image, "Angle: " + str(angle), (50, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2, cv.LINE_AA)
        if foundStop:
            cv.putText(image, "Dist to Stop: " + str(distStop), (50, 75), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2, cv.LINE_AA)
        if foundTL:
            cv.putText(image, "Color TL: " + str(colTL), (50, 100), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2, cv.LINE_AA)
        if foundSL:
            cv.putText(image, "Value SL: " + str(valueSL), (50, 125), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2, cv.LINE_AA)
                
        print("**** Lane ****\n\tDirection: {}\n\tAngle: {}".format(dire, angle))
        print("**** Stop ****\n\tFound: {}\n\tDistance: {}".format(foundStop, distStop))
        print("**** Traffic Light ****\n\tFound: {}\n\tDistance: {}\n\tColor: {}".format(foundTL, distTL, colTL))
        print("**** Speed Limit ****\n\tFound: {}\n\tValue: {}".format(foundSL, valueSL))
        print("---------------------------------------")
        
        cv.imshow("Original Image", image)
        
        camera.rawCapture.truncate(0)
        
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            cv.destroyAllWindows()
            exit()

if __name__ == "__main__":
    global romi, speed, move, maxSpeed, minSpeed, moveCamera
    
    move = True
    moveCamera = True
    
    maxSpeed = 10
    minSpeed = 6
    speed = maxSpeed
    
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