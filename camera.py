import bge
controller = bge.logic.getCurrentController()
move = controller.actuators["move"]
cam = controller.owner

turn_phase_length = 4
move_phase_length = 8


# ^^^^^^^^^^^^ adjust speed settings here ^^^^^^^^^^^^^^^^^
total_phase_length = turn_phase_length + move_phase_length

# get sensor data
press_w = controller.sensors["w"]
press_a = controller.sensors["a"]
press_s = controller.sensors["s"]
press_d = controller.sensors["d"]
wheel_up = controller.sensors["wheel up"]
wheel_down = controller.sensors["wheel down"]
space = controller.sensors["space"]

cam_height = cam.position[2]

def sign(x):
    if (x > 0):
        return 1
    elif (x<0):
        return -1
    else:
        return 0


############### x, y motion ################

v_x = move.dLoc[0]
v_y = move.dLoc[1]

# acceleration factor of the camera
acc = 0.0008
# max velocity of the camera (per axis)
v_max = 0.3
# dampening factor for the camera motion
damp = 0.95
# stop the velocity if it is smaller than this value
stop_limit = 0.0001

# multiply by the height so that the camera
# moves faster when it's further up
acc *= cam_height
v_max *= cam_height
stop_limit *= cam_height

# calculate the acceleration and new velocity
a_x = acc * (press_d.positive - press_a.positive)
a_y = acc * (press_w.positive - press_s.positive)
v_x += a_x
v_y += a_y
v_x *= damp
v_y *= damp


# velocity limits
if(abs(v_x) < stop_limit):
    v_x = 0
if(abs(v_y) < stop_limit):
    v_y = 0
if(abs(v_x) > v_max):
    v_x = v_max*sign(v_x)
if(abs(v_y) > v_max):
    v_y = v_max*sign(v_y)



############# z motion ###############

v_speed = 0.07
camera_min_height = 4


v_z = v_speed * cam_height * (wheel_down.positive - wheel_up.positive)

if( cam_height < camera_min_height and v_z < 0):
    v_z = 0

############# directors ##############
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

frame_nr = cam["frame_nr"]
neutval = [0] * 7
oldval = neutval
newval = neutval
rotation_euler = cam.orientation.to_euler()
curval = [cam["frame_nr_exact"] / total_phase_length, cam.position.x, cam.position.y, cam.position.z, rotation_euler.x, rotation_euler.y, rotation_euler.z]
shouldval = neutval
vr_x = vr_y = vr_z = 0
for d in cam["directors"]:
    if d[0] > frame_nr:
        newval = d
        break
    else:
        oldval = d
if oldval != newval and oldval != neutval and newval != neutval:
    prog = curval[0] / (newval[0] - oldval[0])
    for i in range(1, 4):
        shouldval[i] = lerp(oldval[i], newval[i], prog)
    for i in range(4, 7):
        shouldval[i] = lerp_angle(oldval[i], newval[i], prog)
    _, v_x, v_y, v_z, vr_x, vr_y, vr_z = (s - c for s, c in zip(shouldval, curval))

move.dLoc = [v_x, v_y, v_z]
move.dRot = [vr_x, vr_y, vr_z]
controller.activate(move)

if space.positive:
    print(" ".join(map(str, curval)))
