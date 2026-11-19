# ws224j: the WS72b Kasser S sidewalk (east to Cole) starts at x -222 lying 4.6-5.9 cm ABOVE the WS71 walk it overlaps
# (they converge by x -221.5), a pale lip line across the walk. Raise-only (rule 6): WS71 top verts under WS72b raised to
# WS72b - 2 mm; west of x -222 each row's seam raise is tapered to 0 over 3 m (<= 2 % added grade). WS72b untouched.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(n): return [o for o in bpy.data.objects if o.name.startswith(n)][0]
A=ob('WS71_Kasser_S_sidewalk_ortho'); B=ob('WS72b_Kasser_S_sidewal')
MA=A.matrix_world; MAI=MA.inverted(); RA=MA.to_3x3(); MB=B.matrix_world; RB=MB.to_3x3()
TB=BVHTree.FromPolygons([MB@v.co for v in B.data.vertices],[p.vertices[:] for p in B.data.polygons if (RB@p.normal).z>0.3])
def zb(x,y):
    h=TB.ray_cast(Vector((x,y,140)),Vector((0,0,-1))); return h[0].z if h[0] else None
top=set(i for p in A.data.polygons if (RA@p.normal).z>0.3 for i in p.vertices)
W={i:MA@A.data.vertices[i].co for i in top}
seam=[]
for i,w in W.items():
    if abs(w.x+222.0)<0.01:
        z=zb(-221.99,w.y); seam.append((w.y,max(0.0,z-0.002-w.z) if z else 0.0))
seam.sort()
def d_at(y):
    if y<=seam[0][0]: return seam[0][1]
    if y>=seam[-1][0]: return seam[-1][1]
    for (y0,d0),(y1,d1) in zip(seam,seam[1:]):
        if y0<=y<=y1: return d0+(d1-d0)*(y-y0)/(y1-y0)
plan={}
for i,w in W.items():
    if -222.01<=w.x<=-214.4:
        z=zb(max(w.x,-221.99),w.y); dz=max(0.0,z-0.002-w.z) if z else 0.0
    elif -225.01<w.x<-222.01:
        dz=d_at(w.y)*(1-(-222.0-w.x)/3.0)
    else: continue
    if dz>0.0005: plan[i]=dz
for i,dz in sorted(plan.items()):
    v=A.data.vertices[i]; w=MA@v.co; w.z+=dz; v.co=MAI@w
    print('F224J v%d (%.2f,%.2f) +%.1f cm'%(i,w.x,w.y,dz*100),flush=True)
A.data.update(); print('F224J raised',len(plan),flush=True)
