# ws194 WOBBLE #W3: Lot 3 S ramp N edge, W half (x -311.2..-307.0, y ~-234.5): asphalt borders the NW lawn corner
# (WS187 shoulder toe / WS186 bank lawn / WS169c bridge); probe194c: lawn 0.15 m N of the edge is -6..+4.4 cm vs the asphalt
# -> lawn laps on/off the edge = wavy dark line (W eye view, left). Fix: lawn graded to a clean 2 cm drop below the asphalt
# along the straight edge, feathered back to the original by 0.8 m; lawn under the asphalt clamped 3 cm below it.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _o(p):
    l=[o for o in bpy.data.objects if o.name.startswith(p)]; return l[0] if l else None
D=_o('WS163_Lot3_aisle_S_drive'); M=D.matrix_world
W=np.array([tuple(M@v.co) for v in D.data.vertices])
bm=bmesh.new(); bm.from_mesh(D.data)
bidx=sorted({v.index for e in bm.edges if e.is_boundary for v in e.verts}); bm.free()
B=W[bidx]; Nn=B[(B[:,1]>-235.4)&(B[:,0]<-306.9)]; Nn=Nn[np.argsort(Nn[:,0])]
DB=BVHTree.FromPolygons([Vector(w) for w in W],[p.vertices[:] for p in D.data.polygons])
def segd(px,py):
    best=(9,0)
    for a,b in zip(Nn,Nn[1:]):
        ab=b[:2]-a[:2]; t=np.clip(np.dot([px-a[0],py-a[1]],ab)/max(1e-9,ab@ab),0,1); q=a+t*(b-a)
        d=np.hypot(px-q[0],py-q[1])
        if d<best[0]: best=(d,q[2])
    return best
tot=0
for nm in ('WS187_Lot3_W_shoulder_toe','WS186_Lot3_S_bank_lawn','WS169c_Lot3_S_end_lawn','WS162_Lot3_W_shoulder_lawn'):
    o=_o(nm)
    if o is None: continue
    Mo=o.matrix_world; Moi=Mo.inverted(); c=0
    for v in o.data.vertices:
        p=Mo@v.co
        if not (-311.6<p.x<-306.9 and -236.0<p.y<-233.4): continue
        h=DB.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)))
        if h[0] is not None:
            if p.z>h[0].z-0.03: p.z=h[0].z-0.03; v.co=Moi@p; c+=1
            continue
        d,ez=segd(p.x,p.y)
        if d<0.8:
            t=d/0.8; t=t*t*(3-2*t); tgt=(1-t)*(ez-0.02)+t*p.z
            if d<0.4: tgt=min(tgt,ez-0.025+0.02*d)
            if abs(tgt-p.z)>1e-4: p.z=tgt; v.co=Moi@p; c+=1
    o.data.update(); tot+=c; print('FIX194b',nm,c,flush=True)
print('FIX194b total',tot,'edge pts',len(Nn),flush=True)
