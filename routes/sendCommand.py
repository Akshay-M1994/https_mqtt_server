from   flask       import Blueprint,request
from   os.path     import exists
from   mqtt2modbus import mqtt2Modbus_ErrorStatus
import json
import os
import secrets

# Defining a blueprint
sendCommand_bp = Blueprint('sendCommand_bp', __name__, template_folder='templates',static_folder='static')

@sendCommand_bp.route("/sendCommand",  methods=['POST'])
def sendCommand():

    #Retrieve command details
    json_command_parameters = request.json

    #Empty json object -> will be populated and forwarded to mqtt_modbus_bridge
    mqtt_command = {
                        "cmdName":"", 
                        "uuid":"",
                        "devId":"",
                        "devProfile":"",
                        "devAdd":0,
                        "regData":[],
                        "result":mqtt2Modbus_ErrorStatus.RESULT_UNKNOWN.value
                   }
    
    #Ensure that json command parameters are valid->refer to the JSON body for the "sendCmd" API URL
    if not "cmdName" in json_command_parameters:
        print("\"cmdName\" key was not found")
        return "cmdName key was not found in json object"
    
    if not "regData" in json_command_parameters:
        print("\"regData\" key was not found")
        return "regData key was not found in json object"

    if not "devId" in json_command_parameters:
        print("\"devId\" key was not found")
        return "devId key was not found in json object"

    #Check if file exists first->find better way to handle this
    if not exists("installed_devices/installed_devices.json"):
        return "installed_devices.json file is missing!"

    try:
        #Check if device is installed
        installedDevicesFile = open(os.getenv('INSTALLED_DEVICES_FILE_PATH'))
    except:
        return "failed to open installed_devices.json"
    
    try:
        #Convert json file to python dictionary
        installedDevicesDict = json.load(installedDevicesFile)
    except:
        return "failed to convert json file to python dictionary"
    
    for device in installedDevicesDict["installedDevices"]:
        if device["devId"] == json_command_parameters["devId"]:
            mqtt_command["devId"] = json_command_parameters["devId"]
            mqtt_command["cmdName"] = json_command_parameters["cmdName"]
            mqtt_command["regData"] = json_command_parameters["regData"]
            mqtt_command["uuid"] = secrets.token_hex(4)
            mqtt_command["devProfile"] = device["deviceModel"]
            mqtt_command["devAdd"] = device["devAdd"]
            break


    from   app         import sendMqttCommand
    #Publish command
    sendMqttCommand(json.dumps(mqtt_command))

    return "None"


    global msgRxd

    if(msgRxd == True):
        msgRxd = False
        return "None"


    #return json.dumps(mqtt_command)