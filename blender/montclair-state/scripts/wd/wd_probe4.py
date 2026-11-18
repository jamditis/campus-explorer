import bpy, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
L=bpy.data.objects['TK_Bohn_landing_N_steps_UNVERIFIED']
lv=[L.matrix_world@v.co for v in L.data.vertices]
G=bpy.data.objects['TK_Bohn_door_glass_N_steps_UNVERIFIED']
gv=[G.matrix_world@v.co for v in G.data.vertices]
gc=sum(gv,Vector())/len(gv)
s=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].evaluated_get(dg)
def hit(x,y):
    r=s.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    return r[1].z if r[0] else None
A=Vector((222.41,416.16,0));B=Vector((231.01,412.36,0));u=(B-A).normalized()
prof=[(round(t,2),round(hit(*(A+u*t).xy) or -1,3)) for t in [i*0.25 for i in range(-20,40)]]
# also lateral ground grid around
grid=[[round(x,2),round(y,2),round(hit(x,y) or -1,3)] for x in [218+i*0.5 for i in range(30)] for y in [406+j*0.5 for j in range(26)]]
W=[(L.matrix_world@v.co) for v in L.data.vertices]
json.dump(dict(landing=[list(p) for p in lv],landing_faces=[list(f.vertices) for f in L.data.polygons],glass_c=list(gc),glass=[list(p) for p in gv],prof=prof,grid=grid,
  door_w=[list(bpy.data.objects['TK_Bohn_landing_W_walk_UNVERIFIED'].matrix_world@v.co) for v in bpy.data.objects['TK_Bohn_landing_W_walk_UNVERIFIED'].data.vertices]),open('data/wd/probe4.json','w'))
print('OK',len(lv))
