import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dk=bpy.data.objects['NJ Transit Deck']; M=dk.matrix_world
DB=BVHTree.FromPolygons([M@v.co for v in dk.data.vertices],[p.vertices[:] for p in dk.data.polygons])
rows=[]
for y in range(930,1080,4):
    s=''
    for x in range(-140,-36,3):
        h=DB.ray_cast(Vector((x,y,100.0)),Vector((0,0,1)),30.0)
        if h[0] is None: s+='  .'; continue
        # top of lowest slab: continue up through thickness
        h2=DB.ray_cast(h[0]+Vector((0,0,0.01)),Vector((0,0,1)),2.0)
        z=h2[0].z if h2[0] is not None and h2[0].z-h[0].z<0.8 else h[0].z
        s+='%3d'%int(round((z-100)*10)) if z<112 else '  ^'
    rows.append('%d %s'%(y,s))
open('/workspace/nj-scenes/montclair-state/scripts/ws241/probe241c.out','w').write('P241C x from -140 step 3; value=(z-100)*10 of lowest slab top\n'+'\n'.join(rows)); print('P241C ok',flush=True)
os._exit(0)
