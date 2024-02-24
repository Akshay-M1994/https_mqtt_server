import os
import json
from   os.path     import exists

def isDeviceProfilePresent(devProfile:str)->dict|None:

    deviceProfileJsonPath  = 'device_profiles/'+ devProfile +'.json'

    #Now we determine if such a profile exists on the database
    if not exists(deviceProfileJsonPath):
        return None
    
    try:
        #Open device profile json object
        deviceProfileJsonFile = open(deviceProfileJsonPath)

        #Create device profile dictionary
        deviceProfileDictionary = json.load(deviceProfileJsonFile)

        #Close the file
        deviceProfileJsonFile.close()

        return deviceProfileDictionary

    except:
        return None