from   flask_mqtt  import Mqtt
from   os.path     import exists
from   flask       import Flask, request
from   dotenv      import load_dotenv
from   enum        import Enum
from   mqtt2modbus import mqtt2Modbus_ErrorStatus
from   routes      import help,getCommands,getDeviceModelList,sendCommand
import os,binascii
import secrets
import json
import sys

def initialize():
    try:
        #Used to flag when a message is received over mqtt
        global msgRxd
        msgRxd = False

        global mqttJsonMsg
        mqttJsonMsg = dict()

        global mqtt_client
        mqtt_client = Mqtt(app)
    except:
        print("Error!")

#Load environment variable file
load_dotenv()

#Create flask instance
app = Flask(__name__)

#Register blueprints or "routes"
app.register_blueprint(help.help_bp)
app.register_blueprint(getCommands.getCommands_bp)
app.register_blueprint(getDeviceModelList.getDeviceModelList_bp)
app.register_blueprint(sendCommand.sendCommand_bp)


app.config['MQTT_BROKER_URL'] = '192.168.1.100'     # IP Address of MQTT broker
app.config['MQTT_BROKER_PORT'] = 1884               # Set Port used for MQTT comms.
app.config['MQTT_USERNAME'] = ''                    # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''                    # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5                    # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False              # If your broker supports TLS, set it True

initialize()

if __name__ == "__main__":
    app.run(os.getenv('FLASK_HTTP_SERVER'), int(os.getenv('FLASK_HTTP_PORT', 4000)), debug=False)


@mqtt_client.on_disconnect()
def handle_disconnect():
    print("Disconnected!")

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(os.getenv('MODBUS_RESP_TOPIC')) 
   else:
       print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
   
   #For debug
   data = dict(topic=message.topic,payload=message.payload.decode())
   print('Received message on topic: {topic} with payload: {payload}'.format(**data))
   
   global mqttJsonMsg
   global msgRxd

   #Copy received message payload to global variable
   mqttJsonMsg = json.loads(message.payload)

   #Set message received flag to true
   msgRxd = True






