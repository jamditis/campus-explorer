# om: classify the Footpaths_OSM float east/north of Schmitt (read-only). Per 8 m grid cell of walk faces within 95 m of the
# entrance: median float of walk face centres over the LiDAR DTM, DTM relief inside the cell, float spread, walk slope vs DTM slope.
import bpy,bmesh,statistics as st
from mathutils import Vector
from mathutils.bvhtree import BVHTree
C=Vector((10.6,141.1)); G=8.0
fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get()
bt=bmesh.new(); bt.from_mesh(ter.evaluated_get(dg).to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=tree.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
bm=bmesh.new(); bm.from_mesh(fp.data); bm.transform(fp.matrix_world)
cells={}
for f in bm.faces:
    c=f.calc_center_median()
    if (c.xy-C).length>95 or f.normal.z<0.5: continue
    z=tz(c.x,c.y)
    if z is None: continue
    k=(int((c.x)//G),int((c.y)//G)); cells.setdefault(k,[]).append((c.x,c.y,c.z,z,f.calc_area()))
out=[]
for k,L in cells.items():
    A=sum(l[4] for l in L)
    if A<4: continue
    fl=[l[2]-l[3] for l in L]; med=st.median(fl)
    tzs=[l[3] for l in L]; wz=[l[2] for l in L]
    rel=max(tzs)-min(tzs); wrel=max(wz)-min(wz); spread=max(fl)-min(fl)
    cx=sum(l[0] for l in L)/len(L); cy=sum(l[1] for l in L)/len(L)
    if med<0.3: cls='OK (on grade)'
    elif spread>1.5 and rel>1.5: cls='STEP/STAIR? (DTM relief + mixed float: walk crosses a slope/terrace edge)'
    elif med>1.2 and rel<1.2: cls='DRAPE ERROR likely (flat DTM, walk uniformly above it)'
    elif med>1.2: cls='DRAPE ERROR probable (walk above DTM on a slope, smoothed OSM grade)'
    else: cls='MINOR float (0.3-1.2 m) -> bank/curb treatment'
    out.append((med,cx,cy,A,rel,wrel,spread,cls))
out.sort(key=lambda o:-o[0])
with open('data/om/osm_walk_float_classes.txt','w') as fh:
    fh.write('# om float classification of Footpaths_OSM within 95 m of the Schmitt entrance (10.6,141.1); 8 m cells; float = walk face z - LiDAR DTM z\n# med_float  centre(x,y)  walk_area_m2  DTM_relief  walk_relief  float_spread  class\n')
    for o in out: fh.write('%5.2f  (%6.1f,%6.1f)  %6.1f  %4.2f  %4.2f  %4.2f  %s\n'%o)
from collections import Counter
print('CLASSES',Counter(o[7].split(' (')[0] for o in out))
print('TOP',out[:6])
