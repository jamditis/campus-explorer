# ws121 d: self-review fix. Footpaths_OSM's GN stack drapes the walk 10-17 cm below its base mesh, so the flare's N
# edge (matched to the base mesh) stood as a lip. Re-match the last 0.9 m of the flare to the EVALUATED walk surface.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
fpo=bpy.data.objects['Footpaths_OSM']; mw=fpo.matrix_world
B0=BVHTree.FromPolygons([tuple(mw@v.co) for v in fpo.data.vertices],[tuple(p.vertices) for p in fpo.data.polygons])
dg=bpy.context.evaluated_depsgraph_get(); e=fpo.evaluated_get(dg); me=e.to_mesh()
BE=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear()
def zh(b,x,y):
    h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); return None if h[0] is None else h[0].z
fl=next(o for o in bpy.data.objects if o.name.startswith('WS121_Chapin_W_plaza_NW_corner')); fw=fl.matrix_world; inv=fw.inverted()
def d(x):
    xc=min(max(x,-210.7),-207.6); a=zh(BE,xc,-159.6); b=zh(B0,xc,-159.63)
    return 0 if (a is None or b is None) else (a+0.005)-b
n=0; ds=[]
for v in fl.data.vertices:
    w=fw@v.co
    t=(w.y+160.65)/0.9
    if t>0:
        dz=d(w.x)*min(t,1); w.z+=dz; v.co=inv@w; n+=1; ds.append(dz)
fl.data.update(); print('M121d moved',n,'dz range',round(min(ds),3),round(max(ds),3))
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M121d SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M121d SAVED',SAVE)
