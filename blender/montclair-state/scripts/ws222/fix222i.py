# ws222i (Codex P1 on PR #23, AGENTS.md rule 6 "raise paving, never lower it"): fix222b/d lowered asphalt verts under the
# crossing walks. This makes the net change from ws221c raise-only:
# (1) every WS214 underfill / KY / WS67 vert in the crossing box gets z = max(ws221c z, current z), i.e. all net lowering undone;
# (2) where an asphalt vert now sits within 1 cm of (or above) the WS215 sidewalk / WS72 landing top it runs under, the WALK
#     top verts within 0.35 m are RAISED to that asphalt z + 1 cm (raise-only), so the walk clears the asphalt again.
import bpy, os
from mathutils import Vector
SRC=os.environ.get('SRC221','/workspace/nj-scenes/montclair-state/montclair_state_ws221c.blend')
PFX=('WS214_N_berm_tip_gap_asphalt_underfill','WS67_CollegeAve_gap_asphalt','KY_college_ave_carriageway_asphalt')
A=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(PFX)]
names=[o.name for o in A]
import shutil, tempfile
if os.path.abspath(bpy.data.filepath)==os.path.abspath(SRC):   # rebuilding from ws221c itself: load from a temp copy
    _tmp=os.path.join(tempfile.gettempdir(),'ws221c_src_copy_222i.blend'); shutil.copyfile(SRC,_tmp); SRC=_tmp
with bpy.data.libraries.load(SRC) as (src,dst): dst.meshes=[A_.data.name for A_ in A]
orig={}
for o,m in zip(A,dst.meshes):
    orig[o.name]=[v.co.copy() for v in m.vertices]
BOX=(-257.2,-253.8,-54.2,-52.1)
inb=lambda w:BOX[0]<=w.x<=BOX[1] and BOX[2]<=w.y<=BOX[3]
for o in A:
    M=o.matrix_world; MI=M.inverted(); oc=orig[o.name]; assert len(oc)==len(o.data.vertices); n=0
    for i,v in enumerate(o.data.vertices):
        w=M@v.co; w0=M@oc[i]
        if inb(w) and w0.z>w.z+1e-5:
            print('F222I restore %s v%d z %.3f -> %.3f'%(o.name[:6],i,w.z,w0.z),flush=True); v.co=oc[i].copy(); n+=1
    o.data.update(); print('F222I',o.name[:30],'restored',n,flush=True)
for m in dst.meshes: bpy.data.meshes.remove(m)
if SRC.endswith('ws221c_src_copy_222i.blend'): os.remove(SRC)
WALKS=[bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']]+[o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level_sidewalk')]
def slab_top(s,x,y,z):
    SM=s.matrix_world; SI=SM.inverted()
    ok,loc,n,fi=s.ray_cast(SI@Vector((x,y,z+2.0)),(SI.to_3x3()@Vector((0,0,-1))).normalized(),distance=6.0)
    if ok:
        hz=(SM@loc).z
        if abs(hz-z)<0.6: return hz
    return None
need=[]   # asphalt points that poke within 1 cm of a walk top
for o in A:
    M=o.matrix_world
    for v in o.data.vertices:
        w=M@v.co
        if not inb(w): continue
        for s in WALKS:
            t=slab_top(s,w.x,w.y,w.z)
            if t is not None and w.z>t-0.01: need.append((s.name,w.copy(),t))
print('F222I asphalt points too close to a walk top:',len(need),flush=True)
for s in WALKS:
    SM=s.matrix_world; SI=SM.inverted(); pts=[(w,t) for nm,w,t in need if nm==s.name]
    if not pts: continue
    # top verts = verts with a linked up-facing face
    top=set()
    for p in s.data.polygons:
        if p.normal.z>0.5: top.update(p.vertices)
    n=0
    for i in top:
        v=s.data.vertices[i]; w=SM@v.co
        if not inb(w): continue
        near=[p for p,t in pts if (p.xy-w.xy).length<=0.35]
        if not near: continue
        tz=max(p.z for p in near)+0.01
        if tz>w.z:
            # raise the matching bottom vert too only if the slab would get thinner than 10 cm (it won't here); top only
            print('F222I raise %s v%d (%.3f,%.3f) z %.3f -> %.3f'%(s.name[:6],i,w.x,w.y,w.z,tz),flush=True); w.z=tz; v.co=SI@w; n+=1
    s.data.update(); print('F222I',s.name[:30],'top verts raised',n,flush=True)
