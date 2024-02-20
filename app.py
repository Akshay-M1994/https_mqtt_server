from flask import Flask
import json

#Flask http host server
FLASK_HTTP_SERVER = "0.0.0.0"
FLASK_HTTP_PORT   = 4000

app = Flask(__name__)

@app.route("/help")
def help():
    data = {"routeList":
                [
                    {
                     "routeName":"help",
                     "requestURL":"http://serverAddress:serverPort/help",
                     "description":"Returns a list of routes that can be used to access different endpoints"
                    },
                    {
                     "routeName":"getAPIs",
                     "requestURL":"http://serverAddress:serverPort/getCommands",
                     "Request Body(Json)":{"deviceType":"DeviceType"},
                     "description":"Returns a list of commands that can be sent to a particular modbus device"
                    },
                    {
                     "routeName":"profileList",
                     "requestURL":"http://serverAddress:serverPort/profileList",
                     "description":"Returns a list of profiles of different modbus devices current present on the modbus"
                    },
                    {
                     "routeName":"sendcmd",
                     "requestURL":"http://serverAddress:serverPort/sendcmd",
                     "description":"Returns a list of profiles of different modbus devices current present on the modbus"
                    }
                ]
        }
    return json.dumps(data)
    
if __name__ == "__main__":
    app.run(FLASK_HTTP_SERVER, FLASK_HTTP_PORT, debug=True)