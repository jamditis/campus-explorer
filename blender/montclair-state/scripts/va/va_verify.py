"""Verify va lettering restore without saving the inspected scene."""
import bpy, json
from mathutils import Vector, Matrix
D='/workspace/nj-scenes/montclair-state'
s=next(o for o in bpy.data.objects if o.type=='FONT' and 'FREEMAN' in o.data.body)
original=json.load(open(D+'/data/va/lettering_pre_va.json'))
report=json.load(open(D+'/data/va/va_fix_report.json'))
assert s.data.body=='GRACE H. FREEMAN HALL'
assert s.type=='FONT' and s.data.size>0
assert len(bpy.data.objects)==report['objects']==8644
assert len(bpy.data.materials)==report['materials']==1024
assert s.get('va_fixed')==1
bpy.context.view_layer.update()
ev=s.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=ev.to_mesh()
pts=[s.matrix_world @ v.co for v in mesh.vertices]
ev.to_mesh_clear()
edge=next(e for e in json.load(open(D+'/data/uv/freeman_osm_probe.json'))['edges'] if e['i']==6)
A=Vector((*edge['a'],0)); U=Vector((*edge['u'],0)); N=Vector((*edge['n'],0))
l,r=report['support_t']
ts=[(p-A).dot(U) for p in pts]
ns=[(p-A).dot(N) for p in pts]
assert min(ts)>=l and max(ts)<=r
assert min(ns)>=0.34-1e-5
print('VASIG',len(bpy.data.objects),len(bpy.data.materials),s.data.body,
      'text_t',min(ts),max(ts),'wall_t',l,r,'outward_n',min(ns),max(ns))
print('VA_VERIFY PASS: complete sign supported by solid wing, no glass overhang or NW corner overhang')
