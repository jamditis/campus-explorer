import bpy, json
from mathutils import Vector
out={}
out['blanton']=[]; out['stone']=[]; out['walks_near_stone']=[]; out['mats']=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if 'Blanton' in o.name:
        mats=[s.material.name if s.material else None for s in o.material_slots]
        corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
        out['blanton'].append({'name':o.name,'mats':mats,'nverts':len(o.data.vertices),
            'xmin':round(min(c.x for c in corners),1),'xmax':round(max(c.x for c in corners),1),
            'ymin':round(min(c.y for c in corners),1),'ymax':round(max(c.y for c in corners),1),
            'zmin':round(min(c.z for c in corners),1),'zmax':round(max(c.z for c in corners),1)})
    if 'Stone' in o.name:
        mats=[s.material.name if s.material else None for s in o.material_slots]
        corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
        out['stone'].append({'name':o.name,'mats':mats,'nverts':len(o.data.vertices),'keys':[k for k in o.keys() if not k.startswith('_')],
            'xmin':round(min(c.x for c in corners),1),'xmax':round(max(c.x for c in corners),1),
            'ymin':round(min(c.y for c in corners),1),'ymax':round(max(c.y for c in corners),1),
            'zmin':round(min(c.z for c in corners),1),'zmax':round(max(c.z for c in corners),1)})
    n=o.name.lower()
    if any(k in n for k in ('walk','footway','path')):
        corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
        xs=[c.x for c in corners]; ys=[c.y for c in corners]
        if max(xs)>120 and min(xs)<180 and max(ys)>250 and min(ys)<360:
            out['walks_near_stone'].append({'name':o.name,
                'xmin':round(min(xs),1),'xmax':round(max(xs),1),'ymin':round(min(ys),1),'ymax':round(max(ys),1),
                'mats':[s.material.name if s.material else None for s in o.material_slots]})
for m in bpy.data.materials:
    if any(k in m.name for k in ('dorm','Stone','Blanton','TJ_dorm','TI_dorm','TM_dorm','TQ_','TK_dorm')):
        out['mats'].append(m.name)
out['mats']=sorted(out['mats'])
# TJ base material detail
for mn in ('TJ_dorm_wall_base_UNVERIFIED','TM_dorm_wall_streaked_UNVERIFIED','TQ_Stone_buff_brick_UNVERIFIED','TI_dorm_wall_windows_UNVERIFIED','TN_Blanton_piers_UNVERIFIED','TN_Blanton_spandrel_bands_UNVERIFIED','TN_Blanton_block_base_UNVERIFIED'):
    m=bpy.data.materials.get(mn)
    if not m or not m.use_nodes: continue
    info={'name':mn,'nodes':[]}
    for n in m.node_tree.nodes:
        if n.type in ('VALTORGB','MIX','BSDF_PRINCIPLED'):
            d={'type':n.type,'name':n.name}
            if n.type=='VALTORGB':
                d['els']=[(round(e.position,3),[round(c,3) for c in e.color]) for e in n.color_ramp.elements]
            if n.type=='MIX':
                try: d['fac']=round(n.inputs['Factor'].default_value,3)
                except: pass
                try: d['B']=[round(c,3) for c in n.inputs['B'].default_value]
                except: pass
                try: d['blend']=n.blend_type
                except: pass
            if n.type=='BSDF_PRINCIPLED':
                try: d['base']=[round(c,3) for c in n.inputs['Base Color'].default_value]
                except: pass
            info['nodes'].append(d)
    out.setdefault('mat_detail',[]).append(info)
# OSM ways: look for objects with osm_id near Stone or named 546643369
osm=[]
for o in bpy.data.objects:
    if '546643' in o.name or ('osm' in o.name.lower() and 'foot' in o.name.lower()):
        osm.append(o.name)
    for k in o.keys():
        if 'osm' in str(k).lower() or '546643' in str(o.get(k,'')):
            osm.append(f'{o.name}:{k}={o[k]}')
out['osmish']=sorted(set(osm))[:40]
# check TI material slots per mesh materials list
for o in bpy.data.objects:
    if o.type=='MESH' and ('TI_Stone' in o.name or 'TI_Blanton' in o.name):
        out.setdefault('slot_detail',[]).append({'name':o.name,'mats':[m.name if m else None for m in o.data.materials]})
print(json.dumps(out, indent=2)[:14000])
open('/workspace/nj-scenes/montclair-state/data/tr/probe.json','w').write(json.dumps(out,indent=2))
print('N_OBJ',len(bpy.data.objects))
