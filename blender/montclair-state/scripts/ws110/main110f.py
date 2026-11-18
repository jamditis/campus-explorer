# push the WS60 terrain-edge apron (and any other ground sheet) under the new 1 m DTM patch inside its footprint
import bpy, numpy as np
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state/'
D=np.load(R+'prep/ws79_normal_ave_dtm/normal_ave_dtm_1m.npz'); DT=D['dtm']; DX0=float(D['x0']); DY0=float(D['y0'])
def dtm(x,y):
    fx=x-DX0; fy=y-DY0; j=int(np.floor(fx)); i=int(np.floor(fy))
    j=min(max(j,0),DT.shape[1]-2); i=min(max(i,0),DT.shape[0]-2); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith(('WS60_terrain_edge_apron',)): continue
    mw=o.matrix_world; inv=mw.inverted(); n=0
    for v in o.data.vertices:
        w=mw@v.co
        if -300<=w.x<=-150 and -300<=w.y<=-250.5:
            zt=dtm(w.x,w.y)-0.35
            if w.z>zt: v.co=inv@Vector((w.x,w.y,zt)); n+=1
    o.data.update(); print('E110f',o.name,'pushed',n,[ (m.type,m.name) for m in o.modifiers])
bpy.ops.wm.save_mainfile(); print('M110 SAVED f',flush=True)
exec(open(R+'scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws110/render_cut110'))
