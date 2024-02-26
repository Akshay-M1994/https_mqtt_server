from   flask             import Blueprint,request
from   os.path           import exists
from   mqtt2modbus       import mqtt2Modbus_ErrorStatus
from   mqtt2modbus       import modbusMqttMsg
from   installed_devices import installed_devices
from   device_profiles   import device_profiles
import json
import os
import secrets
import time

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
        print("\"cmdName\" key was not found")
        return "cmdName key was not found in json object"
    
    if not "regData" in json_command_parameters:
        print("\"regData\" key was not found")
        return "regData key was not found in json object"

    if not "devId" in json_command_parameters:
        print("\"devId\" key was not found")
        return "devId key was not found in json object"

    device = installed_devices.isDeviceInstalled(json_command_parameters["devId"])
    
    if(device != None):

        deviceProfile = device_profiles.isDeviceProfilePresent(device["deviceModel"])

        if(deviceProfile != None):

            for cmd in deviceProfile["cmdList"]:
                if cmd["cmdName"] == json_command_parameters["cmdName"]:
        
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
                    break
        else:
            return "Device Profile Not Found!"
    else:
        return "Device Not Installed!"



    #Publish request using mqtt client created in app.py
    import app
    publish_result = app.mqtt_client.publish(os.getenv('MODBUS_CMD_TOPIC'), json.dumps(mqtt_command))

    #Variable to track timeout timer
    timeLeft = 5

    #Wait for response to be received from mqtt_modbus_bridge
    while((app.msgRxd != True) and (timeLeft != 0)):
        time.sleep(0.035)
        timeLeft-=1


    #Wait for message to be received before returning response
    if(app.msgRxd == True):
        app.msgRxd = False
        return json.dumps(app.mqttJsonMsg)
    
    return "None"

