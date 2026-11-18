# ws143 (#50 part 1): Freeman NE entrance forecourt = the "N island" of Lot 9. Evidence (scripts/ws143/EVIDENCE_forecourt.md):
# 2023 LiDAR class-2 intensity 11-13k (concrete) inside, 7-8k on the outer ~2 m band, 2-3k asphalt outside; surface crowned 9.55 m
# local (+0.4-0.5 m over the lot) falling to the curb; outer step ~0.10 m. 2020 ortho: pale curved concrete edge, interior under a tree crown
# (LiDAR class-1 returns 2-4 m over x -78..-73). Built as ONE concrete surface draped on the smoothed 2023 DTM + curb ring on the lot side.
# Joint pattern, curb section and tree species UNVERIFIED. Runs after main142b (needs lz(), curbmesh(), col, cm from it).
import bpy, bmesh, math, numpy as np
from mathutils import Vector
OUTL=[(-79.2,-178.45),(-75.0,-178.45),(-72.0,-178.55),(-70.6,-178.55),(-69.1,-178.3),(-67.6,-177.6),(-66.8,-176.4),(-66.8,-174.9),
      (-67.5,-173.4),(-68.3,-172.2),(-69.0,-171.2),(-69.7,-170.35),(-70.5,-169.6),(-71.3,-169.0),(-72.6,-168.4),(-74.2,-167.8),(-76.5,-167.2),(-79.2,-166.7)]
def chaikin(P,n=2):
    for _ in range(n):
        Q=[P[0]]
        for a,b in zip(P[:-1],P[1:]):
            a=np.array(a);b=np.array(b); Q+= [tuple(a*0.75+b*0.25),tuple(a*0.25+b*0.75)]
        Q.append(P[-1]); P=Q
    return P
CURVE=chaikin(OUTL[1:-1],3); CURVE=[OUTL[0]]+[tuple(map(float,p)) for p in CURVE]+[OUTL[-1]]
poly=CURVE+[(-79.2,-170.6)]
def inpoly(x,y,P=poly):
    c=False; n=len(P)
    for i in range(n):
        x1,y1=P[i]; x2,y2=P[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
for o in [o for o in OB if o.name.startswith('WS143_')]: OB.remove(o)
con=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
wk=[o for o in OB if o.name.startswith('WS136a_Skyline')]
if wk and wk[0].data.materials: con=wk[0].data.materials[0]
bm=bmesh.new()
vs=[bm.verts.new((p[0],p[1],0)) for p in poly]
bm.faces.new(vs)
for x in np.arange(-79.0,-66.8,0.5):
    g=bm.verts[:]+bm.edges[:]+bm.faces[:]
    bmesh.ops.bisect_plane(bm,geom=g,plane_co=(x,0,0),plane_no=(1,0,0))
for y in np.arange(-178.0,-166.8,0.5):
    g=bm.verts[:]+bm.edges[:]+bm.faces[:]
    bmesh.ops.bisect_plane(bm,geom=g,plane_co=(0,y,0),plane_no=(0,1,0))
bmesh.ops.triangulate(bm,faces=bm.faces[:])
for v in bm.verts: v.co.z=lz(v.co.x,v.co.y)+0.04
nf=len(bm.faces)
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS143_Freeman_NE_forecourt_concrete_LiDAR2023int_ortho2020_UNVERIFIEDjoints'); bm.to_mesh(me); bm.free(); me.materials.append(con)
uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.5,p.y*0.5)
fc=OB.new(me.name,me); col.objects.link(fc); print('FORECOURT faces',nf)
# curb ring on the lot/aisle side (outer edge), top = forecourt edge, reveal 0.10 over the asphalt (LiDAR step)
ring=curbmesh('WS143_Freeman_NE_forecourt_curb_LiDAR2023step0p10_UNVERIFIEDsection',CURVE[1:-1],1,0.04,cm,w=0.15,step=0.4)
print('CURB verts',len(ring.data.vertices))
# retire drape faces under the forecourt, push ground below it
from mathutils.bvhtree import BVHTree
TF=BVHTree.FromPolygons([fc.matrix_world@v.co for v in fc.data.vertices],[p.vertices for p in fc.data.polygons])
def ztf(x,y):
    h=TF.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
for ro in [o for o in OB if o.type=='MESH' and (o.name in ('Roads_OSM','Footpaths_OSM') or o.name.startswith('UA_'))]:
    rb=bmesh.new(); rb.from_mesh(ro.data); rw=ro.matrix_world; k=[]
    for f in rb.faces:
        c=rw@f.calc_center_median()
        if -79.3<c.x<-66.5 and -178.7<c.y<-166.5:
            zt=ztf(c.x,c.y)
            if zt is not None and abs(c.z-zt)<1.5: k.append(f)
    if k: bmesh.ops.delete(rb,geom=k,context='FACES'); rb.to_mesh(ro.data); ro.data.update(); print('retired fc',ro.name,len(k))
    rb.free()
for g in [o for o in OB if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS114_terrain_fan_fill','WS110_ground_patch','WS133b_','WS134_ground'))]:
    me2=g.data; mw=np.array(g.matrix_world); n=len(me2.vertices)
    co=np.empty(n*3); me2.vertices.foreach_get('co',co); co=co.reshape(-1,3); Wc=co@mw[:3,:3].T+mw[:3,3]
    idx=np.nonzero((Wc[:,0]>-79.5)&(Wc[:,0]<-66.3)&(Wc[:,1]>-179)&(Wc[:,1]<-166.3))[0]; c=0
    for i in idx:
        zt=ztf(Wc[i,0],Wc[i,1])
        if zt is not None and Wc[i,2]>zt-0.10: Wc[i,2]=zt-0.10; c+=1
    if c:
        L=(Wc-mw[:3,3])@np.linalg.inv(mw[:3,:3]).T; me2.vertices.foreach_set('co',L.ravel()); me2.update(); print('pushed fc',g.name,c)
px=OB.get('WS113_paving_tops_proxy')
if px:
    pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted()
    for p in fc.data.polygons: pbm.faces.new([pbm.verts.new(pmi@(fc.matrix_world@fc.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('proxy +fc')
# probe: forecourt edge vs lot top at the shared S edge
for x in (-77,-74,-71):
    print('FCNB',x,ztf(x,-178.3),'lot',ztop(x,-178.75))
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws143/tree143.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws143/band143.py').read())
