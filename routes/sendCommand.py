from   flask                 import Blueprint,request
from   os.path               import exists
from   mqtt2modbus           import mqtt2Modbus_ErrorStatus
from   mqtt2modbus           import modbusMqttMsg
from   installed_devices.src import installed_devices
from   device_profiles.src   import device_profiles
from   debug_nid             import debug
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
    mqtt_command = modbusMqttMsg.blankMsg()

    #Ensure that json command parameters are valid->refer to the JSON body for the "sendCmd" API URL
    if not "cmdName" in json_command_parameters:
        debug.logging.debug("\"cmdName\" key was not found")
        return "cmdName key was not found in json object"
    
    if not "regData" in json_command_parameters:
        debug.logging.debug("\"regData\" key was not found")
        return "regData key was not found in json object"

    if not "devId" in json_command_parameters:
        debug.logging.debug("\"devId\" key was not found")
        return "devId key was not found in json object"

    device = installed_devices.isDeviceInstalled(json_command_parameters["devId"])
    if device == None:
          debug.logging.debug("Device Not Installed!") 
          return "Device Not Installed!"
     
    deviceProfile = device_profiles.isDeviceProfilePresent(device["deviceModel"])
    if deviceProfile == None:
          debug.logging.debug("Device Profile Not Found!")
          return "Device Profile Not Found!"
     
    cmd = isCommandValid(deviceProfile,json_command_parameters["cmdName"])
    if(cmd == None):
          debug.logging.debug("Command is not part of devices command set")
          return "Command is not part of devices command set"

    mqtt_command = modbusMqttMsg.CreateMsg(
                                            cmd["cmdName"],
                                            secrets.token_hex(4),
                                            device["devId"],
                                            device["deviceModel"],
                                            cmd["modfunc"],
                                            device["devAdd"],
                                            cmd["regAdd"],
                                            cmd["regCount"],
                                            json_command_parameters["regData"] if cmd["cmdType"] == "W" else cmd["regData"],
                                            mqtt2Modbus_ErrorStatus.RESULT_UNKNOWN.value
                                           )

    #Publish request using mqtt client created in app.py
    import app
    publish_result = app.mqtt_client.publish(os.getenv('MODBUS_CMD_TOPIC'), json.dumps(mqtt_command))
 
    #Wait for msg received semaphore to be released
    if app.mqttMsgRxdSemaphore.acquire(blocking=True,timeout=0.250) != True:
        debug.logging.debug("Failed to acquire message received semaphore")
        return "None"

    #Wait for message to be received before returning response
    return json.dumps(app.mqttJsonMsg)


def isCommandValid(deviceProfile:dict,cmdName:str)->dict|None:
    for cmd in deviceProfile["cmdList"]:
        if cmd["cmdName"] == cmdName:
            return cmd
        
    return None