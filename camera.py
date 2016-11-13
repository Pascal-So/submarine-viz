import bge
controller = bge.logic.getCurrentController()
move = controller.actuators["move"]

press_w = cont.sensors["w"]
press_a = cont.sensors["a"]
press_s = cont.sensors["s"]
press_d = cont.sensors["d"]
wheel_up = cont.sensors["wheel up"]
wheel_down = cont.sensors["wheel down"]

v_x = move.dLoc[0]
v_y = move.dLoc[1]