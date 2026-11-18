"""vz probe: dump TR_Blanton_infill_cream_UNVERIFIED node graph (Mapping/Noise causing vertical striping)."""
import bpy, json, os
OUT='/workspace/nj-scenes/montclair-state/data/vz/probe.json'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
names=[]
for m in bpy.data.materials:
    if 'Blanton' in m.name and ('infill' in m.name.lower() or 'cream' in m.name.lower()):
        names.append(m.name)
    elif 'infill_cream' in m.name.lower() or 'cream_infill' in m.name.lower():
        names.append(m.name)
# also any twin
for m in bpy.data.materials:
    if 'cream' in m.name.lower() and m.name not in names:
        names.append(m.name)
print('CANDIDATES', names)
report={'mats':{}, 'cams':[], 'objs_using':{}}
for name in names:
    m=bpy.data.materials.get(name)
    if not m or not m.use_nodes: continue
    nt=m.node_tree
    nodes=[]
    for n in nt.nodes:
        info={'name':n.name,'type':n.type,'label':n.label}
        if n.type=='MAPPING':
            info['loc']=list(n.inputs['Location'].default_value)
            info['rot']=list(n.inputs['Rotation'].default_value)
            info['scale']=list(n.inputs['Scale'].default_value)
        if n.type=='TEX_NOISE':
            for k in ('Scale','Detail','Roughness','Lacunarity','Distortion'):
                if k in n.inputs: info[k]=float(n.inputs[k].default_value)
        if n.type=='TEX_VORONOI':
            for k in ('Scale','Detail','Roughness','Randomness'):
                if k in n.inputs: info[k]=float(n.inputs[k].default_value)
        if n.type=='VALTORGB':
            info['elements']=[{'pos':e.position,'color':list(e.color)} for e in n.color_ramp.elements]
        if n.type=='MAP_RANGE':
            info['from_min']=float(n.inputs['From Min'].default_value)
            info['from_max']=float(n.inputs['From Max'].default_value)
            info['to_min']=float(n.inputs['To Min'].default_value)
            info['to_max']=float(n.inputs['To Max'].default_value)
        if n.type=='MIX' or n.type=='MIX_RGB':
            try: info['blend']=n.blend_type
            except: pass
            try: info['fac']=float(n.inputs[0].default_value)
            except: pass
            try:
                if hasattr(n,'data_type'): info['data_type']=n.data_type
            except: pass
        if n.type=='BSDF_PRINCIPLED':
            bc=n.inputs['Base Color']
            info['base_linked']=bc.is_linked
            info['base_default']=list(bc.default_value)
            info['rough']=float(n.inputs['Roughness'].default_value)
        nodes.append(info)
    links=[{'from':l.from_node.name+'.'+l.from_socket.name,'to':l.to_node.name+'.'+l.to_socket.name} for l in nt.links]
    report['mats'][name]={'users':m.users,'nodes':nodes,'links':links,'custom':{k:m[k] for k in m.keys()}}
    users=[]
    for o in bpy.data.objects:
        for s in o.material_slots:
            if s.material and s.material.name==name:
                users.append(o.name); break
    report['objs_using'][name]=users
# cams of interest
for c in bpy.data.objects:
    if c.type=='CAMERA' and ('Blanton' in c.name or 'east_dorm' in c.name or c.name.startswith('VZ_') or c.name.startswith('TR_CAM') or c.name.startswith('TU_CAM') or c.name.startswith('TI_CAM')):
        report['cams'].append(c.name)
print('CAMS', report['cams'])
json.dump(report, open(OUT,'w'), indent=1)
print('WROTE', OUT)
print('OBJS', len(bpy.data.objects))
