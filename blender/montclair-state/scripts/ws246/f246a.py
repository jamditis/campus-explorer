# ws246 W62c bank lawn tone: the ws245 graded east bank (and the 1.5 m level margin) are Terrain_LiDAR_DTM_1m faces with
# Ground_ortho_grass, which tints Grass004 by the 2020 ortho through the 'ortho' UV. Where the ground was regraded the ortho
# texel under it shows the stand's aluminium seat tops / pad / fence line (pale grey), so the new bank read paler than the
# lawn around it. Fix (f240c pattern): every terrain loop whose vertex lies over the hold-under or bank-grade target (+2 m)
# and whose ortho texel is NOT lawn-green takes the UV of the nearest green texel outside the targets (1-20 m search).
# Geometry unchanged. DRY=1 reports only.
import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects[os.environ.get('F246OBJ','Terrain_LiDAR_DTM_1m')]; me=T.data; M=T.matrix_world
uvl=me.uv_layers['ortho'].data
def bv(o):
    m=o.matrix_world; return BVHTree.FromPolygons([m@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
TG=[bv(bpy.data.objects[n]) for n in ('WS243_stands_pitch_holdunder_target','WS245_E_bank_grade_target_UNVERIFIED')]
STN=[bv(bpy.data.objects[n]) for n in ('fse_stand_under_pad','fr_stand_under_pad','fs_turf','fse_front_walkway','fr_front_walkway')]
MG=float(os.environ.get('F246MG','2'))
OFS=[(0,0)]+[(MG*a,MG*b) for a,b in ((1,0),(-1,0),(0,1),(0,-1))+(((.7,.7),(-.7,.7),(.7,-.7),(-.7,-.7)) if 'F246MG' in os.environ else ())]  # ws246a ran with the 4-neighbour test
def over(x,y,L):
    for t in L:
        for dx,dy in OFS:
            if t.ray_cast(Vector((x+dx,y+dy,400)),Vector((0,0,-1)),600)[0] is not None: return True
    return False
def over2(x,y,L):
    return any(t.ray_cast(Vector((x+dx,y+dy,400)),Vector((0,0,-1)),600)[0] is not None for t in L for dx,dy in ((0,0),(2,0),(-2,0),(0,2),(0,-2)))
_ims=[n.image for m in me.materials if m and m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and any(k in (n.image.name+n.image.filepath).lower() for k in ('ortho','naip'))]
img=_ims[0] if _ims else next(i for i in bpy.data.images if i.name.startswith('ortho2020'))
print(os.environ.get('F246TAG','F246A')+' image',img.name,img.size[:],flush=True)
w,h=img.size; px=np.empty(w*h*4,np.float32); img.pixels.foreach_get(px); px=px.reshape(h,w,4)
def col(u,v): i=min(h-1,max(0,int(v*h))); j=min(w-1,max(0,int(u*w))); return px[i,j,:3]
def green(c): return c[1]>=c[0]*1.01 and c[1]>c[2]*1.04 and c.sum()<1.5
# local affine xy->uv from loops in the box (terrain ortho UV is planar)
BX=tuple(float(v) for v in os.environ.get('F246BOX','-250,-195,90,180').split(','))
vin=[v.index for v in me.vertices if BX[0]<(M@v.co).x<BX[1] and BX[2]<(M@v.co).y<BX[3]]; vs=set(vin)
li=[l.index for l in me.loops if l.vertex_index in vs]
P=np.array([tuple(M@me.vertices[me.loops[i].vertex_index].co)[:2] for i in li]); U=np.array([tuple(uvl[i].uv) for i in li])
X=np.c_[P,np.ones(len(P))]; A=np.linalg.lstsq(X,U,rcond=None)[0]; err=float(np.abs(X@A-U).max())
print(os.environ.get('F246TAG','F246A')+' affine loops',len(li),'max texel err',round(err*w,2),flush=True)
def uv(x,y): return np.array([x,y,1.0])@A
cand=[vi for vi in vin if over((M@me.vertices[vi].co).x,(M@me.vertices[vi].co).y,TG) and not over((M@me.vertices[vi].co).x,(M@me.vertices[vi].co).y,STN[:0])]
pale=0; fixed=0; fb=0; newuv={}; cs=[]; cg=[]
for vi in cand:
    p=M@me.vertices[vi].co; c=col(*uv(p.x,p.y)); cs.append(c)
    if green(c): continue
    pale+=1; got=None
    for r in np.arange(1.0,20.01,0.5):
        for k in range(24):
            a=2*np.pi*k/24; x=p.x+r*np.cos(a); y=p.y+r*np.sin(a)
            u=uv(x,y)
            if green(col(*u)) and not over2(x,y,TG+STN): got=u; break
        if got is not None: break
    if got is None: fb+=1; continue
    newuv[vi]=got; fixed+=1; cg.append(col(*got))
cs=np.array(cs) if cs else np.zeros((1,3))
print(os.environ.get('F246TAG','F246A')+' bank verts',len(cand),'non-green texels',pale,'remapped',fixed,'no green found',fb,'mean texel before',cs.mean(0).round(3),'mean new',np.array(cg).mean(0).round(3) if cg else None,flush=True)
if os.environ.get('DRY')!='1':
    n=0
    for lp in me.loops:
        if lp.vertex_index in newuv: uvl[lp.index].uv=tuple(newuv[lp.vertex_index]); n+=1
    me.update(); print(os.environ.get('F246TAG','F246A')+' loops set',n,flush=True)
