import numpy as np
import cv2 as cv

def canny(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5, 5), 0)
    canny = cv.Canny(blur, 85, 85)
    
    return canny

def detectStop(frame):
    # stopHaarcascade = "../haarcascades/stop.xml"
    stopHaarcascade = "haarcascades/stop.xml"
    signalCascade = cv.CascadeClassifier(stopHaarcascade)
    
    signal = signalCascade.detectMultiScale(frame, 1.05, 3)
    if len(signal) > 0:
        for step, s in enumerate(signal):
            # cv.imshow(str(step), frame[s[1] : (s[1] + s[3]), s[0] : (s[0] + s[2])])
            return frame[s[1] : (s[1] + s[3]), s[0] : (s[0] + s[2])], s[0], s[1]
    return None, None, None

def stopRec(image):
    rD = 25 # real distance
    fW = 90 # frame width
    rW = 4.3 # real width
    
    fL  = fW * rD / rW

    ROI, xROI, yROI = detectStop(image)
    if ROI is not None:
        hsv = cv.cvtColor(ROI, cv.COLOR_BGR2HSV)
    
        lr = np.array([150, 100, 80])
        # ur = np.array([179, 195, 165])
        ur = np.array([179, 165, 215])
        mask = cv.inRange(hsv, lr, ur)
        
        # cv.imshow("mask", mask)
        
        _, cnt, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        
        areas = []
        if len(cnt) > 0:
            for c in cnt:
                areas.append(cv.contourArea(c))
            
            maxVal = max(areas)
            if maxVal > 1000:
                index = areas.index(maxVal)
                
                x, y, wRectangle, h = cv.boundingRect(cnt[index])
                cv.rectangle(image, (xROI + x, yROI + y), (xROI + x+wRectangle, yROI + y+h), (255, 255, 0), 2)
                
                distance = rW * fL / wRectangle
                return int(round(distance, 1)) - 20