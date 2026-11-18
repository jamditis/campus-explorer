# ws195 WOBBLE W6: WS77 lot median island (Red Hawk/Kasser lot) rebuilt on a designed outline (was a hand-traced 12-pt polygon
# that ws93 only RDP-straightened: N side kinks, S side kink at x -237, W-end jog/foot at (-254.4,-88.6); survey jitter 0.34 m).
# New outline: N side = least-squares straight line through the old N trace (x -250…-220); S side = straight line through the old
# SE and SW corners (-217.8,-94.78)…(-252.38,-86.98) (old S kink pushed out 0.47 m, never inside the old edge -> no lot hole);
# W end = true circular round nose tangent to both sides, tip at the old W extreme (curbed mulch medians on this campus have
# rounded concrete noses — Joe catwalk_03/04 2026-11-12; exact radius UNVERIFIED); E end kept exactly (it runs into the WS98
# raised walk pad / WS99 bed). Construction as ws77a: 0.15 m wide concrete curb ring, top 15 cm over the lot, open skirt 6 cm under;
# dark mulch (WS87 material) 4 cm below the curb top; draped on the lot sheets (continuous under the island — probe195b).
import bpy,bmesh,math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
NAME='WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020'
old=bpy.data.objects[NAME]; mats=list(old.data.materials); col=old.users_collection[0]
OLDP=[(-256.0,-81.2),(-253.4,-81.5),(-248.5,-81.9),(-236.97,-84.92),(-217.12,-88.62)]
# densify old N trace, fit x -250..-220
xs=np.linspace(-250,-220,61); ys=np.interp(xs,[p[0] for p in OLDP],[p[1] for p in OLDP])
aN,bN=np.polyfit(xs,ys,1); yN=lambda x:aN*x+bN
p1=np.array((-217.8,-94.78)); p2=np.array((-252.38,-86.98)); aS=(p2[1]-p1[1])/(p2[0]-p1[0]); bS=p1[1]-aS*p1[0]; yS=lambda x:aS*x+bS
print('F195 N y=%.4fx%+.3f S y=%.4fx%+.3f'%(aN,bN,aS,bS),flush=True)
# W cap: circle tangent to both lines, centre on the bisector, leftmost point at x=-256.0
def dl(a,b,x,y): return abs(a*x-y+b)/math.hypot(a,1)
best=None
for cx in np.linspace(-256,-248,8001):
    # bisector point: centre equidistant to both lines, between them
    lo,hi=yS(cx),yN(cx)
    for _ in range(40):
        cy=(lo+hi)/2
        if dl(aN,bN,cx,cy)>dl(aS,bS,cx,cy): lo=cy
        else: hi=cy
    r=dl(aN,bN,cx,cy)
    if best is None or abs(cx-r+256.0)<best[0]: best=(abs(cx-r+256.0),cx,cy,r)
_,cx,cy,r=best; c=np.array((cx,cy)); print('F195 W cap c',c,'r %.3f'%r,flush=True)
def foot(a,b):  # tangent point = perpendicular foot of c on the line
    n=np.array((-a,1.0))/math.hypot(a,1); d=(cy-(a*cx+b))/math.hypot(a,1); return c-n*d
tN=foot(aN,bN); tS=foot(aS,bS)
def seg(a,b,st):
    a=np.array(a,float); b=np.array(b,float); n=max(1,int(round(np.linalg.norm(b-a)/st))); return [a+(b-a)*k/n for k in range(n)]
a0=math.atan2(tN[1]-cy,tN[0]-cx); a1=math.atan2(tS[1]-cy,tS[0]-cx)
if a1<a0: a1+=2*math.pi
na=max(8,int(r*(a1-a0)/0.15)); arc=[c+r*np.array((math.cos(a0+(a1-a0)*k/na),math.sin(a0+(a1-a0)*k/na))) for k in range(na)]
eN=np.array((-217.12,yN(-217.12)))
# CCW order: S side W->E, E end (old), N side E->W, W cap N->S
POLY=seg(tS,p1,0.5)+seg(p1,(-214.03,-94.1),0.5)+seg((-214.03,-94.1),(-213.35,-90.54),0.5)+seg((-213.35,-90.54),eN,0.5)+seg(eN,tN,0.5)+arc
pts=[Vector((float(p[0]),float(p[1]))) for p in POLY]
# drop near-duplicates
pp=[pts[0]]
for p in pts[1:]:
    if (p-pp[-1]).length>0.05: pp.append(p)
if (pp[0]-pp[-1]).length<0.05: pp.pop()
pts=pp
lots=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and any(o.name.startswith(p) for p in ('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch'))]
TR=[]
for o in lots:
    mw=o.matrix_world; TR.append(BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]))
def zat(x,y):
    b=None
    for T in TR:
        h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0] and (b is None or h[0].z>b): b=h[0].z
    return b
# old island foot z as fallback (lot missing): nearest old boundary vert z+0.06
OW=[old.matrix_world@v.co for v in old.data.vertices]
def zfb(x,y):
    v=min(OW,key=lambda q:(q.x-x)**2+(q.y-y)**2); return v.z
raw=[zat(p.x,p.y) for p in pts]; miss=sum(z is None for z in raw)
zs=[z if z is not None else zfb(p.x,p.y)+0.06 for p,z in zip(pts,raw)]
# smooth curb line z along the loop (kills lot-sheet facet jitter in the curb top = z-wobble), 5-pt window, wrap
Z=np.array(zs); Zs=np.array([np.mean(np.take(Z,range(i-2,i+3),mode='wrap')) for i in range(len(Z))]); Zs=np.clip(Zs,Z-0.03,Z+0.03)
print('F195 outline pts',len(pts),'lot miss',miss,'z',Z.min(),Z.max(),'smooth max d %.3f'%np.abs(Zs-Z).max(),flush=True)
CURB=0.15
bpy.data.objects.remove(old)
bm=bmesh.new()
top=[bm.verts.new((p.x,p.y,z+CURB)) for p,z in zip(pts,Zs)]
bot=[bm.verts.new((p.x,p.y,min(z,zr)-0.08)) for p,z,zr in zip(pts,Zs,Z)]
f=bm.faces.new(top); f.material_index=1
for i in range(len(pts)):
    j=(i+1)%len(pts); s=bm.faces.new((bot[i],bot[j],top[j],top[i])); s.material_index=0
bm.normal_update()
if f.normal.z<0: bmesh.ops.reverse_faces(bm,faces=[f])
rr=bmesh.ops.inset_region(bm,faces=[f],thickness=0.15,depth=0)
for ff in rr['faces']: ff.material_index=0
f.material_index=1
inner=bmesh.ops.triangulate(bm,faces=[f])['faces']
for it in range(8):
    E=list({e for ff in inner if ff.is_valid for e in ff.edges if e.calc_length()>1.2})
    if not E: break
    bmesh.ops.subdivide_edges(bm,edges=E,cuts=1,use_grid_fill=False)
    inner=[ff for ff in bm.faces if ff.material_index==1]
    bmesh.ops.triangulate(bm,faces=inner); inner=[ff for ff in bm.faces if ff.material_index==1]
iv={v for ff in inner for v in ff.verts}
bnd={v for v in iv if any(l.face.material_index==0 for l in v.link_loops)}
for v in iv:
    if v in bnd: v.co.z-=0.04
    else:
        z=zat(v.co.x,v.co.y)
        if z is not None: v.co.z=z+CURB-0.04
bm.normal_update()
for ff in bm.faces:
    if ff.material_index==0 and ff.normal.z<-0.9: ff.normal_flip()
uv=bm.loops.layers.uv.new('UVMap')
for ff in bm.faces:
    for l in ff.loops:
        co=l.vert.co; l[uv].uv=(co.x/4.0,co.y/4.0) if ff.normal.z>0.5 else ((co.x+co.y)/2.0,co.z/0.5)
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
for ff in me.polygons: ff.use_smooth=False
for m in mats: me.materials.append(m)
ob=bpy.data.objects.new(NAME,me); col.objects.link(ob)
print('F195 built verts',len(me.vertices),'faces',len(me.polygons),'inner',len(inner),'mats',[m.name for m in mats],flush=True)
def pip(P,x,y):
    P=np.array([(p.x,p.y) for p in P]); xs_,ys_=P[:,0],P[:,1]; xj,yj=np.roll(xs_,1),np.roll(ys_,1)
    cc=((ys_>y)!=(yj>y))&(x<(xj-xs_)*(y-ys_)/(yj-ys_+1e-12)+xs_); return cc.sum()%2==1
for tn in ('T_LondonPlane_L1_0245','T_SugarMaple_L1_0244','T_RedMaple_L1_0239'):
    t_=bpy.data.objects.get(tn)
    if t_:
        p=t_.matrix_world.translation; d=min(math.hypot(p.x-q.x,p.y-q.y) for q in pts)
        print('F195 tree',tn,'inside',pip(pts,p.x,p.y),'dist to edge %.2f'%d,flush=True)
