import bge
import loadMap


def place_vessel(type, x, y):
    """ returns the vessel object once it's been instanciated 
    
    The objects have to be named "ship" and "submarine"
    """
    ship = scene.addObject(type, "gameLogic")
    ship.worldPosition = (x, y, 0)
    return ship




map_name="submarine/rt/maps/map10.png"

loadMap.load_map(map_name)

