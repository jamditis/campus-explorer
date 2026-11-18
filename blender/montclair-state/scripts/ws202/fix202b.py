# ws202 W19 leftovers: faint dashes along the old WS75/WS80 joint in the Sprague-lot S bay.
# Probe p202a (0.025 m top-object grid, real GN terrain): residual vs a 0.4 m local median plane shows 2-9 mm LOW cells on
# WS81 underlay / WS94 slit filler slivers (mean -5 mm) and on WS75/WS80 edge cells (mean -3 mm) along the old seam.
# Designer call (same as ws201): one flush asphalt mat. RAISE-ONLY to the local median plane: exposed low verts -> plane (+bias);
# covered underlay/filler verts -> 1.5 mm (WS81) / 1 mm (WS94) under the sheet above. Cap 2.5 cm. Paint untouched (not in the box's low cells).
import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
G=np.load(os.environ['GRID']); R=G['R']; xs=G['xs']; ys=G['ys']; M=G['Z']-R
X0,X1,Y0,Y1=[float(a) for a in os.environ['FBOX'].split(',')]
ST=xs[1]-xs[0]
PF={'WS75_sprague_lot_asphalt':0.0,'WS80_sprague_lot_fill_asphalt':0.0,'WS94_lot_slit_filler':-0.001,'WS81_lot_seam_underlay':-0.0015,'WS76_accessible_lot':0.0,'WS199_lot_gap_patch':0.0}
SH={o.name:b for o in bpy.data.objects if o.type=='MESH' for p,b in PF.items() if o.name.startswith(p)}
def cellz(x,y):
    i=int(round((x-xs[0])/ST)); j=int(round((y-ys[0])/ST))
    if 0<=i<len(xs) and 0<=j<len(ys): return i,j
    return None
def bvh(excl):
    V=[];F=[]
    for n in SH:
        if n==excl: continue
        o=bpy.data.objects[n]; mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
tot=0
for n,b in SH.items():
    o=bpy.data.objects[n]; mw=o.matrix_world; mi=mw.inverted(); T=bvh(n); nl=0; mx=0; nin=0
    for v in o.data.vertices:
        p=mw@v.co
        if not (X0<p.x<X1 and Y0<p.y<Y1): continue
        nin+=1
        h=T.ray_cast(Vector((p.x,p.y,p.z+0.3)),Vector((0,0,-1)),0.3)
        covered = h[0] is not None and h[0].z>p.z+0.0005
        if covered and b<0:
            t=h[0].z+max(b,-float(os.environ.get('EB','0.0015')))
        else:
            c=cellz(p.x,p.y)
            if c is None or not np.isfinite(R[c]): continue
            # use the min residual of the 3x3 neighbourhood of this vertex (dash cells sit between verts)
            i,j=c; r=np.nanmin(R[max(i-2,0):i+3,max(j-2,0):j+3]); 
            if not (r<-0.0015): continue
            t=np.nanmedian(M[max(i-2,0):i+3,max(j-2,0):j+3])+(max(b,-float(os.environ.get('EB','0.0015'))) if b<0 else b)
            if covered: t=min(t,h[0].z-0.001)
        d=t-p.z
        if 0.0005<d<0.025: p.z=t; v.co=mi@p; nl+=1; mx=max(mx,d)
    o.data.update(); tot+=nl; print('F202b',n[:30],'in box',nin,'lifted',nl,'max',round(mx,4),flush=True)
    del T
print('F202b total',tot,flush=True)
