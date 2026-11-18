import bpy, mathutils, json
out=[]
for o in bpy.data.objects:
    n=o.name.lower()
    if 'schmitt' in n or 'sch_' in n[:4]:
        bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box] if o.type=='MESH' else [o.matrix_world.translation]
        xs=[v.x for v in bb];ys=[v.y for v in bb];zs=[v.z for v in bb]
        out.append(dict(name=o.name,type=o.type,hide=o.hide_render,coll=[c.name for c in o.users_collection],
          verts=len(o.data.vertices) if o.type=='MESH' else 0,
          mats=[m.name for m in o.data.materials if m] if o.type=='MESH' else [],
          bb=[round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),2),round(max(zs),2)]))
json.dump(out,open('data/og/schmitt_objs.json','w'),indent=1)
print('N',len(out))
for d in out: print(d)
