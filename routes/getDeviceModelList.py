from   flask    import Blueprint
from   os.path  import exists
from   debug_nid import debug
import json
import os

# Defining a blueprint
getDeviceModelList_bp = Blueprint('getDeviceModelList_bp', __name__, template_folder='templates',static_folder='static')

@getDeviceModelList_bp.route("/getDeviceModelList")
def getDeviceProfileList():

    #Retrieve all device types current installed on bus -> File names must be "DeviceModel.json" and present in device profiles folder
    deviceProfileList = os.listdir(os.getenv('DEVICE_PROFILES_FOLDER_PATH'))

    #Empty Device Profile dictionary
    response ={"deviceProfiles":[]}
    
    #Next we open each profile and return the device descriptions along with the manufacturer model of each device
    for device in deviceProfileList:
        
        try:
            if(device.__contains__(".json")):
                #Open json file->path as environment variable
                deviceProfileFile = open(os.getenv('DEVICE_PROFILES_FOLDER_PATH')+'/'+device)

                #Convert to dictionary
                deviceProfileDict = json.load(deviceProfileFile)

                #Add device device model and device description to response
                response["deviceProfiles"].append({"Model":deviceProfileDict["deviceModel"],"desc":deviceProfileDict["devDescription"]})

                #Close file
                deviceProfileFile.close()
        except:
            debug.logging.debug("Failed to open device profile!")

    return json.dumps(response)