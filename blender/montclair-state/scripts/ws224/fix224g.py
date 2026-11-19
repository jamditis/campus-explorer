# ws224g: the WS71 Kasser S sidewalk W edge (x -243.0) stands 0.8-7 cm over the WS72 landing E edge (worst at the S end,
# 126.266 vs 126.197): a lit step line across the walk. Raise-only (rule 6): WS72 top verts raised by the seam step d(y)
# (interpolated along the seam, minus 1 mm), tapered linearly to 0 over 1.5 m west of the seam (<= 4.7 % added grade).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(n): return [o for o in bpy.data.objects if o.name.startswith(n)][0]
A=ob('WS72_Kasser_SW_RHD_core_sidewalk_landing'); C=ob('WS71_Kasser_S_sidewalk')
MA=A.matrix_world; MAI=MA.inverted(); MC=C.matrix_world; RC=MC.to_3x3(); RA=MA.to_3x3()
TC=BVHTree.FromPolygons([MC@v.co for v in C.data.vertices],[p.vertices[:] for p in C.data.polygons if (RC@p.normal).z>0.3])
top=set(i for p in A.data.polygons if (RA@p.normal).z>0.3 for i in p.vertices)
seam=[]
for i in top:
    w=MA@A.data.vertices[i].co
    if abs(w.x+243.0)<0.01:
        h=TC.ray_cast(Vector((-242.97,w.y,130)),Vector((0,0,-1)))
        if h[0] is not None: seam.append((w.y,max(0.0,h[0].z-0.001-w.z)))
seam.sort(); print('F224G seam',[('%.2f'%y,'%.1fcm'%(d*100)) for y,d in seam],flush=True)
def d_at(y):
    if y<=seam[0][0]: return seam[0][1]
    for (y0,d0),(y1,d1) in zip(seam,seam[1:]):
        if y0<=y<=y1: return d0+(d1-d0)*(y-y0)/(y1-y0)
    return 0.0
n=0
for i in top:
    v=A.data.vertices[i]; w=MA@v.co
    if -244.51<w.x<=-242.99:
        k=max(0.0,1-(-243.0-w.x)/1.5); dz=d_at(w.y)*k
        if dz>0.0005: w.z+=dz; v.co=MAI@w; n+=1; print('F224G v%d (%.2f,%.2f) +%.1f cm'%(i,w.x,w.y,dz*100),flush=True)
A.data.update(); print('F224G raised',n,flush=True)
