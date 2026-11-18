import bpy, bmesh
from mathutils import Vector
o=[x for x in bpy.data.objects if x.name.startswith('MI Annex west wall planted bed')][0]
print('BED',o.name,o.modifiers[:] and [m.type for m in o.modifiers], o.dimensions[:], o.location[:])
me=o.data; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(me)
bd=[v for v in bm.verts if v.is_boundary]
o.hide_set(True); o.hide_render=True
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
import statistics
diffs=[]
for v in bd[::4]:
    w=mw@v.co
    h,l,n,i,ob,_=sc.ray_cast(dg,Vector((w.x,w.y,w.z+3)),Vector((0,0,-1)))
    if h: diffs.append((round(w.z-l.z,3),ob.name[:40]))
print('BED boundary n',len(bd),'samples',len(diffs))
print('BED z-ground stats',statistics.median([d[0] for d in diffs]),min(d[0] for d in diffs),max(d[0] for d in diffs))
import collections; print(collections.Counter(d[1] for d in diffs).most_common(5))
zs=[(mw@v.co).z for v in bm.verts]; print('BED z range',min(zs),max(zs))
m=me.materials[0]; print('BEDMAT',[n.type for n in m.node_tree.nodes])
