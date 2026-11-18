# ws121 e: UNIFY #28 dark slot at the stair foot S corner = the WS120 S-wing apron (flat 122.875) stood ~0.2 m above the
# WS117 corridor / lowest riser foot (122.67), leaving a shadowed step face. Re-grade the apron to the corridor (5 % run to
# the foot, then level at the foot beside the stair); window sill 123.11 stays 0.44 m clear. Lawn under it pushed down.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
def bvo(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([tuple(mw@v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def zh(b,x,y):
    h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); return None if h[0] is None else h[0].z
COR=bvo(ob('WS116_Chapin_W_plaza_E_corridor'))
def zt(x):
    z=zh(COR,min(x,-217.15),-200.6)
    return (z if z is not None else 122.67)+0.003
ap=ob('WS120_Chapin_W_S_wing_door_apron'); mw=ap.matrix_world; inv=mw.inverted()
tops={}
for v in ap.data.vertices:
    w=mw@v.co; k=(round(w.x,3),round(w.y,3)); tops[k]=max(tops.get(k,-1e9),w.z)
n=0; dz=[]
for v in ap.data.vertices:
    w=mw@v.co; t=tops[(round(w.x,3),round(w.y,3))]; nz=min(t,zt(w.x)); d=nz-t
    if d<0: w.z+=d; v.co=inv@w; n+=1; dz.append(d)
ap.data.update(); print('M121e apron verts',n,'dz',round(min(dz),3) if dz else 0)
BA=bvo(ap)
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    o=ob(nm); m=o.matrix_world; iv=m.inverted(); c=0
    for v in o.data.vertices:
        w=m@v.co
        if -204.0<=w.y<=-200.8 and -219.3<=w.x<=-215.0:
            zz=[zh(BA,w.x+dx,w.y+dy) for dx in (-0.4,0,0.4) for dy in (-0.4,0,0.4)]; zz=[z for z in zz if z is not None]
            if zz and w.z>min(zz)-0.06: w.z=min(zz)-0.06; v.co=iv@w; c+=1
    o.data.update(); print('M121e',nm,'pushed',c)
px=next((o for o in bpy.data.objects if o.name.startswith('WS113_paving_tops_proxy')),None)
if px:
    m=px.matrix_world; iv=m.inverted(); c=0
    for v in px.data.vertices:
        w=m@v.co
        if -203.6<=w.y<=-201.0 and -219.0<=w.x<=-215.3 and w.z>zt(w.x)+0.01: w.z=zt(w.x); v.co=iv@w; c+=1
    px.data.update(); print('M121e proxy lowered',c)
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M121e SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M121e SAVED',SAVE)
