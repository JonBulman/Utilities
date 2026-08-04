import json
import os
import sys
import pytz
from datetime import datetime, UTC

from typing import List, Any#, Union, Dict

# from google.auth.transport.requests import Request
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from dotenv import load_dotenv

class Jon_Bulman_Base:
    def to_dict(self):
        """Converts any child class instance into a JSON-serializable dict."""
        data = self.__dict__.copy()
        
        # Add the class name so we know how to "cast" it back later
        data["__type__"] = self.__class__.__name__
        
        # Handle datetime objects (JSON can't save them natively)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    def to_json(self):
        """Returns a JSON string of the object."""
        return json.dumps(self.to_dict(), indent=3)
    
def setup_environment():
    sysState = getattr(sys, 'frozen', False)
    if sysState is False :
    #    # Running as compiled .exe
    #    return os.path.join(os.path.dirname(sys.executable), configFile)
    #else :
        print(sys.executable)
        if "automation" not in sys.executable:
            raise RuntimeError("Wrong Python environment")
        
    # This reads my environment variables from /Users/Jon/.config/automation/.env MAKE CHANGES THERE!
    #load_dotenv("/Users/Jon/.config/automation/.env")
    load_dotenv()

def load_json(filepath: str, class_map: Any) -> List[Any]:
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []

    # 1. If it's already a list, process each item
    if isinstance(data, list):
        processed_objects = []
        for item in data:
            class_str = item.pop("__type__", None)
            # Handle if class_map is a dict or a single class
            actual_class = class_map.get(class_str) if isinstance(class_map, dict) else class_map
            
            if actual_class:
                processed_objects.append(actual_class(**item))
            else:
                processed_objects.append(item)
        return processed_objects
    
    # 2. If it's a single dict, wrap the result in a list []
    else:
        class_str = data.pop("__type__", None)
        actual_class = class_map.get(class_str) if isinstance(class_map, dict) else class_map
        
        if actual_class:
            return [actual_class(**data)] # Wrapped in list
        return [data] # Wrapped in list

def Getenv(var):
    val = os.getenv(var)
    # if val is None:
    #    raise ValueError(f"{var} must be set")
    return val

def ConvertUTCtoLocal(date,time):
# convert UTC times to local

    utc_format = "%Y-%m-%d %H:%M:%S"
    local_tz = pytz.timezone('Europe/London')

    utc_string=f"{date} {time}:00"
    utc_dt = datetime.strptime(utc_string, utc_format).replace(tzinfo=UTC)

    local_time = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

    return local_time

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

def Email_Me(credentials, token_file, to, subject, body):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print("No credentials or valid token")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing auth token")
            request = google.auth.transport.requests.Request()
            try:
                creds.refresh(request)
            except Exception as e:
                print(f"How exceptional! {e}")
                print(f"A refresh error occurred - new token needed - delete {token_file}")
                return
        else:
            print("Creating credentials token", credentials)
            flow = InstalledAppFlow.from_client_secrets_file( credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            print("Writing token",token_file)
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(body, 'html')
        message['to'] = to
        message['subject'] = subject
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        #results = 
        (service.users().messages().send(userId="me", body=create_message).execute())
        print("Message sent to ", to , " Subject:", subject)
        #print(f"Message sent to {results} Message Id: {results['id']}")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

# The config file is a key file to load settings
def Load_Config(configfile):
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe
        configPath = os.path.join(os.path.dirname(sys.executable), configfile)
    else:
        # Running as .py script
            cwd = os.getcwd()
            #cwf =os.path.dirname(os.path.abspath(__file__)) # where the exe is running
            #print(cwd)
            #print(cwf)
            configPath = os.path.join(cwd, configfile)

    config=None
    ok=os.path.isfile(configPath)
    if ok :
        with open(configPath, "r") as f:
            config = json.load(f)
        print("Config loaded ",configPath)
    else :
         print("Failed to find config ",configPath)

    return config

def Get_Variable(name,config,verbose=0):
    # can be set in
    # 1. Command line parameter
    # 2. Environment variable
    # 3. config.json file
    # My order of priority is... 1,2,3

    val = Getenv(name)
    if val is not None and verbose > 0:
        print(f"Get_Variable: {name} from ENV VAR: {val}")
    if val is not None:
        return val
    elif config is not None:
        val = config.get(name)
        if val is not None and verbose > 0:
            print(f"Get_Variable: {name} from CONFIG FILE: {val}")
        return val
    if verbose > 0:
        print(f"Get_Variable: {name} NOT FOUND")
    return None
    
def Extract_values(obj, key):
	"""Pull all values of specified key from nested JSON."""
	arr = []
	def extract(obj, arr, key):        
		"""Recursively search for values of key in JSON tree."""
		if isinstance(obj, dict):
			v1 = 0 
			for k, v in obj.items():
				if isinstance(v, (dict, list)):
					extract(v, arr, key)
				elif k == key:
					v1 = v	
			arr.append(v1)
		elif isinstance(obj, list):
			for item in obj:
				extract(item, arr, key)
		return arr

	results = extract(obj, arr, key)
	return results

def bold(colour, value):
    return f'<b style="color:{colour};">{value}</b>'