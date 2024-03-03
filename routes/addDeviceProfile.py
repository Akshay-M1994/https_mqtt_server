from   flask    import Blueprint,request
from   os.path  import exists
import json
import os

# Defining a blueprint
addDeviceProfile_bp = Blueprint('addDeviceProfile_bp', __name__, template_folder='templates',static_folder='static')

@addDeviceProfile_bp.route("/addDeviceProfile")
def addDeviceProfile():

    #Retrieve device profile from request
    newDeviceProfile = request.json

    #Validate profile contents->Add length validation
    if not "deviceModel" in newDeviceProfile:
        return "deviceModel key absent"
    
    if not "devDescription" in newDeviceProfile:
        return "devDescription key absent"
    
    if not "deviceWebsite" in newDeviceProfile:
        return "deviceWebsite key absent"
    
    if not "cmdList" in newDeviceProfile:
        return "cmdList key absent"

    for cmdIndex,cmd in enumerate(newDeviceProfile["cmdList"]):
        if not "cmdName" in cmd:
            return "cmdName key absent in command["+str(cmdIndex)+"]"
        
        if not "modfunc" in cmd:
            return "modfunc key absent in command["+str(cmdIndex)+"]"

        if not "regAdd" in cmd:
            return "regAdd key absent in command["+str(cmdIndex)+"]"
        
        if not "regCount" in cmd:
            return "regCount key absent in command["+str(cmdIndex)+"]"
        
        if not "regData" in cmd:
            return "regData key absent in command["+str(cmdIndex)+"]"
        
        if not "cmdType" in cmd:
            return "cmdType key absent in command["+str(cmdIndex)+"]"
        
        #Determine if file already exists
        deviceProfileList = os.listdir(os.getenv('DEVICE_PROFILES_FOLDER_PATH'))

        #Determine if specified filename is in the list
        for deviceProfile in deviceProfileList:
            if deviceProfile.find(newDeviceProfile["deviceModel"]) != -1:
                return "Device Profile Already Exists!"
            
        newDeviceProfileJsonFile = open(os.getenv('DEVICE_PROFILES_FOLDER_PATH')+'/'+newDeviceProfile["deviceModel"]+".json", "w")  
        json.dump(newDeviceProfile,newDeviceProfileJsonFile,indent=6)
        newDeviceProfileJsonFile.close()

    return "Device Profile was added successfully!"