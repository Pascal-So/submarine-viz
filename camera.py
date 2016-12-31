import bge
import os
import mathutils
controller = bge.logic.getCurrentController()
move = controller.actuators["move"]
cam = controller.owner

turn_phase_length = 4
move_phase_length = 8

export_path = "export"
export_prefix = "export"
export = False

# ^^^^^^^^^^^^ adjust speed settings here ^^^^^^^^^^^^^^^^^
total_phase_length = turn_phase_length + move_phase_length

# get sensor data
press_w = controller.sensors["w"]
press_a = controller.sensors["a"]
press_s = controller.sensors["s"]
press_d = controller.sensors["d"]
press_q = controller.sensors["q"]
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
camera_min_height = 0


v_z = v_speed * cam_height * (wheel_down.positive - wheel_up.positive)

if( cam_height < camera_min_height and v_z < 0):
    v_z = 0

############# directors ##############
def lerp(val1, val2, frac):
    """ linear interpolation """
    return val1 * (1-frac) + val2 * frac

frame_nr = cam["frame_nr"]
neutval = [0] * 7
oldval = neutval
newval = neutval
rotation_euler = cam.orientation.to_euler()
curval = [cam["frame_nr_exact"] / total_phase_length, cam.position.x, cam.position.y, cam.position.z, rotation_euler.x, rotation_euler.y, rotation_euler.z]
shouldval = neutval
vr_x = vr_y = vr_z = 0
for d in cam["directors"]:
    if d[0] > curval[0]:
        newval = d
        break
    else:
        oldval = d
if oldval != newval and oldval != neutval and newval != neutval and not cam["directors_paused"]:
    prog = (curval[0] - oldval[0]) / (newval[0] - oldval[0])
    for i in range(1, 4):
        shouldval[i] = lerp(oldval[i], newval[i], prog)
    new_rot = mathutils.Euler(newval[4:7]).to_quaternion()
    old_rot = mathutils.Euler(oldval[4:7]).to_quaternion()
    cur_rot = mathutils.Euler(curval[4:7]).to_quaternion()
    should_rot = old_rot.slerp(new_rot, prog)
    shouldval[4:7] = should_rot.to_euler()
    _, v_x, v_y, v_z, vr_x, vr_y, vr_z = (s - c for s, c in zip(shouldval, curval))
    cam.orientation = should_rot.to_matrix()

move.dLoc = [v_x, v_y, v_z]
#move.dRot = [vr_x, vr_y, vr_z]
controller.activate(move)

if space.positive:
    print(" ".join(map(str, curval)))

if press_q.positive:
    cam["directors_paused"] = not cam["directors_paused"]

if export:
    filename = os.path.join(export_path, export_prefix + str(cam["frame_nr_exact"]).zfill(8) + ".png")
    bge.render.makeScreenshot(os.path.abspath(filename))
