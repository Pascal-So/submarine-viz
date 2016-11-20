import bge
import png
import itertools

terrain_types = {}
terrain_types[0] = "start"
terrain_types[1] = "end"
terrain_types[2] = "water"
terrain_types[3] = "land"

scene = bge.logic.getCurrentScene()

def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks
    
    Example: grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    returns list of tuples
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def place_camera( x, y ):
    cam = scene.active_camera
    z = cam.worldPosition[2]
    
    cam.worldPosition = (x, y, z)


def create_map(width, height, pixels):
    """place the land, start and end blocks, resize water
    
    The coordinates are mapped one to one, this means that
    one unit in the map data will correspond to one blender
    unit.
    Doesn't return anything, just has side effects.
    """
    


    
    def index_to_xy(i, width, height):
        """ Takes 0 based index going line wise from top
        left to bottom right, returns x, y coordinates so
        that 0,0 is on bottom left corner
        """
        x = i % width
        y = i // width
        y*= -1
        y+= height - 1
        return (x,y)
    
    def place_terrain(type, i):
        """This won't return anything, just do side effects
        
        The object "gameLogic" is used to place the object
        initially. It doesn't matter where this object is,
        as long as it exists. There must be an easier way,
        but this works.
        """
        x,y = index_to_xy(i, width, height)

        object_name = terrain_types.get(type, "water")

        if object_name != "water":
            object = scene.addObject(object_name, "gameLogic")
            object.worldPosition = (x,y,0) 
    
    
    list(map( (lambda tup : place_terrain(tup[1], tup[0])), list(enumerate(pixels)) ))


def load_map(map_name):
    "read the png file"
    reader = png.Reader(filename=map_name)
    image_width, image_height, pixels, metadata = reader.read_flat()
    
    nr_channels = 4 if metadata["alpha"] else 3
    
    terrains = {}
    terrains[(255,0,0)] = 0 # start
    terrains[(0,255,0)] = 1 # end
    terrains[(0,0,255)] = 2 # water
    terrains[(0,0,0)]   = 3 # land
    
    def colorToTerrain(color):
        color = color[0:3] # drop alpha value
        return terrains.get(color, -1) # returns -1 if incorrect color is found
    
    pixels = map(colorToTerrain, grouper(pixels, nr_channels, 0))
    
    create_map(image_width, image_height, pixels)
    
    place_camera(image_width/2, image_height/2)
    
    #print(list(pixels))
    
#load_map("submarine/rt/maps/map10.png")