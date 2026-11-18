import bpy, bmesh, numpy as np, re, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
bm=bmesh.new(); bm.from_mesh(ter.data); bm.transform(ter.matrix_world); T=BVHTree.FromBMesh(bm); bm.free()
import os
X0,X1,Y0,Y1=[float(v) for v in os.environ["BOX"].split(",")]
for o in sc.objects:
    if o.type!='MESH' or o.hide_render or not o.visible_get() or o==ter: continue
    if not re.search(r'(footpath|road|walk|path|asphalt|paver|crosswalk|carriage|curb|slab|lot|drive)',o.name,re.I): continue
    mw=o.matrix_world; d=[]
    for v in o.data.vertices:
        p=mw@v.co
        if X0<p.x<X1 and Y0<p.y<Y1:
            h=T.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)))
            if h[0]: d.append((p.z-h[0].z,p.x,p.y))
    if not d: continue
    a=np.array(d); fl=a[a[:,0]>0.25]
    print('OBJ',o.name[:55],'n',len(a),'h p50 %.2f p95 %.2f max %.2f'%(np.percentile(a[:,0],50),np.percentile(a[:,0],95),a[:,0].max()),'float>25cm',len(fl), ('x %.0f..%.0f y %.0f..%.0f'%(fl[:,1].min(),fl[:,1].max(),fl[:,2].min(),fl[:,2].max())) if len(fl) else '')
o=bpy.data.objects['Footpaths_OSM']; mw=o.matrix_world; c=collections.Counter(); mx={}
for v in o.data.vertices:
    p=mw@v.co
    if X0<p.x<X1 and Y0<p.y<Y1:
        h=T.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)))
        if h[0] and p.z-h[0].z>0.25:
            k=(int(p.x//4)*4,int(p.y//4)*4); c[k]+=1; mx[k]=max(mx.get(k,0),round(p.z-h[0].z,2))
for k,n in sorted(c.items()): print('FP',k,n,mx[k])
# poke: terrain above pavement
pav=[o for o in sc.objects if o.type=='MESH' and not o.hide_render and o.visible_get() and o!=ter and re.search(r'(footpath|roads_osm|walk|paver|asphalt|crosswalk|carriage|curb|plaza_deck|sidewalk)',o.name,re.I) and not re.search(r'(joint|stain|decal|stripe|line|rail|crack)',o.name,re.I)]
dg=bpy.context.evaluated_depsgraph_get(); bm=bmesh.new()
for o in pav:
    ev=o.evaluated_get(dg); m=ev.to_mesh(); t=bmesh.new(); t.from_mesh(m); t.transform(o.matrix_world); tm=bpy.data.meshes.new('t'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm); ev.to_mesh_clear()
P=BVHTree.FromBMesh(bm); cc=collections.Counter(); mm={}
for x in np.arange(X0,X1,0.5):
    for y in np.arange(Y0,Y1,0.5):
        h=P.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if not h[0]: continue
        t=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if t[0] and t[0].z>h[0].z-0.01 and t[0].z<h[0].z+1.5:
            k=(int(x//4)*4,int(y//4)*4); cc[k]+=1; mm[k]=max(mm.get(k,0),round(t[0].z-h[0].z,2))
print('POKE total',sum(cc.values()))
for k,n in sorted(cc.items(),key=lambda k:-k[1])[:30]: print('PK',k,n,mm[k])
