# ws165c: UNIFY #69 redo — ws165a's bisected mulch left holes/lawn showing through (closeup 1436). Rebuild the mulch as a clean
# 0.15 m grid inside the curb's inner line: flat at walk+0.10 (ws164 level) and easing down to walk+0.02 over the front 0.45 m, ending at
# the walk back edge with a 12 cm vertical face (and on the E side against the spur). Ground verts inside the bed footprint -> walk-0.10.
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws164/fix164a.py').read().split('def ramp')[0].split('OB=bpy.data.objects',1)[1])
SL=0.236; dv=np.array([-1.0,SL]); dv/=np.linalg.norm(dv); nv=np.array([SL,1.0]); nv/=np.linalg.norm(nv); A0=np.array([-268.8,-262.9])
def npt(x): t=(A0[0]-x)/(-dv[0]); return A0+dv*t
def wb(x): return (npt(x)+nv*(0.18+3.2))[1]
def fdist(x,y): return float(np.dot(np.array([x,y])-(npt(x)+nv*(0.18+3.2)),nv))
def bvh(objs):
    V=[];F=[]
    for o in objs:
        b=len(V); V+=[o.matrix_world@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
def hz(T,x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
walk=OB['WS163_NormalAve_W_N_sidewalk_3p2m_LiDAR2023_int_UNVERIFIED']; TW=bvh([walk])
def wz(x): return hz(TW,min(max(x,-305.3),-300.2),wb(min(max(x,-305.3),-300.2))-0.15)
XW,XE,YN,RC,CW=-305.45,-300.0,-248.8,1.0,0.15
xi0=XW+CW; yi1=YN-CW; cx,cy=XW+RC,YN-RC; ri=RC-CW
def inside(x,y):
    if x<xi0 or x>XE or y>yi1 or fdist(x,y)<0: return False
    if x<cx and y>cy and math.hypot(x-cx,y-cy)>ri: return False
    return True
old=[o for o in OB if o.name.startswith(('WS165_aisle_mouth_mulch','WS164_aisle_mouth_mulch'))]
mm=old[0].active_material if old else None
col=old[0].users_collection[0] if old else bpy.context.scene.collection
for o in old: OB.remove(o)
S=0.15; xs=np.linspace(xi0,XE,int(round((XE-xi0)/S))+1); ys=np.arange(wb(XE)-0.6,yi1+1e-6,S)
bm=bmesh.new(); V={}
def zf(x,y):
    w=wz(x); d=max(fdist(x,y),0); t=min(d/0.45,1); t=t*t*(3-2*t); base=max(w+0.10,dz(x,y)+0.03); return w+0.02+(base-(w+0.02))*t
def gv(i,j):
    if (i,j) in V: return V[(i,j)]
    x=float(xs[i]); y=float(ys[j])
    if fdist(x,y)<0: y=y+(-fdist(x,y))/nv[1]   # snap onto the walk back edge
    if x<cx and y>cy and math.hypot(x-cx,y-cy)>ri:
        a=math.atan2(y-cy,x-cx); x=cx+ri*math.cos(a); y=cy+ri*math.sin(a)
    v=bm.verts.new((x,y,zf(x,y))); V[(i,j)]=v; return v
def cin(i,j):
    x=float(xs[i]); y=float(ys[j]); return inside(min(max(x,xi0),XE),y) or (fdist(x,y)<0 and fdist(x,y)>-S*1.2) or (x<cx and y>cy and math.hypot(x-cx,y-cy)<ri+S*1.2 and y<=yi1)
nf=0
for i in range(len(xs)-1):
    for j in range(len(ys)-1):
        cs=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if not all(cin(*c) for c in cs): continue
        mx=(xs[i]+xs[i+1])/2; my=(ys[j]+ys[j+1])/2
        if fdist(mx,my)<-S*0.5 or my>yi1: continue
        vs=[gv(*c) for c in cs]
        if len(set(vs))<3: continue
        try: bm.faces.new(list(dict.fromkeys(vs))); nf+=1
        except ValueError: pass
bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=0.01)
# front + E vertical faces
fe=[e for e in bm.edges if e.is_boundary and (all(abs(fdist(*v.co.xy))<0.03 for v in e.verts) or all(abs(v.co.x-XE)<0.03 for v in e.verts))]
for e in fe:
    a,b=e.verts; dep=0.12 if all(abs(fdist(*v.co.xy))<0.03 for v in e.verts) else 0.40   # E side: deep enough to meet the spur/ground
    a2=bm.verts.new(a.co-Vector((0,0,dep))); b2=bm.verts.new(b.co-Vector((0,0,dep)))
    try: bm.faces.new((a,b,b2,a2))
    except ValueError: pass
for f in bm.faces:
    f.normal_update()
    if abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS165c_mulch'); bm.to_mesh(me); bm.free()
if mm: me.materials.append(mm)
uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.5,p.y*0.5)
mu=OB.new('WS165_aisle_mouth_mulch_bed_graded_to_walk_UNIFY69',me); col.objects.link(mu)
print('MULCHC faces',len(me.polygons),'front/E faces',len(fe),flush=True)
pa=OB['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']; gp=OB['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']; pc=0
for g in (pa,gp):
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if inside(p.x,p.y) or (xi0-0.05<p.x<XE+0.05 and -0.05<fdist(p.x,p.y)<0.6):
            w=wz(p.x); 
            zt=min(w-0.10,zf(p.x,p.y)-0.08) if inside(p.x,p.y) else w-0.10
            if p.z>zt: p.z=zt; v.co=mi@p; pc+=1
    g.data.update()
print('GROUNDC pushed',pc,flush=True)
t=OB.get('WS163_skirt_target_hidden')
if t:
    tb=bmesh.new(); tb.from_mesh(t.data); L=tb.verts.layers.float.get('wv_in')
    for p in mu.data.polygons:
        if p.normal.z<0.5: continue
        vs_=[tb.verts.new(mu.matrix_world@mu.data.vertices[i].co) for i in p.vertices]
        if L:
            for v in vs_: v[L]=0.45
        try: tb.faces.new(vs_)
        except ValueError: pass
    tb.to_mesh(t.data); tb.free(); t.data.update(); print('skirt target +mulchC',flush=True)
