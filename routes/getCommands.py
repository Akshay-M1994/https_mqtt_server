from   flask    import Blueprint,request
from   os.path  import exists
import json
import os

# Defining a blueprint
getCommands_bp = Blueprint('getCommands_bp', __name__, template_folder='templates',static_folder='static')

@getCommands_bp.route("/getCommands")
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