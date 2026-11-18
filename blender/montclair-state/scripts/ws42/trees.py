import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def tree(n):
    ob=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(ob.evaluated_get(dg).to_mesh()); bm.transform(ob.matrix_world); return BVHTree.FromBMesh(bm)
T=tree('Terrain_LiDAR_DTM_1m'); SAVE=os.environ.get('SAVE')=='1'; n=0; ds=[]
for o in bpy.data.objects:
    if not o.name.startswith('T_') or o.hide_render or o.parent: continue
    x,y,_=o.matrix_world.translation; z=min((o.matrix_world@Vector(c)).z for c in o.bound_box)
    if not (-300<x<-120 and -180<y<-30): continue
    zs=[]
    for dx,dy in ((0,0),(0.4,0),(-0.4,0),(0,0.4),(0,-0.4)):
        r=T.ray_cast(Vector((x+dx,y+dy,z+50)),Vector((0,0,-1)),200)
        if r[0]: zs.append(r[0].z)
    if not zs: continue
    g=min(zs); d=z-g; ds.append(d)
    if abs(d+0.05)>0.15:
        print('TR',o.name,round(x,1),round(y,1),'delta',round(d,2)); n+=1
        h=bpy.context.scene.ray_cast(dg,Vector((x,y,z+30)),Vector((0,0,-1)))
        print('TR   first-hit',h[4].name if h[0] else None, round(h[1].z,2) if h[0] else None)
        if SAVE and abs(d)<2.0: o.matrix_world.translation.z+= (g-0.05)-z
print('TR checked',len(ds),'off',n,'median',sorted(ds)[len(ds)//2] if ds else None)
if SAVE: bpy.ops.wm.save_mainfile()
