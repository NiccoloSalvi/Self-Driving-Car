from nn import digitRecognizer

import torchvision.transforms as transforms
import torch.nn as nn
import torch

import numpy as np
import cv2 as cv

def getValue(digits, ROI):
    net = digitRecognizer(1024, 100, 10)
    # net.load_state_dict(torch.load("../lib/myModel.pt"))
    net.load_state_dict(torch.load("lib/myModel.pt"))
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    net = net.to(device)
    limit = ""
    
    for step, (x, y, w, h) in enumerate(digits):
        img = ROI[y:y+h, x:x+w]
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        res = cv.resize(gray, (32, 32))
        
        tens = transforms.ToTensor()(res)
        images = tens.reshape(-1, 32*32).to(device)
        outputs = net(images)
        _, predicted = torch.max(outputs, 1)
        
        limit += str(predicted.item())
    
    if limit != "":
        return int(limit)
    return None
                    
def slRec(image):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    
    lr = np.array([158, 93, 104])
    ur = np.array([179, 170, 195])
    mask = cv.inRange(hsv, lr, ur)
    
    _, cnt, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    areas = []
    if len(cnt) > 0:
        for c in cnt:
            areas.append(cv.contourArea(c))
        
        index = np.argmax(areas)
        x, y, w, h = cv.boundingRect(cnt[index])
        cv.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)
        ROI = image[y:y+h, x:x+w]
        
        return getValues(ROI)
    return None, None

def getDigits(ROI):
    h, w, c = ROI.shape

    wMiddle = int(w/2)
    hMidle = int(h/2)
    radius = int(0.75 * hMidle)

    mask = np.zeros_like(ROI)
    mask = cv.circle(mask, (wMiddle, hMidle), radius, (255, 255, 255), cv.FILLED)
    result = cv.bitwise_and(ROI, mask)

    areaCircle = np.pi * np.power(radius, 2)

    gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)
    _, th = cv.threshold(gray, 70, 255, cv.THRESH_BINARY)
    _, cnt, _ = cv.findContours(th, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    
    rects = []
    cnt = cnt[::-1]
    for step, c in enumerate(cnt[:3]):
        a = cv.contourArea(c)
        
        if not areaCircle-200 < a < areaCircle+200 and a > 100:
            x, y, w, h = cv.boundingRect(c)
            rects.append([x, y, w, h])
            
    return sorted(rects)

def getValues(ROI):
    rD = 25 # real distance
    fW = 80 # frame width
    rW = 4.2 # real width
    fL = fW * rD / rW
    
    distSL = rW * fL / ROI.shape[0]
    
    if distSL < 40:
        limit = getValue(getDigits(ROI), ROI)
        if limit:
            if limit == 90:
                return distSL, 90
            if limit == 50:
                return distSL, 50
    return None, None