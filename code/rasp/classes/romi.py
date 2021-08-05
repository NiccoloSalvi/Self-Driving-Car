import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "lib"))

from a_star import AStar
import time

# Romi Pololu 32u4 Class #

# StatusWord
ButtonC_Pressed = 0x0001
ButtonB_Pressed = 0x0002
ButtonA_Pressed = 0x0004

# ControlWord
ResetAll = 0x8000
ResetEncoders = 0x4000
ResetPosition = 0x2000
ResetRotation = 0x1000
RedLedOn = 0x0004
GreenLedOn = 0x0002
YellowLedOn = 0x0001

class Romi:
    
    def __init__(self, aStar):
        self.running = True
        self.ReadMotionControlData = 0
        self.ControlWord = 1
        self.LeftMotorSpeedRef = 0
        self.RightMotorSpeedRef = 0
        self.CentralSpeedRef = 0
        self.CentralDeltaPosRef = 0
        self.CentralDeltaRotRef = 0
        self.a_star = aStar
    
    # stop running romi #
    def stopRunning(self):
        self.running = False

    def readStatusWord(self):
        return int.from_bytes(self.ReadMotionControlData[0:2], byteorder='little', signed=False)
    
    # read battery's voltage #
    def readBatteryVoltage(self):
        return int.from_bytes(self.ReadMotionControlData[2:4], byteorder='little', signed=False)
    
    # left encoder reader #
    def readLeftEncoder(self):
        return int.from_bytes(self.ReadMotionControlData[4:6], byteorder='little', signed=True)
    
    # right encoder reader #
    def readRightEncoder(self):
        return int.from_bytes(self.ReadMotionControlData[6:8], byteorder='little', signed=True)
    
    # actual speed #
    def readActualspeed(self):
        return int.from_bytes(self.ReadMotionControlData[8:10], byteorder='little', signed=True)
    
    # actual position #
    def readActualPosition(self):
        return int.from_bytes(self.ReadMotionControlData[10:14], byteorder='little', signed=True)
    
    # actual rotation #
    def readActualRotation(self):
        return int.from_bytes(self.ReadMotionControlData[14:16], byteorder='little', signed=True)

    # stop romi #
    def stop(self):
        self.CentralSpeedRef = 0
    
    # set speed untill the end #
    def setSpeed(self, speed):
        self.CentralSpeedRef = speed

    # move romi forward #
    def moveForward(self, deltapos):
        self.CentralDeltaPosRef = 0
        time.sleep(0.051)
        self.CentralDeltaPosRef = deltapos
    
    # move romi backward #
    def moveBackward(self, deltapos):
        self.CentralDeltaPosRef = 0
        time.sleep(0.051)
        self.CentralDeltaPosRef = -deltapos
    
    # rotate clockwise #
    def rotateClockwise(self, deltarot):
        self.CentralDeltaRotRef = 0
        time.sleep(0.051)
        self.CentralDeltaRotRef = deltarot
    
    # rotate anti-clockwise #
    def rotateAnticlockwise(self, deltarot):
        self.CentralDeltaRotRef = 0
        time.sleep(0.051)
        self.CentralDeltaRotRef = -deltarot
    
    # accelerate #
    def accelerate(self, sts, speed):
        deltaV = speed - self.CentralSpeedRef
        if deltaV != 0:
            tts = abs(sts / deltaV)
            acc = deltaV / tts
            
            deltaT = tts/100
            t = 0
            
            v = self.CentralSpeedRef
            if deltaV > 0:
                while (v < speed):
                    t += deltaT
                    v += acc * t
                    self.setSpeed(int(round(v, 0)))
                    
                    time.sleep(deltaT)
            else:
                while (v > speed):
                    t += deltaT
                    v += acc * t
                    self.setSpeed(int(round(v, 0)))
                    
                    time.sleep(deltaT)
    
    # decelerate # 
    def decelerateStop(self, sts):
        acc = (self.CentralSpeedRef ** 2) / (2 * sts)
        tts = (-self.CentralSpeedRef) / (-acc) # time to stop
        
        deltaT = tts/100
        t = tts
        
        v = self.CentralSpeedRef
        while (t > 0):
            t -= deltaT
            v = acc * t
            self.setSpeed(int(round(v, 0)))
            
            time.sleep(deltaT)
        
        return True
            
    def run(self):
        while self.running:
            # Read data from RomiU32
            self.ReadMotionControlData = self.a_star.read_unpack(0, 16, 'BBBBBBBBBBBBBBBB')

            # Write data to RomiU32
            self.ControlWord ^= YellowLedOn
            self.a_star.write_pack(16, 'Hhhhhh', self.ControlWord, self.LeftMotorSpeedRef, self.RightMotorSpeedRef,
                                   self.CentralSpeedRef, self.CentralDeltaPosRef, self.CentralDeltaRotRef)

            time.sleep(0.05)