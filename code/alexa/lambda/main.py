import iot

def buildSpeechletResponse(OUT, endSession):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": OUT
        },
        "shouldEndSession": endSession
    }

def buildResponse(response):
    return {
        "version": "1.0",
        "response": response
    }
    
def welcomeHandler():
    OUT = "Bentornato, come posso esserti d'aiuto?"
    endSession = False
    
    return buildResponse(buildSpeechletResponse(OUT, endSession))

def startHandler():
    OUT = "La macchina sta partendo"
    command = { "start": True }
    iot.update("desired", command)
        
    endSession = True
    
    return buildResponse(buildSpeechletResponse(OUT, endSession))
    
def stopMacchinaHanlder():
    OUT = "La macchina si sta fermando"
    command = { "start": False }
    iot.update("desired", command)
        
    endSession = True
    
    return buildResponse(buildSpeechletResponse(OUT, endSession))
    
def getSpeedHandle():
    currentSpeed = iot.get("speed")
    OUT = "Sto viaggiando a " + str(currentSpeed) + "km/h"
    endSession = False
    
    return buildResponse(buildSpeechletResponse(OUT, endSession))
    
def accHandler():
    OUT = "Ok, accelero"
    command = { "speed": 10 }
    iot.update("desired", command)
        
    endSession = True
    
    return buildResponse(buildSpeechletResponse(OUT, endSession))
    
def decHandler():
    OUT = "Ok, decelero"
    command = { "speed": 6 }
    iot.update("desired", command)
        
    endSession = True
    
    return buildResponse(buildSpeechletResponse(OUT, endSession))
    
def helpHandler():
    OUT = "Puoi chiedermi la velocità attuale, l'ultimo segnale riconosciuto, di accelerare, di fermarsi e di ripartire"
    endSession = False
    
    return buildResponse(buildSpeechletResponse(OUT, endSession))

def stopHandler():
    OUT = "A presto"
    endSession = True
    
    return buildResponse(buildSpeechletResponse(OUT, endSession))

def onLaunch(launch_request, session):
    return welcomeHandler()

def onIntent(intRequest, session):
    intent = intRequest["intent"]
    intName = intRequest["intent"]["name"]

    if intName == "startIntent":
        return startHandler()
    elif intName == "fermaIntent":
        return stopMacchinaHanlder()
    elif intName == "acceleroIntent":
        return accHandler()
    elif intName == "deceleroIntent":
        return decHandler()
    elif intName == "getSpeedIntent":
        return getSpeedHandle()
    elif intName == "AMAZON.HelpIntent":
        return helpHandler()
    elif intName == "AMAZON.CancelIntent" or intName == "AMAZON.StopIntent":
        return stopHandler()
    else:
        raise ValueError("Invalid intent")

def lambda_handler(event, context):
    if event['request']['type'] == "LaunchRequest":
        return onLaunch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return onIntent(event['request'], event['session'])