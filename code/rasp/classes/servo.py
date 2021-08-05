# Servo Motor Class #

import RPi.GPIO as GPIO
import time

class Servo:
    
    def __init__(self, pin):
        self.OFFSET_DUTY = 0.5
        self.SERVO_MIN_DUTY = 2.5 + self.OFFSET_DUTY
        self.SERVO_MAX_DUTY = 12.5 + self.OFFSET_DUTY
        self.PIN = pin
        
        GPIO.setup(self.PIN, GPIO.OUT)
        self.P = GPIO.PWM(self.PIN, 50)
    
    # move servo motor # 
    def Write(self, angle):
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        
        self.P.ChangeDutyCycle(map(angle, 0, 180, self.SERVO_MIN_DUTY, self.SERVO_MAX_DUTY))
        time.sleep(0.02)
    
    # start servo motor #
    def start(self):
        self.P.start(0)
    
    # stop servo motor #
    def stop(self):
        self.P.ChangeDutyCycle(0)

def map(value, fromLow, fromHigh, toLow, toHigh):
        return (toHigh - toLow) * (value - fromLow) / (fromHigh - fromLow) + toLow