import bge
import os
import loadMap



path_to_logfile = "logs/game1.txt"



cont = bge.logic.getCurrentController()
actuator_quit = cont.actuators["quit"]

def exit():
    cont.activate(actuator_quit)

if not os.path.isfile(path_to_logfile):
    exit()
    
log_lines = []

with open(path_to_logfile, "r") as f:
    log_lines = f.readlines()

if len(log_lines) == 0:
    exit()


def place_vessel(type, x, y):
    """ returns the vessel object once it's been instanciated 
    
    The objects have to be named "ship" and "submarine"
    """
    vessel = scene.addObject(type, "gameLogic")
    vessel.worldPosition = (x, y, 0)
    return vessel


map_name="submarine/rt/maps/map10.png"

loadMap.load_map(map_name)

