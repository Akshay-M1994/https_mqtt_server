from   flask    import Blueprint,request
from   os.path  import exists
from   device_profiles.src     import device_profiles
from   installed_devices.src   import installed_devices
from   debug_nid               import debug
import json
import os

# Defining a blueprint
installDevice_bp = Blueprint('installDevice_bp', __name__, template_folder='templates',static_folder='static')

@installDevice_bp.route("/installDevice")
def installDevice():

    #Retrieve device profile from request
    newDeviceDetails = request.json

    #Validate profile contents->Add length validation
    if not "deviceModel" in newDeviceDetails:
        debug.logging.debug("Error:deviceModel key absent")
        return "Error:deviceModel key absent"
    
    if not "devDescription" in newDeviceDetails:
        debug.logging.debug("Error:devDescription key absent")
        return "Error:devDescription key absent"
    
    if not "devId" in newDeviceDetails:
        debug.logging.debug("Error:devId key absent")
        return "Error:devId key absent"
    
    if not "devAdd" in newDeviceDetails:
        debug.logging.debug("Error:devAdd key absent")
        return "Error:devAdd key absent"
    
    if(device_profiles.isDeviceProfilePresent(newDeviceDetails["deviceModel"]) == None):
        debug.logging.debug("Error:devAdd key absent")
        return "Error:Device profile does not exist!"
    
    if(installed_devices.isDeviceInstalled(newDeviceDetails["devId"]) != None):
        debug.logging.debug("Error:devAdd key absent")
        return "Error:Device with Id already exists.Please use a unique Id"
    
    if(installed_devices.isDeviceAddressAvailable(newDeviceDetails["devAdd"]) != None):
        debug.logging.debug("Error:devAdd key absent")
        return "Error:Device Address already occupied on modbus!"
    
     #Check if file exists first->find better way to handle this
    if not exists("installed_devices/installed_devices.json"):
        debug.logging.debug("Error:devAdd key absent")
        return None

    try:
    #Check if device is installed
        installedDevicesFile = open(os.getenv('INSTALLED_DEVICES_FILE_PATH'),"r")
    except:
        return None
    
    try:
        #Convert json file to python dictionary
        installedDevicesDict = json.load(installedDevicesFile)
        installedDevicesDict["installedDevices"].append(newDeviceDetails)
        installedDevicesFile = open(os.getenv('INSTALLED_DEVICES_FILE_PATH'),"w")
        json.dump(installedDevicesDict,installedDevicesFile,indent=6)
        installedDevicesFile.close()
    except Exception as e:
        debug.logging.debug(e)
        return None
    
    debug.logging.debug("Device Installed Successfully!")
    return "Device Installed Successfully!"
    

        
    