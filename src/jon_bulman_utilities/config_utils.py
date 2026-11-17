import json
import os
import sys


from dotenv import load_dotenv
    
def setup_environment():
    load_dotenv()

def Getenv(var):
    val = os.getenv(var)
    # if val is None:
    #    raise ValueError(f"{var} must be set")
    return val

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
