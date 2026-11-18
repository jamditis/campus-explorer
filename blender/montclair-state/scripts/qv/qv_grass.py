# qv (Nov 3 2026 ~12:45 AM ET, MAIN, day 7 Richardson N/W ground): grass clumps (cx_grass instancer, same as qs) on the N/W
# skirt lawn OUTSIDE the qs box (x 30-145, y 218-325): box x -15..150, y 240..345, complementary to the qs 6 m edge fade so the
# density is continuous, 8 m outer fade; not on OSM walks/roads/building footprints/objects. UNVERIFIED. REVERT=1 removes it.
import bpy, os, json, math, random
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; COLG='QV_Richardson_NW_lawn_grass_20261103qv'
def revert():
    c=bpy.data.collections.get(COLG)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith('QV_') and m.users==0]: bpy.data.meshes.remove(me)
    print('QVG reverted')
revert()
if REV:
    if os.environ.get('QVSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
QX0,QX1,QY0,QY1=30.,145.,218.,325.
X0,X1,Y0,Y1=-15.,150.,240.,345.
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
D=json.load(open('data/scene_data.json'))
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
blds=[f['pts'] for f in D['features'] if f.get('tags',{}).get('building') and f.get('closed',True)]
blds=[p for p in blds if max(q[0] for q in p)>X0-20 and min(q[0] for q in p)<X1+20 and max(q[1] for q in p)>Y0-20 and min(q[1] for q in p)<Y1+20]
blds.append(json.load(open('data/qp/rich_poly.json'))['outer'])
def inbld(x,y,m=0.3): return any(pip(x,y,p) for p in blds)
UNB=[]   # OSM footprints with NO MAIN mesh over them (Health Drop-In / Student Center = north blend, day 8; Reid Hall = outside boundary)
GN=['Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km','QM_terrain_band_underlay_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
# ---- grass
D_=float(os.environ.get('D','35')); rnd=random.Random(110303)
okw=('grass','lawn','ortho')
def sm(t): t=min(max(t,0),1); return t*t*(3-2*t)
roadsegs=[]
for f in D['features']:
    t=f.get('tags',{}).get('highway')
    if not t: continue
    hw=1.4 if t in('footway','path') else (2.9 if t=='service' else 4.5)
    for a,b in zip(f['pts'][:-1],f['pts'][1:]): roadsegs.append((a,b,hw))
roadsegs=[s for s in roadsegs if max(s[0][0],s[1][0])>X0-10 and min(s[0][0],s[1][0])<X1+10 and max(s[0][1],s[1][1])>Y0-10 and min(s[0][1],s[1][1])<Y1+10]
def nearroad(x,y):
    for (ax,ay),(bx,by),hw in roadsegs:
        dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2))
        if (x-ax-t*dx)**2+(y-ay-t*dy)**2<hw*hw: return True
    return False
blk=[]
for o in sc.objects:
    if o.type!='MESH' or o.name in GN or o.hide_render or not o.visible_get(): continue
    nl=o.name.lower()
    if any(k in nl for k in ('grass','tree','shrub','farfield','helper','probe','pc_','cx_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    bx0=min(v.x for v in bb); bx1=max(v.x for v in bb); by0=min(v.y for v in bb); by1=max(v.y for v in bb)
    if bx1<X0 or bx0>X1 or by1<Y0 or by0>Y1 or (bx1-bx0)*(by1-by0)>4e5: continue
    blk.append((o.evaluated_get(dg),o.matrix_world.inverted(),bx0,bx1,by0,by1))
print('QV blockers',len(blk))
def blocked(x,y,z):
    for b,iw,bx0,bx1,by0,by1 in blk:
        if x<bx0 or x>bx1 or y<by0 or y>by1: continue
        o0=iw@Vector((x,y,z+40)); o1=iw@Vector((x,y,z-0.08)); d=o1-o0
        if b.ray_cast(o0,d.normalized(),distance=d.length)[0]: return True
    return False
for p in blds[:-1]:
    cx=sum(q[0] for q in p)/len(p); cy=sum(q[1] for q in p)/len(p)
    if pip(cx,cy,p) and not blocked(cx,cy,135.0): UNB.append(p)
blds=[p for p in blds if not any(p is u for u in UNB)]
print('QV unbuilt footprints -> grass placeholder',len(UNB))
def inunb(x,y): return any(pip(x,y,p) for p in UNB)
pts=[]; st={'t':0,'b':0,'m':0,'r':0}; FADE=6.0
for _ in range(int(D_*(X1-X0)*(Y1-Y0))):
    x=X0+rnd.random()*(X1-X0); y=Y0+rnd.random()*(Y1-Y0)
    pq=sm(min(x-QX0,QX1-x,y-QY0,QY1-y)/FADE) if (QX0<x<QX1 and QY0<y<QY1) else 0.0
    if pq>0 and inunb(x,y): pq=0.0   # qs skipped these footprints -> fill at full density
    if rnd.random()>(1-pq)*sm(min(x-X0,X1-x,y-Y0,Y1-y)/8.0): continue
    st['t']+=1
    if inbld(x,y) or nearroad(x,y): st['r']+=1; continue
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best[0]: best=(z,e,r[2],r[3],mw)
    if best is None: st['b']+=1; continue
    z,e,n,fi,mw=best
    if (mw.to_3x3()@n).normalized().z<0.6: st['b']+=1; continue
    ms=e.material_slots
    if ms:
        mn=ms[e.data.polygons[fi].material_index].name.lower() if fi<len(e.data.polygons) else ''
        if not any(k in mn for k in okw): st['m']+=1; continue
    hit=False
    for b,iw,bx0,bx1,by0,by1 in blk:
        if x<bx0 or x>bx1 or y<by0 or y>by1: continue
        o0=iw@Vector((x,y,z+40)); o1=iw@Vector((x,y,z-0.08)); d=o1-o0
        if b.ray_cast(o0,d.normalized(),distance=d.length)[0]: hit=True; break
    if hit: st['b']+=1; continue
    pts.append((x,y,z-0.005))
cg=bpy.data.collections.new(COLG); sc.collection.children.link(cg)
me=bpy.data.meshes.new('QV_Richardson_NW_lawn_grass_points_UNVERIFIED'); me.from_pydata(pts,[],[])
ob=bpy.data.objects.new('QV_Richardson_NW_lawn_grass_points_UNVERIFIED',me); cg.objects.link(ob)
m=ob.modifiers.new('cx_grass','NODES'); m.node_group=bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
ob['UNVERIFIED_qv']='grass clumps round Richardson box x %g-%g y %g-%g D=%g'%(X0,X1,Y0,Y1,D_)
print('QV_GRASS',len(pts),st)
json.dump({'grass':len(pts)},open('data/qv/grass_added.json','w'))
if os.environ.get('QVSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
