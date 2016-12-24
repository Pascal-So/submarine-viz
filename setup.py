import bge
import os
import loadMap
import utility

# parsing of the log file happens in here.
# start blender from the console in the git project roots in order for this to work

# if the game can't be started, check if the path_to_logfile is correct and if the
# logfile is valid. The blender game will quit on incorrect input.

path_to_logfile = "logs/game1.txt"


cont = bge.logic.getCurrentController()
actuator_quit = cont.actuators["quit"]
ob = cont.owner
scene = bge.logic.getCurrentScene()


def exit():
    cont.activate(actuator_quit)

if not os.path.isfile(path_to_logfile):
    exit()
    
log_lines = []

with open(path_to_logfile, "r") as f:
    log_lines = f.readlines()

if len(log_lines) == 0:
    exit()
    
    
def read_header_line(line):
    """ Sets some global variables with the game information
    side-effects: writes variables in owner dict
    returns false if line does not start with "GAMEINFO"
    """
    fields = line.split()
    keyword = fields[0]
    if keyword == "GAMEINFO":
        ob["map"] = fields[1]
        ob["ship_count"] = int(fields[2])
        ob["submarine_count"] = int(fields[3])
        ob["radius_move"] = int(fields[4])
        ob["radius_view"] = int(fields[5])
        ob["radius_attack"] = int(fields[6])
        return True
    else:
        return False
    
    
if not read_header_line(log_lines[2]):
    print ("incorrect log file format, expected gameinfo on line 3")
    exit()
    

def place_vessel(type, x, y):
    """ returns the vessel object once it's been instanciated 
    
    The objects have to be named "ship" and "submarine"
    """
    vessel = scene.addObject(type, "gameLogic")
    vessel.worldPosition = (x, y, 0.0)
    return vessel





# main stuff. ------------------------------------------------------

if not read_header_line(log_lines[2]):
    exit()
    # invalid log file, gameinfo should be on line 3

loadMap.load_map(ob["map"])

ob["pointer"] = 3 # current (0-indexed) live in the logfile

ship_lines = log_lines[ob["pointer"]:ob["pointer"]+ob["ship_count"]]
ob["pointer"] += ob["ship_count"]
submarine_lines = log_lines[ob["pointer"]:ob["pointer"] + ob["submarine_count"]]
ob["pointer"] += ob["submarine_count"]


# grumble grumble..
# Blender gameengine can't handle storing game object
# references in dicts, therefore I have to use arrays
# and search for the correct object which is gonna make
# it a bit slower but hey, we're not gonna have like
# thousands of entities at a time, right? right??

# `ships` and `submarines` are arrays of tuples
# (game object, (x,y), last rotation)

ships = []

for line in ship_lines:
    fields = line.split()
    x = int(fields[1])
    y = int(fields[2])
    ship = place_vessel("ship", x, ob["map_height"]-1-y)
    tpl = (ship, (x,y), 0.0)
    ships.append(tpl)


submarines = []

for line in submarine_lines:
    fields = line.split()
    x = int(fields[1])
    y = int(fields[2])
    submarine = place_vessel("submarine", x, ob["map_height"]-1-y)
    tpl = (submarine, (x,y), 0.0)
    submarines.append(tpl)


# submarines and ships have been added to their start
# positions, start main loop now. 

# pass the relevant information to the object so it can
# be used by "running.py"
ob["log_lines"] = log_lines
ob["ships"] = ships
ob["submarines"] = submarines



# phases: turing ships, moving ships, turning subs, moving
# subs, etc..
ob["moving_phase"] = False

# this line effectively starts the "running.py" script
ob["frame_nr"] = 0