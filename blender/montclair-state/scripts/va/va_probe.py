"""Read-only Freeman north lettering / wall inspection for session va."""
import bpy, json, os
from mathutils import Vector
D='/workspace/nj-scenes/montclair-state'
out={'objects':len(bpy.data.objects),'materials':len(bpy.data.materials),'sign':{},'walls':[]}
E=next(e for e in json.load(open(D+'/data/uv/freeman_osm_probe.json'))['edges'] if e['i']==6)
U=Vector((*E['u'],0)).normalized(); N=Vector((*E['n'],0)).normalized(); A=Vector((*E['a'],0))
out['frame']={'A':list(A),'U':list(U),'N':list(N),'length':E['len']}
def beam(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return {'name':o.name,'type':o.type,'collection':[c.name for c in o.users_collection],
            'bounds':{'t':[min((p-A).dot(U) for p in pts),max((p-A).dot(U) for p in pts)],
                      'n':[min((p-A).dot(N) for p in pts),max((p-A).dot(N) for p in pts)],
                      'z':[min(p.z for p in pts),max(p.z for p in pts)]},
            'verts':len(o.data.vertices) if o.type=='MESH' else None,
            'props':{k:o[k] for k in o.keys() if not isinstance(o[k],(list,tuple,dict))}}
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.data.body.upper():
        r=beam(o)
        r.update(body=o.data.body,size=o.data.size,matrix=[list(v) for v in o.matrix_world],
                 extrude=o.data.extrude,align_x=o.data.align_x)
        out['sign']=r
    if o.type=='MESH' and ('Freeman' in o.name or 'freeman' in o.name) and any(s in o.name for s in ['letter','wall','terracotta','screen','entrance','cream']):
        out['walls'].append(beam(o))
json.dump(out,open(D+'/data/va/va_probe.json','w'),indent=2,default=str)
print('VA_PROBE',json.dumps(out,indent=2,default=str))
