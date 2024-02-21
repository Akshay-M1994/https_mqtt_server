from   flask_mqtt import Mqtt
from   os.path    import exists
from   flask      import Flask, request
from   dotenv     import load_dotenv
from   enum       import Enum
from mqtt2modbus import mqtt2Modbus_ErrorStatus
import os,binascii
import secrets
import json

#Load environment variable file
load_dotenv()

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = '192.168.1.100'     # IP Address of MQTT broker
app.config['MQTT_BROKER_PORT'] = 1884               # Set Port used for MQTT comms.
app.config['MQTT_USERNAME'] = ''                    # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''                    # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5                    # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False              # If your broker supports TLS, set it True

mqtt_client = Mqtt(app)

msgRxd = False

@app.route("/help")
def gethelp():

    #This should be in a json file -> File path must be an environment variable
    routeListFilePath = os.getenv('ROUTE_LIST_FILE_PATH')

    #Check if file exists first
    if not exists(routeListFilePath):
        response = {"routeList": "","result": "Error route list not found!"}
        return json.dumps(response)

    try:
        #Open file and create dictionary containing route lists from json file
        routeListFile = open(routeListFilePath)
    except:
        #Failed to open route list file
        response = {"routeList": "","result": "Error route list file failed to open!"}
        return json.dumps(response)

    try:
        #create routelist dictionary
        routeListDictionary = json.load(routeListFile)
    except:
        #Failed to create route list dictionary
        response = {"routeList": "","result": "Failed to create route list dictionary!"}
        return json.dumps(response)
    

    return json.dumps(routeListDictionary)

@app.route("/getCommands")
def getCommandList():

    #Retrieve device profile from request
    deviceModel = request.json

    #Open device profile
    deviceProfileFilePath = os.getenv('DEVICE_PROFILES_FOLDER_PATH')+'/'+deviceModel["deviceModel"]+".json"

    #Check if file exists first
    if not exists(deviceProfileFilePath):
        response = {"commandList": "","result": "Device Profile File Not Found!"}
        return json.dumps(response)

    try:
        #Open file and create dictionary containing route lists from json file
        deviceProfileFile = open(deviceProfileFilePath)
    except:
        #Failed to open device profile file
        response = {"commandList": "","result": "Device profile file failed to open!"}
        return json.dumps(response)

    try:
        #create device profile dictionary
        deviceProfileDictionary = json.load(deviceProfileFile)
        response = deviceProfileDictionary["cmdList"]
    except:
        #Failed to create route list dictionary
        response = {"commandList": "","result": "Failed to create device profile list dictionary!"}
        return json.dumps(deviceProfileDictionary["cmdList"])
    
    
    return json.dumps(response)

@app.route("/getDeviceModelList")
def getDeviceProfileList():

    #Retrieve all device types current installed on bus -> File names must be "DeviceModel.json" and present in device profiles folder
    deviceProfileList = os.listdir(os.getenv('DEVICE_PROFILES_FOLDER_PATH'))

    #Empty Device Profile dictionary
    response ={"deviceProfiles":[]}
    
    #Next we open each profile and return the device descriptions along with the manufacturer model of each device
    for device in deviceProfileList:
        
        try:
            #Open json file->path as environment variable
            deviceProfileFile = open(os.getenv('DEVICE_PROFILES_FOLDER_PATH')+'/'+device)

            #Convert to dictionary
            deviceProfileDict = json.load(deviceProfileFile)

            #Add device device model and device description to response
            response["deviceProfiles"].append({"Model":deviceProfileDict["deviceModel"],"desc":deviceProfileDict["devDescription"]})

            #Close file
            deviceProfileFile.close()
        except:
            print("Failed to open device profile!")

    return json.dumps(response)


@app.route("/sendCmd",methods=['POST'])
def sendCmd():

    #Retrieve command details
    json_command_parameters = request.json

    #Empty json object -> will be populated and forwarded to mqtt_modbus_bridge
    mqtt_command = {
                        "cmdName":"", 
                        "uuid":"",
                        "devId":"",
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

    publish_result = mqtt_client.publish(os.getenv('MODBUS_CMD_TOPIC'), json.dumps(mqtt_command))

    global msgRxd

    if(msgRxd == True):
        msgRxd = False
        return "None"


    #return json.dumps(mqtt_command)
    

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(os.getenv('MODBUS_RESP_TOPIC')) # subscribe topic
   else:
       print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
   data = dict(topic=message.topic,payload=message.payload.decode())
   print('Received message on topic: {topic} with payload: {payload}'.format(**data))
   global msgRxd
   msgRxd = True

if __name__ == "__main__":
    app.run(os.getenv('FLASK_HTTP_SERVER'), int(os.getenv('FLASK_HTTP_PORT', 4000)), debug=False)




