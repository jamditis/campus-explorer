import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P) as (df,dt):
    dt.objects=[n for n in df.objects if not n.startswith(('T_','Tree','ShrubLeaf','Leaf','Grass','WS122','WS108','WS107')) and 'CAM' not in n]
T=[]
for o in dt.objects:
    if o is None or o.type!='MESH' or len(o.data.vertices)>800000: continue
    mw=o.matrix_world; vs=[mw@v.co for v in o.data.vertices]
    if not any(-200<v.x<-195 and -232<v.y<-226 for v in vs): continue
    T.append((o.name,BVHTree.FromPolygons(vs,[p.vertices for p in o.data.polygons])))
for x in (-198.5,-197.8,-197.2,-196.6):
  for y in (-228.0,-228.8,-229.5,-230.2,-231.0):
    hs=[]
    for n,t in T:
        h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0] is not None: hs.append((round(h[0].z,3),n[:34]))
    print('P',x,y,sorted(hs,reverse=True)[:4])
