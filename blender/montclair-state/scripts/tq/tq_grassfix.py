# tq: grass clumps floating 0.3-2 m above the ground round Stone Hall (seen as a dark line across Stone's west wall from TQ_CAM_eye_Stone_from_W).
# Points in box x 110..190, y 200..320 whose z is > 0.25 m above the highest ground surface below them are snapped down to it.
# Mesh swap (original kept with fake user as o['tq_orig_mesh']); tq_main REVERT restores it exactly.
import bpy, os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
G=[]
for n in GN:
    o=bpy.data.objects.get(n)
    if o: e=o.evaluated_get(dg); G.append((e,o.matrix_world.copy(),o.matrix_world.inverted()))
def gz(x,y):
    best=None
    for e,mw,iw in G:
        r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z; best=z if best is None or z>best else best
    return best
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BOX','110,190,200,320').split(',')]
tot=0
for o in list(bpy.data.objects):
    if o.type!='MESH' or 'grass' not in o.name.lower() or len(o.data.polygons)>0 or not o.data.vertices: continue
    mw=o.matrix_world; iw=mw.inverted(); fix=[]
    for v in o.data.vertices:
        w=mw@v.co
        if X0<w.x<X1 and Y0<w.y<Y1:
            g=gz(w.x,w.y)
            if g is not None and w.z-g>0.25: fix.append((v.index,w,g))
    if not fix: continue
    me=o.data; o['tq_orig_mesh']=me.name; me.use_fake_user=True; nm=me.copy(); nm.name=me.name+'.tq'; o.data=nm; o['tq_snapped']=len(fix)
    for i,w,g in fix: nm.vertices[i].co=iw@Vector((w.x,w.y,g))
    tot+=len(fix); print('TQGRASS',o.name,len(fix),'max lift',round(max(w.z-g for i,w,g in fix),2))
print('TQGRASS total',tot)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
