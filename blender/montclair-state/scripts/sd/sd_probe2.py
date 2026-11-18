import bpy, collections
from mathutils import Vector
o=[x for x in bpy.data.objects if x.name.startswith('MI Annex RED HAWK COUNTRY 3D letters')][0]
me=o.data; mw=o.matrix_world
print('NAME',o.name, 'mods',[m.type for m in o.modifiers])
cnt=collections.Counter(); 
nb=collections.defaultdict(list)
for p in me.polygons:
    cnt[p.material_index]+=1
    c=mw@p.center; n=(mw.to_3x3()@p.normal).normalized()
    nb[p.material_index].append((round(c.x,2),round(c.y,2),round(c.z,2),round(n.x,2),round(n.y,2),round(n.z,2),round(p.area,4)))
print('CNT',cnt)
import statistics
for mi,l in nb.items():
    xs=[a[0] for a in l]; ys=[a[1] for a in l]; zs=[a[2] for a in l]
    print('MI',mi,o.material_slots[mi].material.name,min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
    nc=collections.Counter((a[3],a[4],a[5]) for a in l); print('  normals',nc.most_common(6))
# black faces with large area
bl=sorted(nb[1],key=lambda a:-a[6])[:15]
for a in bl: print('BLK',a)
for m in o.material_slots:
    mat=m.material; b=mat.node_tree.nodes.get('Principled BSDF')
    print('MAT',mat.name, tuple(round(v,3) for v in b.inputs['Base Color'].default_value) if b else None)
