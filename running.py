import bge
import math

c = bge.logic.getCurrentController()
ob = c.owner


phase_length = 30


def set_object_z_rotation(rOb, degs):
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
    curr_line = ob["log_lines"][ob["end_pointer"]]
    while curr_line != target_line and curr_line != "GAMEEND":
        ob["end_pointer"] += 1
        curr_line = ob["log_lines"][ob["end_pointer"]]
        
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
            
        elif fields[0] == "HIT" or fields[0] == "MISS"
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


def tick():
    time_in_phase = ob["frame_nr"] % phase_length
    
    if time_in_phase == 0 and ob["turning_phase"]:
        # first frame in the new phase
        # these functions set global variables instead
        # of returning the results because we need to
        # keep the information accross multiple calls of
        # the scripts which makes this a bit more 
        # difficult.
        get_relevant_lines()
        extract_actions()
    
    
    
    
    if time_in_phase == phase_length-1:
        if ob["moving_phase"]:
            # reached end of turn, prepare for next turn
            ob["ship_turn"] = ! ob["ship_turn"]
            ob["moving_phase"] = False
            ob["pointer"] = ob["end_pointer"]
        else:
            ob["moving_phase"] = True
    

if "frame_nr" in ob and ob["frame_nr"] >= 0:
    # we don't need no .. optimization... dum dudum dum dum ..
    tick()
    ob["frame_nr"]+=1
    
    
    
# example code for setting z rotation of an object
# xyz = gameobject.localOrientation.to_euler()
# xyz[2] = math.radians(45)
# own.localOrientation = xyz.to_matrix() 
