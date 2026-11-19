# ws217 W35e: the WS215 walk meets the KX deck drive apron as a 20-30 cm face near College Ave (ws216c). AGENTS.md rule 6:
# raise paving, never lower it. (1) RAISE the apron's E-edge vertex column (top verts only) so the walk stands a standard
# 15 cm curb above it; the apron's last 1.1 m strip becomes a gentle edge warp (driveway edge flare), nothing lowered.
# (2) The apron's safety-yellow edge treatment (KY_safety_yellow_paint_UNVERIFIED on its vertical side faces) is hidden
# under the walk edge since ws216c; carry it onto the visible curb face = the walk's W-facing side faces along the apron.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
SL=ob('WS215_RHD_SE_core_street_level_sidewalk'); AP=ob('KX_drive_apron')
def bvh(o,top=False):
    M=o.matrix_world; P=[p for p in o.data.polygons if (not top) or (M.to_3x3()@p.normal).z>0.7]
    return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in P])
def ray(t,x,y):
    h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300); return h[0].z if h[0] is not None else None
TS=bvh(SL,top=True)
Ma=AP.matrix_world; Mai=Ma.inverted(); n=0; mx=0
for i in range(160,180,2):
    v=AP.data.vertices[i]; w=Ma@v.co
    if w.z<123.5: continue
    zw=None
    for dx in (0.10,0.2,0.3):
        zw=ray(TS,w.x+dx,w.y)
        if zw is not None: break
    if zw is None: print('F217a no walk at',i,round(w.x,2),round(w.y,2),flush=True); continue
    tgt=zw-0.15; dz=tgt-w.z
    print('F217a v',i,'y',round(w.y,2),'apron',round(w.z,3),'walk',round(zw,3),'face',round(zw-w.z,3),'dz',round(max(dz,0),3),flush=True)
    if dz>0.002:
        v.co=Mai@Vector((w.x,w.y,tgt)); n+=1; mx=max(mx,dz)
        # bottom twin keeps its depth (slab stays closed)
AP.data.update()
print('F217a apron E-edge top verts raised',n,'max',round(mx,3),flush=True)
YM=bpy.data.materials.get('KY_safety_yellow_paint_UNVERIFIED')
if YM.name not in [m.name for m in SL.data.materials if m]: SL.data.materials.append(YM)
yi=[m.name if m else '' for m in SL.data.materials].index(YM.name)
M=SL.matrix_world; R=M.to_3x3(); ny=0
xs=[(M@v.co).x for v in SL.data.vertices]
for p in SL.data.polygons:
    nn=(R@p.normal).normalized(); c=M@p.center
    if abs(nn.z)<0.3 and nn.x<-0.7 and -51.0<=c.y<=-43.3 and c.x<-264.5:
        p.material_index=yi; ny+=1
SL.data.update()
print('F217a walk W curb faces painted yellow',ny,flush=True)
