from   flask_mqtt  import Mqtt
from   os.path     import exists
from   flask       import Flask, request
from   dotenv      import load_dotenv
from   enum        import Enum
from   mqtt2modbus import mqtt2Modbus_ErrorStatus
from   routes      import help,getCommands,getDeviceModelList
import os,binascii
import secrets
import json

#Load environment variable file
load_dotenv()

#Create flask instance
app = Flask(__name__)

#Register blueprints or "routes"
app.register_blueprint(help.help_bp)
app.register_blueprint(getCommands.getCommands_bp)
app.register_blueprint(getDeviceModelList.getDeviceModelList_bp)

app.config['MQTT_BROKER_URL'] = '192.168.1.100'     # IP Address of MQTT broker
app.config['MQTT_BROKER_PORT'] = 1884               # Set Port used for MQTT comms.
app.config['MQTT_USERNAME'] = ''                    # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''                    # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5                    # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False              # If your broker supports TLS, set it True

#Create flask mqtt client instance
mqtt_client = Mqtt(app)

msgRxd = False

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
            mqtt_command["deviceModel"] = device["deviceModel"]
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
