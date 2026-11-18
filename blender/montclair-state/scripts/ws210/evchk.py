import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F=os.environ['PF']
N=['Terrain_LiDAR_DTM_1m','WS205_lotE_entry_apron_asphalt_fill_ortho2020_UNVERIFIED','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho','Footpaths_OSM','WS99_lotE_padS_bed_MULCH_ortho2020_LiDARshrubs_UNVERIFIED']
with bpy.data.libraries.load(F) as (a,b): b.objects=list(N)
sc=bpy.context.scene
for o in b.objects:
    sc.collection.objects.link(o)
    if o.name!='Terrain_LiDAR_DTM_1m':
        for m in o.modifiers: m.show_viewport=False
for l in open('/proc/self/status'):
    if l.startswith('VmRSS'): print('EV mem',l.strip(),flush=True)
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; te=T.evaluated_get(dg); me=te.to_mesh(); mw=T.matrix_world
TB=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
BB=BVHTree.FromPolygons([mw@v.co for v in T.data.vertices],[tuple(p.vertices) for p in T.data.polygons])
cov=[]
for n in N[1:]:
    o=bpy.data.objects[n]; w=o.matrix_world
    cov.append(BVHTree.FromPolygons([w@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]))
d=[]; poke=0; tot=0
for x in np.arange(-216,-203,0.25):
    for y in np.arange(-114,-94,0.25):
        o=Vector((x,y,150)); dn=Vector((0,0,-1))
        he=TB.ray_cast(o,dn,60); hb=BB.ray_cast(o,dn,60)
        if he[0] is None or hb[0] is None: continue
        tot+=1; d.append(he[0].z-hb[0].z)
        for c in cov:
            h=c.ray_cast(o,dn,60)
            if h[0] is not None and he[0].z>h[0].z+0.005 and he[0].z-h[0].z<0.6: poke+=1; break
d=np.array(d); print('EV n',tot,'eval-base dz: mean %.3f absmax %.3f  frac>2cm %.3f'%(d.mean(),np.abs(d).max(),(np.abs(d)>0.02).mean()),'eval terrain over cover cells',poke,flush=True)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('EV mem',l.strip(),flush=True)
