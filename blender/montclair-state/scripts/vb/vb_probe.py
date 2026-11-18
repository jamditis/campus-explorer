"""Read-only probe of Freeman UV_/UW_/UY_/VA objects + materials for session vb."""
import bpy, json, os
from mathutils import Vector
D='/workspace/nj-scenes/montclair-state'
DATA=D+'/data/vb'
os.makedirs(DATA, exist_ok=True)
OSM=json.load(open(D+'/data/uv/freeman_osm_probe.json'))
E6=next(e for e in OSM['edges'] if e['i']==6)
U=Vector((*E6['u'],0)).normalized(); N=Vector((*E6['n'],0)).normalized(); A=Vector((*E6['a'],0))
out={
  'n_objects':len(bpy.data.objects),
  'n_materials':len(bpy.data.materials),
  'uv':sum(1 for o in bpy.data.objects if o.get('uv_obj')),
  'uw':sum(1 for o in bpy.data.objects if o.get('uw_obj')),
  'uy':sum(1 for o in bpy.data.objects if o.get('uy_obj')),
  'va_props':sum(1 for o in bpy.data.objects if any(k.startswith('va_') for k in o.keys())),
  'frame':{'A':list(A),'U':list(U),'N':list(N),'len':E6['len']},
  'objects':[],
  'materials':[],
  'n_face_spans':[],
}
def beam(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return {
      'name':o.name,'type':o.type,
      'hide':bool(o.hide_get()),'hide_render':bool(o.hide_render),
      'col':[c.name for c in o.users_collection],
      't':[min((p-A).dot(U) for p in pts), max((p-A).dot(U) for p in pts)],
      'n':[min((p-A).dot(N) for p in pts), max((p-A).dot(N) for p in pts)],
      'z':[min(p.z for p in pts), max(p.z for p in pts)],
      'dims':[round(v,3) for v in o.dimensions],
      'mats':[s.material.name if s.material else None for s in (o.material_slots or [])],
      'props':{k:o[k] for k in o.keys() if k in ('uv_obj','uw_obj','uy_obj','uy_polish','uy_hid_prev','UNVERIFIED') or str(k).startswith('va_')},
      'body':getattr(o.data,'body',None) if o.type=='FONT' else None,
    }
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    tags=any(o.get(k) for k in ('uv_obj','uw_obj','uy_obj')) or 'Freeman' in o.name or 'freeman' in o.name.lower()
    if not tags and not (o.type=='FONT' and 'FREEMAN' in (getattr(o.data,'body','') or '').upper()):
        continue
    r=beam(o)
    out['objects'].append(r)
    if o.type=='MESH' and not o.hide_get() and ('N_' in o.name or 'letter' in o.name.lower() or 'entrance' in o.name.lower() or 'screen' in o.name.lower() or 'terracotta' in o.name.lower() or 'orange' in o.name.lower()):
        out['n_face_spans'].append({'name':o.name,'t':r['t'],'n':r['n'],'z':r['z']})
for m in bpy.data.materials:
    if any(s in m.name for s in ('Freeman','freeman','curtain_glass','cream_brick','terracotta','spandrel','window_frame')) or m.get('uv_mat') or m.get('uy_mat') or m.get('uw_mat'):
        info={'name':m.name,'uy':bool(m.get('uy_mat')),'uv':bool(m.get('uv_mat')),'uw':bool(m.get('uw_mat')),'nodes':[]}
        if m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type=='BSDF_PRINCIPLED':
                    bc=list(n.inputs['Base Color'].default_value)
                    rough=n.inputs['Roughness'].default_value
                    alpha=n.inputs['Alpha'].default_value if 'Alpha' in n.inputs else None
                    trans=None
                    for key in ('Transmission Weight','Transmission'):
                        if key in n.inputs:
                            trans=n.inputs[key].default_value; break
                    info['principled']={'base':bc,'rough':rough,'alpha':alpha,'transmission':trans}
                if n.type=='TEX_BRICK':
                    info['brick']={
                      'c1':list(n.inputs['Color1'].default_value),
                      'c2':list(n.inputs['Color2'].default_value),
                      'mortar':list(n.inputs['Mortar'].default_value),
                      'width':n.inputs['Brick Width'].default_value,
                      'row':n.inputs['Row Height'].default_value,
                      'mortar_size':n.inputs['Mortar Size'].default_value,
                      'scale':n.inputs['Scale'].default_value,
                    }
        out['materials'].append(info)
# W window object slot detail
for wn in ('UY_Freeman_W_recessed_vertical_windows_UNVERIFIED','UY_Freeman_S_recessed_vertical_windows_UNVERIFIED','UY_Freeman_N_terracotta_3panel_window_bay_UNVERIFIED','UY_Freeman_W_cream_brick_skin_UNVERIFIED','UY_Freeman_S_cream_brick_skin_UNVERIFIED'):
    o=bpy.data.objects.get(wn)
    if o:
        out.setdefault('slot_detail',{})[wn]=[s.material.name if s.material else None for s in o.material_slots]
json.dump(out, open(DATA+'/vb_probe.json','w'), indent=2, default=str)
open(DATA+'/probe_notes.md','w').write(
f"""# vb probe notes (session vb, Nov 6 2026)
objects={out['n_objects']} mats={out['n_materials']} uv={out['uv']} uw={out['uw']} uy={out['uy']}
N-face spans (visible): {len(out['n_face_spans'])}
Freeman-ish objects: {len(out['objects'])}
materials of interest: {len(out['materials'])}
See vb_probe.json for full dump.
""")
print('VB_PROBE objs',out['n_objects'],'freemanish',len(out['objects']),'mats',len(out['materials']))
for s in out['n_face_spans']:
    print('NSPAN', s['name'], 't', [round(x,2) for x in s['t']], 'z', [round(x,1) for x in s['z']])
for m in out['materials']:
    if 'cream' in m['name'].lower() or 'glass' in m['name'].lower() or 'curtain' in m['name'].lower():
        print('MAT', m['name'], m.get('principled'), m.get('brick'))
