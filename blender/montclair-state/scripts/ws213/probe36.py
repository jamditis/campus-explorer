import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
BB=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json'))
X0,X1,Y0,Y1=-262,-248,-64,-50
want=[n for n,v in BB.items() if v[0]=='MESH' and not v[1] and not (v[3]<X0 or v[2]>X1 or v[5]<Y0 or v[4]>Y1) and not n.startswith(('Context_skirt','BD_farfield'))]
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in want if n in a.objects]
T=[]
for o in b.objects:
    if o is None or o.type!='MESH' or len(o.data.polygons)==0 or o.hide_render: continue
    mods=[m.type for m in o.modifiers]
    m=o.matrix_world; T.append((o,BVHTree.FromPolygons([m@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]),mods))
print('OBJS',[(o.name,md) for o,t,md in T],flush=True)
for y in range(-62,-51,1):
  for x in range(-260,-249,1):
    hs=[]
    for o,t,md in T:
        h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
        if h[0] is not None: hs.append((round(h[0].z,2),o.name[:28],o.data.materials[o.data.polygons[h[2]].material_index].name[:14] if o.data.materials else None))
    hs.sort(reverse=True); print('P',x,y,hs[:4],flush=True)
