from   flask    import Blueprint
from   os.path  import exists
import json
import os

# Defining a blueprint
getCommands_bp = Blueprint('getCommands_bp', __name__, template_folder='templates',static_folder='static')

@getCommands_bp.route("/getCommands")
def gethelp():

    #This should be in a json file -> File path must be an environment variable
    routeListFilePath = os.getenv('ROUTE_LIST_FILE_PATH')

    #Check if file exists first
    if not exists(routeListFilePath):
        response = {"routeList": "","result": "Error route list not found!"}
        return json.dumps(response)

    try:
        #Open file and create dictionary containing route lists from json file
        routeListFile = open(routeListFilePath)
    except:
        #Failed to open route list file
        response = {"routeList": "","result": "Error route list file failed to open!"}
        return json.dumps(response)

    try:
        #create routelist dictionary
        routeListDictionary = json.load(routeListFile)
    except:
        #Failed to create route list dictionary
        response = {"routeList": "","result": "Failed to create route list dictionary!"}
        return json.dumps(response)
    

    return json.dumps(routeListDictionary)