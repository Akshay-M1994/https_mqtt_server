from   flask_mqtt  import Mqtt
from   os.path     import exists
from   flask       import Flask, request
from   dotenv      import load_dotenv
from   enum        import Enum
from   mqtt2modbus import mqtt2Modbus_ErrorStatus
from   routes      import help,getCommands,getDeviceModelList,sendCommand
from   debug_nid   import debug
import os,binascii
import secrets
import json
import sys
import threading


def initialize():
    try:
        #Global Msg Control Sempahore
        global mqttMsgRxdSemaphore
        mqttMsgRxdSemaphore = threading.Lock()

        #Ensure that semaphore starts in non-released state
        mqttMsgRxdSemaphore.acquire()

        global mqttJsonMsg
        mqttJsonMsg = dict()

        global mqtt_client
        mqtt_client = Mqtt(app)

    except Exception as e:
        debug.logging.debug("Initialization Failed [%s]!",str(e))


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
    debug.logging.debug("Mqtt Client Disconnected!")

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       debug.logging.debug("Mqtt Client Connected!")
       mqtt_client.subscribe(os.getenv('MODBUS_RESP_TOPIC')) 
   else:
       debug.logging.debug("Bad Connection Code [%d]",rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
   
   #For debug
   data = dict(topic=message.topic,payload=message.payload.decode())
   debug.logging.debug('Received message on topic: {topic} with payload: {payload}'.format(**data))
   
   #Copy received message payload to global variable
   global mqttJsonMsg
   mqttJsonMsg = json.loads(message.payload)

   #Release the semaphore as we have received a message
   mqttMsgRxdSemaphore.release()






