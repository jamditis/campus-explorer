"""ws30: lower floating Roads_OSM / Footpaths_OSM verts back onto terrain (+4/+5 cm) and the walk-joint overlays onto the walk below (+1 cm),
in BOX, only where the vert floats 0.12..0.9 m over terrain. Pavement truth = terrain here (the ws30 probe showed the old OSM ribbons
floating over the CCOM dock apron and the walk south of CCOM)."""
import bpy, bmesh, os, re, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=[float(v) for v in os.environ['DBOX'].split(',')]
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
bm=bmesh.new(); bm.from_mesh(ter.data); bm.transform(ter.matrix_world); T=BVHTree.FromBMesh(bm); bm.free()
def tz(x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
rep={}
EX=[float(v) for v in os.environ.get('EXBOX','-15,10,-55,-18').split(',')]
import collections; CL=collections.Counter()
for name,off in (('Footpaths_OSM',0.05),):
    o=bpy.data.objects[name]; mw=o.matrix_world; inv=mw.inverted(); c=0
    for v in o.data.vertices:
        p=mw@v.co
        if not(X0<p.x<X1 and Y0<p.y<Y1): continue
        if EX[0]<p.x<EX[1] and EX[2]<p.y<EX[3]: continue
        z=tz(p.x,p.y)
        if z is None: continue
        d=p.z-z
        if 0.12<d<0.9: v.co=inv@Vector((p.x,p.y,z+off)); c+=1; CL[(int(p.x//8)*8,int(p.y//8)*8)]+=1
    o.data.update(); rep[name]=c
dg.update()
fp=bpy.data.objects['Footpaths_OSM']; bm=bmesh.new(); bm.from_mesh(fp.data); bm.transform(fp.matrix_world); F=BVHTree.FromBMesh(bm); bm.free()
for o in sc.objects:
    if o.type!='MESH' or not re.search(r'(joints)',o.name,re.I) or o.data.users>1 or o.library: continue
    if o.modifiers: continue
    mw=o.matrix_world; inv=mw.inverted(); c=0
    for v in o.data.vertices:
        p=mw@v.co
        if not(X0<p.x<X1 and Y0<p.y<Y1): continue
        z=tz(p.x,p.y)
        if z is None or not(0.15<p.z-z<0.95): continue
        h=F.ray_cast(Vector((p.x,p.y,p.z+0.3)),Vector((0,0,-1)),2.0)
        nz=(h[0].z+0.01) if (h[0] and h[0].z<p.z-0.05) else z+0.06
        v.co=inv@Vector((p.x,p.y,nz)); c+=1
    if c: o.data.update(); rep[o.name]=c
print('CLUSTERS',sorted(CL.items()))
print('DRAPE',os.environ['DBOX'],rep)
