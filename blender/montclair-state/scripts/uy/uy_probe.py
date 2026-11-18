import bpy, json, os
DATA='/workspace/nj-scenes/montclair-state/data/uy'
os.makedirs(DATA, exist_ok=True)
objs=[o for o in bpy.data.objects if 'Freeman' in o.name or o.get('uv_obj') or o.get('uw_obj')]
rows=[]
for o in sorted(objs, key=lambda x:x.name):
    rows.append({
        'name': o.name,
        'type': o.type,
        'col': o.users_collection[0].name if o.users_collection else None,
        'loc': [round(v,3) for v in o.location],
        'dims': [round(v,3) for v in o.dimensions],
        'uv': bool(o.get('uv_obj')),
        'uw': bool(o.get('uw_obj')),
        'body': getattr(o.data,'body',None) if o.type=='FONT' else None,
    })
    print(o.name, o.type, 'uv' if o.get('uv_obj') else '', 'uw' if o.get('uw_obj') else '', getattr(o.data,'body', '') if o.type=='FONT' else '')
core={}
for n in ['Freeman Hall walls','Freeman Hall roof (LiDAR)','UC_Freeman_parapet_UNVERIFIED']:
    o=bpy.data.objects.get(n)
    if o:
        bb=[list(o.matrix_world @ bpy.data.objects[n].bound_box[i]) for i in range(8)] if False else None
        xs=[(o.matrix_world @ __import__('mathutils').Vector(c)).x for c in o.bound_box]
        ys=[(o.matrix_world @ __import__('mathutils').Vector(c)).y for c in o.bound_box]
        zs=[(o.matrix_world @ __import__('mathutils').Vector(c)).z for c in o.bound_box]
        core[n]={'dims':[round(v,3) for v in o.dimensions],'bbox':[min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)]}
        print('CORE', n, core[n])
    else:
        print('CORE MISS', n)
out={'n_objects':len(bpy.data.objects),'freemanish':rows,'core':core}
json.dump(out, open(DATA+'/uy_probe.json','w'), indent=2)
print('TOTAL', len(bpy.data.objects), 'FREEMANISH', len(rows))
# list mats with Freeman/UV_
mats=[m.name for m in bpy.data.materials if 'reeman' in m.name or m.name.startswith('UV_')]
print('MATS', mats)
