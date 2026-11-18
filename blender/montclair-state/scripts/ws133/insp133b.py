import bpy, math, re
from mathutils import Vector
pat=re.compile(r'footpath|road|paving|plaza|walk|ground|lawn|freeman|russ|balance|dining|osm|^ws13|bldg|building|sidewalk|patch|fill|curb|pad',re.I)
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (df,dt):
    dt.objects=[n for n in df.objects if pat.search(n) and n not in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')]
X0,X1,Y0,Y1=-132,-108,-272,-205
for o in dt.objects:
    if o is None or o.type!='MESH': continue
    mw=o.matrix_world; me=o.data
    bb=[mw@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if any(math.isnan(q) for q in xs+ys) or max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    zc=[]; xy=[]
    for p in me.polygons:
        c=mw@p.center
        if X0<c.x<X1 and Y0<c.y<Y1: zc.append(c.z); xy.append((c.x,c.y))
    if not zc: continue
    print('OBJ %-66s hr=%d n=%d z%.2f..%.2f x%.1f..%.1f y%.1f..%.1f %s'%(o.name,o.hide_render,len(zc),min(zc),max(zc),min(a for a,b in xy),max(a for a,b in xy),min(b for a,b in xy),max(b for a,b in xy),[m.name for m in me.materials if m][:3]))
