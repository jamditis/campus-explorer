# ws127: College Ave E curbside planting strip (curb back -> WS115 walk W edge, y -233.9..-203.25) per 2020 ortho dark strip;
# + UNIFY #19: lawn panel E of the WS115 walk off the ortho drape (COLE_lawn_post2020_bs, seams on hard edges).
import bpy, bmesh, random, math, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
random.seed(1271)
SAVE=os.environ.get('SAVE','0')=='1'
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
cb=O('WS102_CollegeAve_S_curb_E'); wk=O('WS115_E_walk_N')
cv=[cb.matrix_world@v.co for v in cb.data.vertices]; wv=[wk.matrix_world@v.co for v in wk.data.vertices]
def fit(pts,deg):
    import numpy as np
    a=np.array(pts); return np.polyfit(a[:,0],a[:,1],deg)
def pv(c,y):
    r=0
    for k in c: r=r*y+k
    return float(r)
cx=[];cz=[];wx=[];wz=[]
for yy in [ -233+i*0.5 for i in range(61)]:
    s=[v for v in cv if abs(v.y-yy)<0.3]
    if s:
        top=max(v.z for v in s); b=max((v for v in s if v.z>top-0.05),key=lambda v:v.x); cx.append((b.y,b.x)); cz.append((b.y,b.z))
    s=[v for v in wv if abs(v.y-yy)<0.3]
    if s and yy<-202.8 and yy>-232.6:
        b=min(s,key=lambda v:v.x); wx.append((b.y,b.x)); wz.append((b.y,b.z))
CX=fit(cx,1);CZ=fit(cz,2);WX=fit(wx,1);WZ=fit(wz,2)
print('M127 fits',len(cx),len(wx),'w@-220',pv(CX,-220),pv(WX,-220))
def edges(y): return pv(CX,y)+0.02, pv(WX,y)-0.02
def zat(y,u): return (1-u)*(pv(CZ,y)-0.04)+u*(pv(WZ,y)-0.05)
YN=-203.25; YS=-232.6
rows=[]
y=YN
while y>YS-1e-6: rows.append((y,1.0)); y-=0.5
if rows[-1][0]>YS+1e-6: rows.append((YS,1.0))
xa,xb=edges(YS); R=(xb-xa)/2
for k in range(1,7):
    a=k/7*math.pi/2; rows.append((YS-R*math.sin(a),math.cos(a)))
rows.append((YS-R+0.001,0.02))
NU=6
bm=bmesh.new(); grid=[]
for (y,f) in rows:
    xa,xb=edges(y); xm=(xa+xb)/2; hw=(xb-xa)/2*f
    r=[]
    for i in range(NU+1):
        u=i/NU; x=xm-hw+2*hw*u; uu=(x-xa)/max(xb-xa,1e-6)
        zz=zat(y,uu)
        if f<0.999 and (i in (0,NU) or f<0.05): zz-=0.08
        elif f<0.999 and (i in (1,NU-1)): zz-=0.03
        r.append(bm.verts.new((x,y,zz)))
    grid.append(r)
top=[]
for j in range(len(grid)-1):
    for i in range(NU):
        top.append(bm.faces.new((grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i])))
bm.normal_update()
for f in top:
    if f.normal.z<0: f.normal_flip()
bnd=[e for e in bm.edges if e.is_boundary]
for e in list(bnd):
    a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.15))); b2=bm.verts.new(b.co-Vector((0,0,0.15)))
    sf=bm.faces.new((a,b,b2,a2)); sf.material_index=1
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0005)
bm.normal_update()
me=bpy.data.meshes.new('WS127_strip'); bm.to_mesh(me); bm.free()
mm=O('WS105_Chapin_E_bank_planting_bed_MULCH').active_material; me.materials.append(mm); me.materials.append(bpy.data.materials['COLE_lawn_post2020_bs'])
col=bpy.data.collections.get('WS127_CollegeAve_E_curb_strip') or bpy.data.collections.new('WS127_CollegeAve_E_curb_strip')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS127_')]: bpy.data.objects.remove(o)
bed=bpy.data.objects.new('WS127_CollegeAve_E_curbside_bed_mulch_ortho2020_UNVERIFIED',me); col.objects.link(bed)
# strip 2D polygon for ground lowering
poly=[(edges(y)[0],y) for y,_ in rows]+[(edges(y)[1],y) for y,_ in reversed(rows)]
def inside(x,y):
    c=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: c=not c
    return c
btree=BVHTree.FromPolygons([v.co for v in me.vertices],[p.vertices for p in me.polygons if p.normal.z>0.5])
nl=0
for gname in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'):
    for g in [o for o in bpy.data.objects if o.name.startswith(gname) and o.type=='MESH']:
        mw=g.matrix_world; mi=mw.inverted()
        for v in g.data.vertices:
            p=mw@v.co
            if -241<p.x<-222 and -236<p.y<-202:
                # lower anything within the bed footprint (+0.25 m margin under curb/walk)
                for dx,dy in ((0,0),(0.25,0),(-0.25,0)):
                    if inside(p.x+dx,p.y+dy): break
                else: continue
                loc=btree.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)))[0]
                zb=loc.z if loc is not None else zat(min(max(p.y,YS-R),YN),0.5)
                if p.z>zb-0.12:
                    p.z=zb-0.12; v.co=mi@p; nl+=1
print('M127 ground verts lowered',nl)
# cap: lawn just S of the bullnose graded up to the bed edge (no mulch skirt showing), 1.0 m falloff
cxm=(edges(YS)[0]+edges(YS)[1])/2; zc=zat(YS,0.5)-0.02; nr=0
for gname in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'):
    for g in [o for o in bpy.data.objects if o.name.startswith(gname) and o.type=='MESH']:
        mw=g.matrix_world; mi=mw.inverted()
        for v in g.data.vertices:
            p=mw@v.co
            if p.y<YS and not inside(p.x,p.y):
                d=(Vector((p.x,p.y))-Vector((cxm,YS))).length-R
                if d<1.0:
                    t=max(0.0,d)/1.0; zt=zc*(1-t)+p.z*t
                    if zt>p.z: p.z=zt; v.co=mi@p; nr+=1
print('M127 cap lawn verts raised',nr)
# proxy: add bed top faces so the WS113 edge-grade GN holds ground 8 cm under the bed
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws127'):
    px['ws127']=1
    pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for p in me.polygons:
        if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@me.vertices[i].co) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('M127 proxy faces',n0,'->',len(px.data.polygons))
# pachysandra carpet (same palette as the WS126 Chapin banks)
pm=bpy.data.materials['WS126_Pachysandra_leaf_glossy']
tops=[p for p in me.polygons if p.normal.z>0.5]
ec={}
for p in tops:
    for k in p.edge_keys: ec[k]=ec.get(k,0)+1
bse=[(me.vertices[a].co.xy,me.vertices[b].co.xy) for (a,b),c in ec.items() if c==1]
def dseg(q):
    m=9
    for a,b in bse:
        ab=b-a; t=max(0,min(1,(q-a).dot(ab)/max(ab.length_squared,1e-9))); m=min(m,(a+ab*t-q).length)
    return m
leafshape=[(0,0),(0.35,-0.42),(0.8,-0.5),(1.0,-0.2),(1.0,0.2),(0.8,0.5),(0.35,0.42)]
gm=bpy.data.meshes.new('WS127_pachysandra'); bm=bmesh.new(); cols=[]; nros=0
# a few gaps (maintenance/foot-worn patches seen as lighter tone in the ortho) none: keep continuous
y=YS-R
while y<YN:
    x=-240.5
    while x<-224.0:
        q=Vector((x+random.uniform(-0.07,0.07),y+random.uniform(-0.07,0.07)))
        loc,nor,idx,dist=btree.ray_cast(Vector((q.x,q.y,200)),Vector((0,0,-1)))
        if loc is not None and dseg(q)>0.28+random.uniform(-0.04,0.04):
            h=random.uniform(0.08,0.22); c=Vector((q.x,q.y,loc.z+h)); nros+=1
            L=random.uniform(0.055,0.105); W=L*0.42; rot0=random.uniform(0,6.28); nlv=random.choice((5,6,6,7))
            g=random.uniform(0.8,1.2); colr=(0.022*g,0.065*g+random.uniform(-0.01,0.012),0.018*g,1)
            for j in range(nlv):
                ang=rot0+j*math.tau/nlv+random.uniform(-0.25,0.25); tilt=math.radians(random.uniform(12,42))
                ca,sa=math.cos(ang),math.sin(ang); vv=[]
                for u,w in leafshape:
                    lx=u*L*math.cos(tilt); lz=-u*L*math.sin(tilt)+0.012*u*(1-u)*4; ly=w*W
                    vv.append(bm.verts.new((c.x+lx*ca-ly*sa,c.y+lx*sa+ly*ca,c.z+lz)))
                bm.faces.new(vv); cols.append(colr)
        x+=0.085
    y+=0.085
bm.to_mesh(gm); bm.free()
ca=gm.color_attributes.new('pcol','FLOAT_COLOR','CORNER')
for p,cc in zip(gm.polygons,cols):
    for l in p.loop_indices: ca.data[l].color=cc
gm.materials.append(pm)
go=bpy.data.objects.new('WS127_CollegeAve_E_curbside_pachysandra_carpet_UNVERIFIEDspecies',gm); col.objects.link(go)
print('M127 rosettes',nros,'faces',len(gm.polygons))
# UNIFY #19: lawn panel E of the walk -> non-ortho lawn material
lm=bpy.data.materials.get('COLE_lawn_post2020_bs'); nf=0
def walkE(y): return pv(WX,y)+2.35
for gname in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    for g in [o for o in bpy.data.objects if o.name.startswith(gname) and o.type=='MESH']:
        mats=[m.name if m else '' for m in g.data.materials]
        if lm.name not in mats: g.data.materials.append(lm); mats.append(lm.name)
        li=mats.index(lm.name); mw=g.matrix_world
        for p in g.data.polygons:
            c=mw@p.center
            if -233.9<c.y<-203.3 and walkE(c.y)-0.3<c.x<-209.0 and mats[p.material_index]=='Ground_ortho_grass':
                p.material_index=li; nf+=1
print('M127 #19 lawn faces retextured',nf)
if SAVE: bpy.ops.wm.save_mainfile(); print('M127 SAVED')
