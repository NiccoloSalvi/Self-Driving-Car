import numpy as np
import cv2 as cv

deltaLine = 5
thicknessLine = 2
colorLines = {
    "sumR": (0, 0, 255),
    "diffR": (26, 140, 255),
    "sumL": (255, 0, 0),
    "diffL": (255, 255, 0)
}

def laneRec(k, image):
    ptsToWarp = getWarpingPoints([95, 80, 0, 240], 640, 480)
    
    """ Loop Variables """
    hImage, wImage, cImage = image.shape
    middleWidthImage = int(wImage/2)
    
    """ Image Transformation """
    ROI = image[int(image.shape[0]/2):, :]
    gray = cv.cvtColor(ROI, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    
    # cv.imshow("thresh", thresh)
    
    out = getWarpingImage(ROI, ptsToWarp, wImage, hImage)
    warp = getWarpingImage(thresh, ptsToWarp, wImage, hImage)
    
    """ Lane Detection Algorithm """ 
    cv.line(warp, (0, 0), (0, hImage), (255, 255, 255), 3)
    cv.line(warp, (wImage, 0), (wImage, hImage), (255, 255, 255), 3)
    
    middleWhitePixels = np.array(np.where(warp[:, middleWidthImage] == 255))
    if len(middleWhitePixels[0]) > 0:
        lastMiddlePixel = middleWhitePixels[0, -1] + deltaLine
    else:
        lastMiddlePixel = deltaLine
        
    # Right Side #
    ## Bottom Pixels ##
    for row in range(hImage-deltaLine, deltaLine, -1):
        pixels = np.array(np.where(warp[row, middleWidthImage:] == 255))
        if len(pixels[0]) != 0:
            pixelsBottom_R = pixels
            rowBottom_R = row
            
            break
    
    pixelsUp_R = None
    ## Upper Pixels ##
    for row in range(lastMiddlePixel, hImage-deltaLine, 1):
        pixels = np.array(np.where(warp[row, middleWidthImage:] == 255))
        if len(pixels[0]) != 0:
            pixelsUp_R = pixels
            rowUp_R = row
            
            break
    
    ## Area ##
    if pixelsUp_R is None or (pixelsUp_R is not None and len(pixelsUp_R[0]) == 0):
        return 0
    rightArea = pixelsUp_R[0, 0] * (rowBottom_R - rowUp_R)
    if pixelsUp_R[0, 0] > pixelsBottom_R[0, 0]:
        rightArea -= (pixelsUp_R[0, 0] - pixelsBottom_R[0, 0]) * (rowBottom_R - rowUp_R) / 2
        tempColor = "diffR"
    else:
        rightArea += (pixelsBottom_R[0, 0] - pixelsUp_R[0, 0]) * (rowBottom_R - rowUp_R) / 2
        tempColor = "sumR"
    
    # Left Side #
    ## Bottom Pixels ##
    for row in range(hImage-deltaLine, deltaLine, -1):
        pixels = np.array(np.where(warp[row, :middleWidthImage] == 255))
        if len(pixels[0]) != 0:
            pixelsBottom_L = pixels
            rowBottom_L = row
            
            break
    
    ## Upper Pixels ##
    for row in range(lastMiddlePixel, hImage-deltaLine, 1):
        pixels = np.array(np.where(warp[row, :middleWidthImage] == 255))
        if len(pixels[0]) != 0:
            pixelsUp_L = pixels
            rowUp_L = row
            
            break

    ## Area ##
    leftArea = (middleWidthImage - pixelsUp_L[0, -1]) * (rowBottom_L - rowUp_L)
    if pixelsUp_L[0, -1] < pixelsBottom_L[0, -1]:
        leftArea -= (pixelsBottom_L[0, -1] - pixelsUp_L[0, -1]) * (rowBottom_L - rowUp_L) / 2
        tempColor = "diffL"
    else:
        leftArea += (pixelsUp_L[0, -1] - pixelsBottom_L[0, -1]) * (rowBottom_L - rowUp_L) / 2
        tempColor = "sumL"
    
    """ Lane Following """
    if leftArea > rightArea:
        curve =((rightArea/leftArea)-1)*k
        if curve > 25:
            curve = 25
    else:
        curve = -((leftArea/rightArea)-1)*k
        if curve < -25:
            curve = -25
            
    return int(round(curve))

def getWarpingImage(frame, pts, wImage, hImage):
    pts1 = np.float32(pts)
    pts2 = np.float32([[0, 0], [wImage, 0], [0, hImage], [wImage, hImage]])

    matrix = cv.getPerspectiveTransform(pts1, pts2)
    warp = cv.warpPerspective(frame, matrix, (wImage, hImage))

    return warp

def getWarpingPoints(pts, wT, hT):
    wTop, hTop, wBottom, hBottom = pts
    
    return np.float32([(wTop, hTop), (wT - wTop, hTop), (wBottom, hBottom), (wT - wBottom, hBottom)])
