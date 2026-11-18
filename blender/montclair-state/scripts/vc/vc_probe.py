"""Read-only probe of Freeman window geometry for dark backplanes + N mid-wall gaps (session vc)."""
import bpy, json, os
from mathutils import Vector
D='/workspace/nj-scenes/montclair-state'
DATA=D+'/data/vc'
os.makedirs(DATA, exist_ok=True)
OSM=json.load(open(D+'/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open(D+'/data/uv/uv_main.json')).get('GR', 129.053))
TOPZ=147.05
E6=next(e for e in OSM['edges'] if e['i']==6)
U=Vector((*E6['u'],0)).normalized(); N=Vector((*E6['n'],0)).normalized(); A=Vector((*E6['a'],0))
out={
  'n_objects':len(bpy.data.objects),
  'GR':GR,'TOPZ':TOPZ,
  'vb':sum(1 for o in bpy.data.objects if o.get('vb_obj')),
  'uy':sum(1 for o in bpy.data.objects if o.get('uy_obj')),
  'uv':sum(1 for o in bpy.data.objects if o.get('uv_obj')),
  'vc_existing':sum(1 for o in bpy.data.objects if o.get('vc_obj')),
  'n_face':[],
  'window_objs':[],
  'letter':None,
}
def beam(o, frame_A=A, frame_U=U, frame_N=N):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return {
      'name':o.name,
      't':[min((p-frame_A).dot(frame_U) for p in pts), max((p-frame_A).dot(frame_U) for p in pts)],
      'n':[min((p-frame_A).dot(frame_N) for p in pts), max((p-frame_A).dot(frame_N) for p in pts)],
      'z':[min(p.z for p in pts), max(p.z for p in pts)],
      'mats':[s.material.name if s.material else None for s in (o.material_slots or [])],
      'n_verts':len(o.data.vertices) if o.type=='MESH' and o.data else 0,
    }
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    if not (('Freeman' in o.name) or o.get('vb_obj') or o.get('uy_obj') or o.get('uv_obj') or o.get('vc_obj')):
        continue
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        mw=o.matrix_world
        out['letter']={'name':o.name,'body':o.data.body,'size':o.data.size,
                       'loc':[round(mw[0][3],4),round(mw[1][3],4),round(mw[2][3],4)]}
    r=beam(o)
    if any(k in o.name for k in ('N_','letter','entrance','screen','fill','terracotta','cream','window','curtain')):
        if o.type=='MESH' and not o.hide_get():
            out['n_face'].append(r)
    if 'window' in o.name.lower() or 'curtain' in o.name.lower() or 'terracotta' in o.name.lower():
        out['window_objs'].append(r)
# W edge centers (match uy polish)
e1=next(e for e in OSM['edges'] if e['i']==1)
L1=e1['len']; pitch=3.6
centers=[]
n_bays=max(1,int((L1-4.0)/pitch))
for i in range(n_bays):
    t=2.0+pitch*(i+0.5)
    if t>L1-2.0: break
    centers.append(round(t,3))
out['W_centers']=centers
out['W_L']=L1
out['S_ts']=[3.5,7.5,11.5]
json.dump(out, open(DATA+'/vc_probe.json','w'), indent=2)
print('VC_PROBE objs',out['n_objects'],'vb',out['vb'],'letter',out['letter'])
print('W_centers',centers)
for s in out['n_face']:
    print('NSPAN', s['name'][:60], 't',[round(x,2) for x in s['t']], 'n',[round(x,2) for x in s['n']], 'z',[round(x,1) for x in s['z']])
