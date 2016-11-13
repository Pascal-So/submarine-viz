import bge
import png
import itertools

#controller = bge.logic.getCurrentController()
#add_land = controller.actuators["add_land"]
#add_end = controller.actuators["add_end"]
#add_start = controller.actuators["add_start"]


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def create_map(width, height, pixels):
    "place the land, start and end blocks, resize water"

    scene = bge.logic.getCurrentScene()
    
    def place_object(object, position):
        object = scene.addObject(object, "gameLogic")
        object.worldPosition(position)
    
    
    

    


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
    
    #print(list(pixels))
    
load_map("submarine/rt/maps/map20.png")