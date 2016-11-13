import bge
controller = bge.logic.getCurrentController()
move = controller.actuators["move"]

# get sensor data
press_w = controller.sensors["w"]
press_a = controller.sensors["a"]
press_s = controller.sensors["s"]
press_d = controller.sensors["d"]
wheel_up = controller.sensors["wheel up"]
wheel_down = controller.sensors["wheel down"]

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
acc = 0.2
# max velocity of the camera (per axis)
v_max = 1
# dampening factor for the camera motion
damp = 0.9
# stop the velocity if it is smaller than this value
stop_limit = 0.05

a_x = acc * (press_d.positive - press_a.positive)
a_y = acc * (press_w.positive - press_s.positive) 

v_x += a_x
v_y += a_y

v_x *= damp
v_y *= damp

if(abs(v_x) < stop_limit):
    v_x = 0
if(abs(v_y) < stop_limit):
    v_y = 0
    
if(abs(v_x) > v_max):
    v_x = v_max*sign(v_x)
if(abs(v_y) > v_max):
    v_y = v_max*sign(v_y)



############# z motion ###############

v_speed = 0.7

v_z = v_speed * (wheel_down.positive - wheel_up.positive)


move.dLoc = [v_x, v_y, v_z]
controller.activate(move)