# ws253 read-only probe: first hit westward from the walk on Feliciano's walls/base/arcade at several y, z
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
C=[o for o in bpy.data.objects if o.type=='MESH' and ('Feliciano' in o.name) and not o.library]
B=[]
for o in C:
    try: B.append((o,BVHTree.FromObject(o,dg)))
    except Exception: pass
for y in (164.5,165.5,166.5,167.5,168.5,169.5,170.5,171.5,172.5,173.5,174.5,176,178,180,182):
    for z in (135.0,136.5,138.0):
        best=None
        for o,b in B:
            Mi=o.matrix_world.inverted(); h=b.ray_cast(Mi@Vector((-188,y,z)),(Mi.to_3x3()@Vector((-1,0,0))).normalized(),30)
            if h[0]:
                w=o.matrix_world@h[0]
                if best is None or w.x>best[0]: best=(w.x,o.name)
        print('W253 y',y,'z',z,'hit x %.2f %s'%best if best else 'none',flush=True)
os._exit(0)
