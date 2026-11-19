# ws234 read-only: poke-through check of the EVALUATED Context skirt over the M3a extension (5 m grid over the extension)
import bpy, os, mathutils, collections
from mathutils.bvhtree import BVHTree
F=os.environ['FILE']; EXT=os.environ['EXT']
with bpy.data.libraries.load(F) as (a,b): b.objects=[EXT,'Context_skirt_3DEP_ortho_4km']
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
def bv(o):
    m=bpy.data.meshes.new_from_object(o.evaluated_get(dg)); m.transform(o.matrix_world)
    return BVHTree.FromPolygons([v.co[:] for v in m.vertices],[p.vertices[:] for p in m.polygons]),m
E_,em=bv(bpy.data.objects[EXT]); S_,sm=bv(bpy.data.objects['Context_skirt_3DEP_ortho_4km'])
xs=[v.co.x for v in em.vertices]; ys=[v.co.y for v in em.vertices]
n=0; bad=[]; D=mathutils.Vector((0,0,-1))
x=min(xs)
while x<max(xs):
    y=min(ys)
    while y<max(ys):
        h=E_.ray_cast(mathutils.Vector((x,y,400)),D)
        if h[0]:
            n+=1; s=S_.ray_cast(mathutils.Vector((x,y,400)),D)
            if s[0] and s[0].z>h[0].z+0.05: bad.append((round(x),round(y),round(s[0].z-h[0].z,2)))
        y+=5
    x+=5
print('P234F grid',n,'skirt above ext',len(bad),'max',max([b[2] for b in bad]) if bad else 0,flush=True)
H=collections.Counter((b[0]//50*50,b[1]//50*50) for b in bad)
print('P234F cells',H.most_common(20),flush=True)
print('P234F worst',sorted(bad,key=lambda b:-b[2])[:15],flush=True)
