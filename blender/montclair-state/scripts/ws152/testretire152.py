import bpy
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
src=open(M+'scripts/ws152/apply152.py').read().replace("bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws152f.blend',copy=True)","pass")
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc=bpy.context.scene
ring=[(-92.966,-168.958),(-105.022,-220.367),(-90.374,-223.781),(-78.293,-172.383)]
me=bpy.data.meshes.new('pw'); vs=[(x+0.1,y,125.0) for x,y in ring]+[(x+0.1,y,146.9) for x,y in ring]
me.from_pydata(vs,[],[(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]); me.update()
w=bpy.data.objects.new('Freeman Hall walls',me); sc.collection.objects.link(w)
def cube(name,loc,sz):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.scale=sz
cube('VR_Freeman_W_interbay_dark_00_UNVERIFIED',(-99.0+(-0.974*0.1),-194.7,135),(0.1,1,10))
cube('UY_Freeman_E_glass_UNVERIFIED',(-84.3+0.974*0.05,-198.0,135),(0.1,1,10))
cube('VT_Freeman_N_entrance_landing_UNVERIFIED',(-86,-170,128),(3,2,0.3))
cube('UY_Freeman_glass_all_sides',(-91,-196,135),(28,56,10))
exec(src)
for o in bpy.data.objects: print('OBJ',o.name,o.hide_render)
