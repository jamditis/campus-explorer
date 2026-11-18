# ws171c: WS110 ground patch S of Normal Ave W sits 0.5-0.85 m ABOVE the 2023 LiDAR DTM south of the S walk (probe171c: (-295.4,-272.1) +0.76,
# (-299.3,-277.5) +0.85, (-298.4,-279.9) +0.56, (-290.5,-294.3) +0.64) -> reads as a mound and buries the new yard-tree bases.
# Lower (never raise) patch verts south of the S walk back edge to smoothed DTM+0.02, feathered from 0.3 m to 1.8 m beyond the walk back edge.
import bpy, numpy as np
from mathutils import Vector
OB=bpy.data.objects
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N)
sw=OB['WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']
S=[float(np.dot(np.array(((sw.matrix_world@v.co).x,(sw.matrix_world@v.co).y))-A,N)) for v in sw.data.vertices]
sback=min(S); print('FIX171c S walk back s',round(sback,2),'front',round(max(S),2),flush=True)
p=OB['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']; mw=p.matrix_world; mi=mw.inverted()
n=0; mx=0
for v in p.data.vertices:
    w=mw@v.co; s=float(np.dot(np.array((w.x,w.y))-A,N))
    if not (-345<w.x<-262): continue
    f=min(max((sback-s-0.3)/1.5,0.0),1.0)
    if f<=0: continue
    zt=dz(w.x,w.y)+0.02; nz=w.z*(1-f)+zt*f
    if nz<w.z-0.005:
        mx=max(mx,w.z-nz); w.z=nz; v.co=mi@w; n+=1
p.data.update(); print('FIX171c verts lowered',n,'max',round(mx,2),flush=True)
