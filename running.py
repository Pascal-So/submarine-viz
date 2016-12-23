import bge

c = bge.logic.getCurrentController()
ob = c.owner


def tick(pointer, log_lines):
    #print(pointer)
    pass
    
    
    

if "frame_nr" in ob and ob["frame_nr"] >= 0:
    # we don't need no .. optimization... dum dudum dum dum ..
    tick(ob["pointer"], ob["log_lines"])
    ob["frame_nr"]+=1
    print(ob["frame_nr"])
    