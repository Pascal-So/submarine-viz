import bge
import math

c = bge.logic.getCurrentController()
ob = c.owner


phase_length = 30


def set_object_z_rotation(rOb, degs):
    """ rotation 0 means pointing in positive y direction
    rotation is counter-clockwise.
    """
    xyz = rOb.localOrientation.to_euler()
    xyz[2] = math.radians(degs)
    rOb.localOrientation = xyz.to_matrix() 


def find_index(vessel_array, needle):
    """ Find the index of the vessel by the (x,y) value.
    
    Structure of `vessel_array` is assumed to be (game_object, 
    (x,y), last_rotation).
    """
    for i, (v, pos, r) in enumerate(vessel_array):
        if pos is needle:
            return i # object found
    return -1 # object not found


def get_relevant_lines():
    """ find the lines from the log that belong to the current turn
    
    sets the property ob["relevant_lines"] to the sub array of
    ob["log_lines"], and sets the property ob["end_pointer"], which is
    the index of the first line belonging to the next turn.
    """
    # find value for `end_pointer`
    target_line = "STARTROUNDSHIP" if ob["ship_turn"] == True else "STARTROUNDSUBMARINE"
    ob["end_pointer"] = ob["pointer"]
    curr_line = ob["log_lines"][ob["end_pointer"]].split()[0]
    while curr_line != target_line and curr_line != "GAMEEND":
        ob["end_pointer"] += 1
        curr_line = ob["log_lines"][ob["end_pointer"]].split()[0]
        
    # extract lines
    ob["relevant_lines"] = ob["log_lines"][ob["pointer"]:ob["end_pointer"]]
    

def extract_actions():
    """ gets actions from ob["relevant_lines"]
    
    ob["movements"]
    ob["shots"]
    ob["deaths"]
    """
    
    movements = []
    shots = []
    deaths = []
    for line in ob["relevant_lines"]:
        fields = line.split()
        if fields[0] == "MOVE":
            # sets ob["movements"] to tuples from start pos to end pos.
            start = (int(fields[1]), int(fields[2]))
            end   = (int(fields[3]), int(fields[4]))
            mv = (start, end)
            movements.append(mv)
            
        elif fields[0] == "HIT" or fields[0] == "MISS":
            # set ob["shots"] to tuples from shot start pos to end pos.
            start = (int(fields[1]), int(fields[2]))
            end   = (int(fields[3]), int(fields[4]))
            shot = (start, end)
            shots.append(shot)
            if fields[0] == "HIT":
                # set ob["deaths"] to ship pos tuple
                deaths.append(end)
    
    ob["movements"] = movements
    ob["shots"] = shots
    ob["deaths"] = deaths

def compute_angles(startend):
    """ takes a tuple of start pos and end pos, returns the angle in degrees
    """
    (sx,sy),(ex,ey) = startend # extract info
    dx = ex-sx
    dy = ey-sy
    rad = tan2(dy, dx)
    


def tick():
    time_in_phase = ob["frame_nr"] % phase_length
    
    #print(time_in_phase, ob["turning_phase"])
    
    if time_in_phase == 0 and ob["turning_phase"]:
        # first frame in the new player's turn
        
        # these functions set global variables instead
        # of returning the results because we need to
        # keep the information accross multiple calls of
        # the scripts which makes this a bit more 
        # difficult.
        get_relevant_lines()
        extract_actions()
    
    #list(map(lambda x: set_object_z_rotation(x[0], ob["frame_nr"]), ob["ships"]))
    
    
    if time_in_phase == phase_length-1:
        if ob["turning_phase"] == False:
            # reached end of player's turn, prepare for next turn
            ob["ship_turn"] = not ob["ship_turn"]
            ob["turning_phase"] = True
            ob["pointer"] = ob["end_pointer"]
        else:
            ob["turning_phase"] = False
    

if "game_running" in ob and ob["game_running"]:
    # we don't need no .. optimization... dum dudum dum dum ..
    tick()
    ob["frame_nr"]+=1
    
    if ob["log_lines"][ob["pointer"]].split()[0] == "GAMEEND": 
        ob["game_running"] = False
    
    
    
    
    
# example code for setting z rotation of an object
# xyz = gameobject.localOrientation.to_euler()
# xyz[2] = math.radians(45)
# own.localOrientation = xyz.to_matrix() 
