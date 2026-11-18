# ws19: lift + shear the west-face barrel tile course so it sits on top of the WS18 skirt (the skirt was burying it 3-12 cm).
import bpy,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE')=='1'
dg=bpy.context.evaluated_depsgraph_get()
sk=bpy.data.objects['WS18_Morehead_W_eave_tile_skirt_UNVERIFIED']
e=sk.evaluated_get(dg).to_mesh(); M=sk.matrix_world
SK=BVHTree.FromPolygons([M@v.co for v in e.vertices],[list(p.vertices) for p in e.polygons],all_triangles=False); sk.evaluated_get(dg).to_mesh_clear()
OUT=Vector((-0.97,0.24,0)).normalized(); AL=Vector((0.24,0.97,0)).normalized(); P0=Vector((-40.03,-56.5,0))
bc=bpy.data.objects['Morehead Hall barrel tile eave course']; me=bc.data; W=bc.matrix_world; Wi=W.inverted()
n=0; sh=[]
for v in me.vertices:
    p=W@v.co; d=Vector((p.x,p.y,0))-P0; a=d.dot(AL); t=d.dot(OUT)
    if not (-11.0<=a<=14.0 and 0.25<=t<=1.1 and p.z<144.2): continue
    tt=min(t,0.82); q=P0+AL*a+OUT*tt
    h,_,_,_=SK.ray_cast(Vector((q.x,q.y,160)),Vector((0,0,-1)),40)
    if h is None: continue
    S=h.z-0.66*(t-tt)
    s=(S+0.02)-(143.87-0.3*(t-0.5))
    s=max(0.0,min(s,0.18))
    sh.append(s)
    if SAVE: v.co=Wi@Vector((p.x,p.y,p.z+s))
    n+=1
print('VERTS',n,'shift min/max/mean',round(min(sh),3),round(max(sh),3),round(sum(sh)/len(sh),3))
if SAVE:
    me.update(); bc['ws19']='west strip lifted onto WS18 skirt'; bpy.ops.wm.save_mainfile(); print('SAVED')
