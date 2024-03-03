import os
import json
from   os.path     import exists

def isDeviceInstalled(devId:str)->dict|None:

    #Check if file exists first->find better way to handle this
    if not exists("installed_devices/installed_devices.json"):
        return None

    try:
    #Check if device is installed
        installedDevicesFile = open(os.getenv('INSTALLED_DEVICES_FILE_PATH'))
    except:
        return None
    
    try:
        #Convert json file to python dictionary
        installedDevicesDict = json.load(installedDevicesFile)
        installedDevicesFile.close()
    except:
        return None
    
    for device in installedDevicesDict["installedDevices"]:
        if device["devId"] == devId:
            return device
        
    return None

def isDeviceAddressAvailable(devAdd:int):
    
    #Check if file exists first->find better way to handle this
    if not exists("installed_devices/installed_devices.json"):
        return None

    try:
    #Check if device is installed
        installedDevicesFile = open(os.getenv('INSTALLED_DEVICES_FILE_PATH'))
    except:
        return None
    
    try:
        #Convert json file to python dictionary
        installedDevicesDict = json.load(installedDevicesFile)
        installedDevicesFile.close()
    except:
        return None
    
    for device in installedDevicesDict["installedDevices"]:
        if device["devAdd"] == devAdd:
            return device
        
    return None
