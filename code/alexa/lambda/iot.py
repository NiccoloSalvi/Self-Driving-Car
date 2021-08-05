import boto3
import json
import os

thingName = "SDC"
host = os.environ.get("")
port = os.environ.get("443")

def update(field, value):
    payload_dict = {"state": {field: value}}
    JSON_payload = json.dumps(payload_dict)
    shadow_client = boto3.client("iot-data", "eu-west-1")
    shadow_client.update_thing_shadow(thingName=thingName, payload=JSON_payload)
    
def get(field):
    shadow_client = boto3.client("iot-data", "eu-west-1")
    response = shadow_client.get_thing_shadow(thingName=thingName)
    streamingBody = response["payload"]
    jsonState = json.loads(streamingBody.read())
    
    return jsonState["state"]["reported"][field]