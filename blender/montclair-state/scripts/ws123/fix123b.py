import bpy, math
e=bpy.data.objects['WS123_Chapin_W_planter_tree_HoneyLocust_young_UNVERIFIEDspecies']
src=[o for o in e.instance_collection.all_objects if o.type=='MESH'][0]; off=src.location
S=e.scale.x; RZ=e.rotation_euler.z
ox=S*(off.x*math.cos(RZ)-off.y*math.sin(RZ)); oy=S*(off.x*math.sin(RZ)+off.y*math.cos(RZ))
e.location.x=-208.3-ox; e.location.y=-168.6-oy; print('F123 off',tuple(off),round(ox,2),round(oy,2),tuple(e.location))
bpy.ops.wm.save_mainfile(); print('F123 SAVED')
