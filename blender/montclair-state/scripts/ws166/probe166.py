import bpy, os
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=lambda n: n.startswith(('WS110_ground','WS163_','WS165_'))
with bpy.data.libraries.load(M) as (s,d): d.objects=[n for n in s.objects if want(n)]
for o in d.objects:
    if o: bpy.context.scene.collection.objects.link(o)
print('LOADED',len(d.objects),flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
import numpy as np
def report(tag):
    mu=OB['WS165_aisle_mouth_mulch_bed_graded_to_walk_UNIFY69']; sp=OB['WS165_concrete_spur_N_of_walk_ortho2020_UNVERIFIEDfunction']
    pa=OB['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']; gp=OB['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']
    TM=bvh([mu]); TS=bvh([sp]); TG=bvh([pa,gp])
    out=[]
    for y in np.arange(wb(-300)+0.05,YN-0.2,0.4):
        a=hz(TM,-300.03,y); b=hz(TS,-299.97,y)
        out.append(None if a is None or b is None else round(a-b,3))
    print(tag,'E edge mulch-spur',out,flush=True)
    bad=[]
    for x in np.arange(XW+0.02,XE+0.2,0.05):
        for y in np.arange(wb(x)+0.01,YN+0.05,0.05):
            g=hz(TG,x,y); m=hz(TM,x,y); s=hz(TS,x,y)
            top=max([z for z in (m,s) if z is not None],default=None)
            if top is None: continue
            if g is not None and g>top-0.005 and inside(min(max(x,xi0),XE),y): bad.append((round(x,2),round(y,2),round(g-top,3)))
    print(tag,'lawn-above pts',len(bad),bad[:12],flush=True)
report('BEFORE')
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/fix166.py').read())
report('AFTER')
