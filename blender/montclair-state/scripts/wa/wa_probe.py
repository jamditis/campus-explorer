# wa probe: Bohn massing faces + VW overlay objects (read-only)
import bpy, json
from mathutils import Vector
OUT='/workspace/nj-scenes/montclair-state/data/wa'
res={'objects':[], 'faces':[], 'vw':[]}
for o in bpy.data.objects:
    if 'Bohn' not in o.name: continue
    res['objects'].append(dict(name=o.name, type=o.type, hide_render=o.hide_render,
        colls=[c.name for c in o.users_collection], props={k:str(o[k])[:80] for k in o.keys()},
        npoly=len(o.data.polygons) if o.type=='MESH' else 0))
    if o.type!='MESH' or o.hide_render: continue
    if o.get('vw_obj'): continue
    mw=o.matrix_world; me=o.data
    for pi,p in enumerate(me.polygons):
        n=(mw.to_3x3()@p.normal).normalized()
        vs=[mw@me.vertices[i].co for i in p.vertices]
        zs=[v.z for v in vs]
        if abs(n.z)>0.5:
            if n.z>0.5 and o.name.startswith(('TL_','TK_')):
                res['faces'].append(dict(obj=o.name,kind='top',z=round(max(zs),2),xy=[[round(v.x,2),round(v.y,2)] for v in vs]))
            continue
        if not o.name.startswith(('TL_','TK_','TP_')): continue
        res['faces'].append(dict(obj=o.name,kind='wall',pi=pi,n=[round(n.x,3),round(n.y,3)],
            z0=round(min(zs),2),z1=round(max(zs),2),
            xy=[[round(v.x,2),round(v.y,2)] for v in vs if abs(v.z-min(zs))<0.01],
            area=round(p.area,1)))
for o in bpy.data.objects:
    if o.get('vw_obj'):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        res['vw'].append(dict(name=o.name,type=o.type,npoly=len(o.data.polygons) if o.type=='MESH' else 0,
          bbmin=[round(min(v[i] for v in bb),2) for i in range(3)],bbmax=[round(max(v[i] for v in bb),2) for i in range(3)]))
res['n_objs']=len(bpy.data.objects)
json.dump(res,open(OUT+'/probe.json','w'),indent=1)
print('PROBE objs',len(res['objects']),'faces',len(res['faces']),'vw',len(res['vw']),'n',res['n_objs'])
