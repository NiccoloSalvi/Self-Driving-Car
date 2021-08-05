from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

class Alexa:
    def __init__(self):
        self.shadowClient.configureEndpoint("", 8883)
        self.shadowClient = AWSIoTMQTTShadowClient("")
        self.shadowClient.configureCredentials("certs/CA.pem", "certs/private.pem.key", "certs/certificate.pem.crt")
        self.shadowClient.configureConnectDisconnectTimeout(10)
        self.shadowClient.configureMQTTOperationTimeout(5)
        
    def connect(self):
        self.shadowClient.connect()
        print("Connected")
        
        self.device = self.shadowClient.createShadowHandlerWithName("SDC", True)
        
        return self.device
        
    def myShadowUpdateCallback(self, payload, responseStatus, token):
        pass
    
    def uploadSpeed(self, speed):
        self.device.shadowUpdate('{"state": {"reported": {"speed":' + str(speed) + '}}}', self.myShadowUpdateCallback, 5)
