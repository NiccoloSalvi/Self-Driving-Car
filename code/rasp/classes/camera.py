# Camera Class #

from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
from servo import Servo
import time

class Camera:
    
    def __init__(self, basePIN, topPIN):
        self.cam = PiCamera()
        self.cam.resolution = (640, 480)
        self.cam.framerate = 32
        self.cam.flash_mode = "on"
        self.cam.brightness = 50
        self.cam.exposure_mode = "auto"
        self.rawCapture = PiRGBArray(self.cam, size=self.cam.resolution)
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.baseServo = Servo(basePIN)
        self.topServo = Servo(topPIN)
        
        time.sleep(0.1)
    
    def toPositionTop(self, startAngle, endAngle):
        self.topServo.start()
        
        inc = startAngle
        while inc <= endAngle:
            self.topServo.Write(inc)
            time.sleep(0.01)
            
            inc += 1
        
        self.topServo.stop()
    
    def toPositionBase(self, startAngle, endAngle):
        self.baseServo.start()
        
        inc = startAngle
        if startAngle < endAngle:
            while inc <= endAngle:
                self.baseServo.Write(inc)
                time.sleep(0.01)
                
                inc += 1
        else:
            while inc >= endAngle:
                self.baseServo.Write(inc)
                time.sleep(0.01)
                
                inc -= 1
                
        self.baseServo.stop()