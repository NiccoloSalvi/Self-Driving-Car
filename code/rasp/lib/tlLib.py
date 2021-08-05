import numpy as np
import cv2 as cv

def detectColor(ROI, w, h, dist):
    middleW = int(w/2)
    
    gray = cv.cvtColor(ROI, cv.COLOR_BGR2GRAY)
    _, th = cv.threshold(gray, 250, 255, cv.THRESH_BINARY)
    # cv.imshow("th", th)
    _, cnt, _ = cv.findContours(th, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    areas = {}
    if len(cnt) > 0:
        for c in range(len(cnt)):
            M = cv.moments(cnt[c])
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                if middleW - 10 < cx < middleW + 10:
                    rect = cv.minAreaRect(cnt[c])
                    ar = rect[1][0] * rect[1][1]
                    if 30 < ar < 500:
                        areas[c] = ar
        
        if not bool(areas):
            return None, None
        
        indexMax = max(areas.keys(), key=(lambda k: areas[k]))
        rect = cv.minAreaRect(cnt[indexMax])
        box = cv.boxPoints(rect)
        box = np.int0(box)
        cv.drawContours(ROI, [box], 0, (255, 255, 0), 2)
        
        perc = 100 - (rect[0][1] / h * 100)
        if perc < 30:
            return 1, None
        elif 35 < perc < 50:
            return 2, dist
        elif 55 < perc < 70:
            return 3, dist
    return None, None

def tlRec(image):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    
    # lr = np.array([0, 122, 132])
    # ur = np.array([179, 255, 255])
    
    lr = np.array([0, 125, 75])
    ur = np.array([29, 255, 255])
    
    mask = cv.inRange(hsv, lr, ur)
    
    _, cnt, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # cv.drawContours(image, cnt, -1, (0, 0, 255), 2)
    
    if len(cnt) > 0:
        areas = {}
        for c in range(len(cnt)):
            x, y, w, h = cv.boundingRect(cnt[c])
            ar = w*h
            if ar > 500:
                areas[c] = ar
        
        if not bool(areas):
            return None, None
        
        indexMax = max(areas.keys(), key=(lambda k: areas[k]))
        x, y, w, h = cv.boundingRect(cnt[indexMax])
        cv.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)
        
        # calcolo dist
        rD = 25 # real distance
        fW = 84 # frame height
        rW = 6.5 # real height # 4.5
        fL = fW * rD / rW
        
        dist = rW * fL / h
        if dist < 40:
            return detectColor(image[y:y+h, x:x+w], w, h, dist)
    return None, None