import numpy as np
import cv2 as cv

deltaLine = 5
foundNEW = False
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
        
    ## Upper Pixels ##
    pixelsUp_R = None
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
    
    pts = np.array([[middleWidthImage+2, rowBottom_R], [middleWidthImage+2, rowUp_R], [middleWidthImage + pixelsUp_R[0, 0], rowUp_R], [middleWidthImage + pixelsUp_R[0, 0], rowBottom_R]])
    cv.polylines(out, [pts], True, colorLines["sumR"], thicknessLine)
    pts = np.array([[middleWidthImage + pixelsUp_R[0, 0], rowUp_R], [middleWidthImage + pixelsUp_R[0, 0], rowBottom_R], [middleWidthImage + pixelsBottom_R[0, 0], rowBottom_R]])
    cv.polylines(out, [pts], True, colorLines[tempColor], thicknessLine)
    
    foundNEW = False
    if deltaLine*4 < lastMiddlePixel < hImage and warp[lastMiddlePixel, middleWidthImage + deltaLine] == 0:
        for row in range(deltaLine, lastMiddlePixel, 1):
            pixels = np.array(np.where(warp[row, middleWidthImage+deltaLine:] == 255))
            if len(pixels[0]) != 0:
                foundNEW = True
                rightPixelsUp_2 = pixels
                rightRowUp_2 = row
                
                break

        if foundNEW:
            pts = np.array([[middleWidthImage+rightPixelsUp_2[0, -1], rightRowUp_2], [320+deltaLine, rightRowUp_2], [320+deltaLine, rowUp_R], [320+pixelsUp_R[0, -1], rowUp_R]])
            cv.polylines(out, [pts], True, colorLines["sumR"], 2)
            
            newPos = np.array(np.where(rightPixelsUp_2[0] <= rightPixelsUp_2[0, -1] - 3))
            if len(newPos[0]) != 0:
                pts = np.array([[320+deltaLine, rightRowUp_2], [320+deltaLine, rowUp_R], [320+rightPixelsUp_2[0, newPos[0, -1]], rightRowUp_2]])
                cv.polylines(out, [pts], True, colorLines["diffR"], 2)

                areaGrandeNuova = int(lastMiddlePixel - rightRowUp_2) * (warp.shape[1]/2 - deltaLine)
                smallArea = int((320+deltaLine - rightPixelsUp_2[0, newPos[0, -1]]) * (lastMiddlePixel - rightRowUp_2) / 2)
                rightArea += areaGrandeNuova - smallArea
                
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
    
    pts = np.array([[pixelsUp_L[0, -1], rowUp_L], [middleWidthImage - deltaLine, rowUp_L], [middleWidthImage - deltaLine, rowBottom_L], [pixelsUp_L[0, -1], rowBottom_L]])
    cv.polylines(out, [pts], True, colorLines["sumL"], thicknessLine)
    pts = np.array([[pixelsUp_L[0, -1], rowUp_L], [pixelsUp_L[0, -1], rowBottom_L], [pixelsBottom_L[0, -1], rowBottom_L]])
    cv.polylines(out, [pts], True, colorLines[tempColor], thicknessLine)
    
    foundNEW = False
    if deltaLine*4 < lastMiddlePixel < hImage and warp[lastMiddlePixel, middleWidthImage - deltaLine] == 0:
        for row in range(deltaLine, lastMiddlePixel, 1):
            pixels = np.array(np.where(warp[row, :middleWidthImage - deltaLine] == 255))
            if len(pixels[0]) != 0:
                foundNEW = True
                NEWpixelsUp_L = pixels
                NEWrowUp_L = row
                
                break
            
        if foundNEW:
            pts = np.array([[NEWpixelsUp_L[0, 0], NEWrowUp_L], [middleWidthImage - deltaLine, NEWrowUp_L], [middleWidthImage - deltaLine, rowUp_L], [pixelsUp_L[0, 0], rowUp_L]])
            cv.polylines(out, [pts], True, colorLines["sumL"], thicknessLine)
            
            newPos = np.array(np.where(NEWpixelsUp_L[0] > 3))
            if len(newPos[0]) != 0:
                azz = newPos[0, 0]
            else:
                azz = 2
            
            pts = np.array([[middleWidthImage - deltaLine, NEWrowUp_L], [middleWidthImage - deltaLine, rowUp_L], [NEWpixelsUp_L[0, azz], NEWrowUp_L]])
            cv.polylines(out, [pts], True, colorLines["diffL"], 2)                    
            addedArea = (lastMiddlePixel - NEWrowUp_L) * (middleWidthImage - deltaLine)
            removeArea = (lastMiddlePixel - deltaLine - NEWpixelsUp_L[0, azz]) * (lastMiddlePixel - NEWrowUp_L) / 2
            leftArea += addedArea - removeArea
            pts = np.array([[middleWidthImage - deltaLine, NEWrowUp_L], [middleWidthImage - deltaLine, rowUp_L], [NEWpixelsUp_L[0, azz], NEWrowUp_L]])
            cv.polylines(out, [pts], True, colorLines["diffL"], 2)
            
            addedArea = (lastMiddlePixel - NEWrowUp_L) * (middleWidthImage - deltaLine)
            removeArea = (lastMiddlePixel - deltaLine - NEWpixelsUp_L[0, azz]) * (lastMiddlePixel - NEWrowUp_L) / 2
            leftArea += addedArea - removeArea
    
    """ Lane Following """
    deltaArea = rightArea - leftArea 
    return int(round(deltaArea/k))

def getWarpingImage(frame, pts, wImage, hImage):
    pts1 = np.float32(pts)
    pts2 = np.float32([[0, 0], [wImage, 0], [0, hImage], [wImage, hImage]])

    matrix = cv.getPerspectiveTransform(pts1, pts2)
    warp = cv.warpPerspective(frame, matrix, (wImage, hImage))

    return warp

def getWarpingPoints(pts, wT, hT):
    wTop, hTop, wBottom, hBottom = pts
    
    return np.float32([(wTop, hTop), (wT - wTop, hTop), (wBottom, hBottom), (wT - wBottom, hBottom)])