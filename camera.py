import bge
controller = bge.logic.getCurrentController()
move = controller.actuators["move"]

cam = controller.owner

# get sensor data
press_w = controller.sensors["w"]
press_a = controller.sensors["a"]
press_s = controller.sensors["s"]
press_d = controller.sensors["d"]
wheel_up = controller.sensors["wheel up"]
wheel_down = controller.sensors["wheel down"]

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
acc = 0.001
# max velocity of the camera (per axis)
v_max = 0.1
# dampening factor for the camera motion
damp = 0.95
# stop the velocity if it is smaller than this value
stop_limit = 0.0005

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

move.dLoc = [v_x, v_y, v_z]
controller.activate(move)
