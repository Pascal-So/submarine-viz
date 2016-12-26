import bge
import math

c = bge.logic.getCurrentController()
ob = c.owner
scene = bge.logic.getCurrentScene()


turn_phase_length = 4
move_phase_length = 8


# ^^^^^^^^^^^^ adjust speed settings here ^^^^^^^^^^^^^^^^^


total_phase_length = turn_phase_length + move_phase_length

def set_object_rotation(rOb, degs, axis):
    xyz = rOb.localOrientation.to_euler()
    xyz[axis] = math.radians(degs)
    rOb.localOrientation = xyz.to_matrix() 

def set_object_z_rotation(rOb, degs):
    """ rotation 0 means pointing in positive y direction
    rotation is counter-clockwise.
    """
    set_object_rotation(rOb, degs, 2) 
    
def set_object_y_rotation(rOb, degs):
    """ rotation 0 is upright
    """
    set_object_rotation(rOb, degs, 1) 


def find_index(vessel_array, needle):
    """ Find the index of the vessel by the (x,y) value.
    
    Structure of `vessel_array` is assumed to be (game_object, 
    (x,y), last_rotation).
    """
    for i, (v, pos, r) in enumerate(vessel_array):
        if pos == needle:
            return i # object found
    return -1 # object not found


def get_relevant_lines():
    """ find the lines from the log that belong to the current turn
    
    sets the property ob["relevant_lines"] to the sub array of
    ob["log_lines"], and sets the property ob["end_pointer"], which is
    the index of the first line belonging to the next turn.
    """
    # find value for `end_pointer`
    target_line = "STARTROUNDSUBMARINE" if ob["ship_turn"] == True else "STARTROUNDSHIP"
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

def wrap(start, end, val):
    diff = end - start
    while val >= end:
        val -= diff
    while val < start:
        val += diff
    return val

def compute_angles(startend):
    """ takes a tuple of start pos and end pos, returns the angle in degrees
    """
    (sx,sy),(ex,ey) = startend # extract info
    dx = ex-sx
    dy = ey-sy
    tmp = math.degrees(math.atan2(dy, dx))
    deg = wrap(0,360, - tmp - 90)
    
    return deg


def lerp(val1, val2, frac):
    """ linear interpolation """
    return val1 * (1-frac) + val2 * frac

def lerp_angle(val1, val2, frac):
    """ like lerp, but wrap over 360 if it
    is shorter
    """
    if abs(val2 - val1) <= 180:
        return lerp(val1, val2, frac)
    else:
        if val1 < val2:
            val1 += 360
        else:
            val2 += 360
        return wrap(0,360, lerp(val1, val2, frac))


def lerp_pos(p1, p2, frac):
    """ like lerp but for (x,y) tuples """
    x1,y1 = p1
    x2,y2 = p2
    
    xc = lerp(x1, x2, frac)
    yc = lerp(y1, y2, frac)
    
    return (xc, yc)

def move_object_to(obj, x, y):
    obj.worldPosition = (x, ob["map_height"] -1 -y, 0.0)


def spawn_bullet(pos, rot):
    """ returns the bullet object once it's been added to the scene
    """
    blt = scene.addObject("bullet", "gameLogic")
    blt.worldPosition = (*pos, 0.0)
    set_object_z_rotation(blt, rot)
    return blt


def setup():
    # these functions set global variables instead
    # of returning the results because we need to
    # keep the information accross multiple calls of
    # the scripts which makes this a bit more 
    # difficult.
    get_relevant_lines()
    extract_actions()
    #print(ob["movements"], "move")
    ob["target_directions"] = list(map(lambda x : (x[0], compute_angles(x)), ob["movements"]))
    # to the submarines it doesn't matter whether they're aligning to shoot or to move.
    ob["target_directions"].extend(list(map(lambda x : (x[0], compute_angles(x)), ob["shots"])))


def tick():
    time_in_phase = ob["frame_nr"] % total_phase_length
    
    if time_in_phase == 0:
        # first frame in the new player's turn
        setup()
        
    
    vessels = ob["ships"] if ob["ship_turn"] else ob["submarines"]
    
    # turn all the things!!
    if ob["turning_phase"]:
        fraction_in_turn_phase = time_in_phase / (turn_phase_length - 1)
        # need the -1 because we want to go from 0 all the way to 1, not just 0.9...
        
        for pos, dir in ob["target_directions"]:
            turn_obj_index = find_index(vessels, pos)
            turn_obj, _, last_dir = vessels[turn_obj_index]
            
            current_dir = lerp_angle(last_dir, dir, fraction_in_turn_phase)
            
            set_object_z_rotation(turn_obj, current_dir)
            
            if time_in_phase == turn_phase_length -1:
                # update last_dir in the vessels array
                vessels[turn_obj_index] = (turn_obj, pos, dir)
    
    
    # move all the things!!
    if not ob["turning_phase"]:
        fraction_in_move_phase = (time_in_phase - turn_phase_length) / (move_phase_length - 1)
        
        for pos, dest in ob["movements"]:
            move_obj_index = find_index(vessels, pos)
            move_obj, start, last_dir = vessels[move_obj_index]
            
            current_pos = lerp_pos(start, dest, fraction_in_move_phase)
            move_object_to(move_obj, *current_pos)
            
            if time_in_phase == total_phase_length -1:
                # update last pos in vessels array
                vessels[move_obj_index] = (move_obj, dest, last_dir)
        
    
    # shoot some things!!
    # turning to align for the shots will take exactly the same time as
    # turning to move, shooting will be twice as fast as moving. I know, this
    # is unrealistic, because the shot speed will depend on the distance, but since
    # the distances won't vary by a lot (only within shoot radius), this shouldn't
    # matter too much.
    # bullets are stored in `ob["bullets"]`, format is `(bullet_object, (start, end))`
    shoot_phase_length = move_phase_length // 2
    time_in_shooting_phase = time_in_phase - turn_phase_length
    is_shooting_phase = time_in_shooting_phase < shoot_phase_length and time_in_shooting_phase >= 0
    if is_shooting_phase:
        if time_in_shooting_phase == 0:
            # spawn bullets
            bullets = []
            for start, end in ob["shots"]:
                dir = compute_angles((start, end))
                blt = spawn_bullet(start, dir)
                bullets.append((blt, (start,end)))
            ob["bullets"] = bullets
        
        fraction_in_shooting_phase = time_in_shooting_phase  / (shoot_phase_length - 1)
        
        for blt, path in ob["bullets"]:
            current_pos = lerp_pos(*path, fraction_in_shooting_phase)
            move_object_to(blt, *current_pos)
        
        if time_in_shooting_phase == shoot_phase_length - 1:
            # despawn bullets
            for blt, _ in ob["bullets"]:
                blt.endObject()
    
    
    # kill some things!!
    # dying ships turn around their local y axis
    dying_phase_length = move_phase_length - shoot_phase_length
    time_in_dying_phase = time_in_phase - turn_phase_length - shoot_phase_length
    is_dying_phase = time_in_dying_phase >= 0
    if is_dying_phase:
        
        fraction_in_dying_phase = time_in_dying_phase / (dying_phase_length - 1)
        
        for pos in ob["deaths"]:
            dying_ship_index = find_index(ob["ships"], pos)
            dying_ship, _, _ = ob["ships"][dying_ship_index]
            
            current_y_rotation = lerp(0, 180, fraction_in_dying_phase)
            
            set_object_y_rotation(dying_ship, current_y_rotation)
    
    
    if time_in_phase == turn_phase_length-1:
        # reached end of turn phase, switch to move phase
        ob["turning_phase"] = False
        
    if time_in_phase == total_phase_length-1:
        # reached end of player's turn, prepare for next turn
        ob["ship_turn"] = not ob["ship_turn"]
        ob["turning_phase"] = True
        ob["pointer"] = ob["end_pointer"]

            
    

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
