"""Quick probe of Freeman glass/cream/sky objects for session vh."""
import bpy, json
D='/workspace/nj-scenes/montclair-state/data/vh'
import os; os.makedirs(D, exist_ok=True)
def princ(name):
    m=bpy.data.materials.get(name)
    if not m or not m.use_nodes: return None
    b=m.node_tree.nodes.get('Principled BSDF')
    if not b: return None
    d={}
    for k in ('Base Color','Roughness','Alpha','Coat Weight','Coat Roughness','Specular IOR Level','Transmission Weight','Emission Strength','Emission Color'):
        if k in b.inputs:
            v=b.inputs[k].default_value
            try: d[k]=[round(float(x),4) for x in v]
            except TypeError: d[k]=round(float(v),4)
    return d
out={
 'n_objects': len(bpy.data.objects),
 'W_glass': princ('VD_Freeman_W_glass_pane_UNVERIFIED'),
 'VB_glass': princ('VB_Freeman_glass_cool_clear_UNVERIFIED'),
 'SE_glass': princ('VG_Freeman_SE_glass_pane_UNVERIFIED'),
 'SE_span': princ('VG_Freeman_SE_spandrel_deep_UNVERIFIED'),
 'sky': princ('VF_Freeman_W_sky_tint_UNVERIFIED'),
 'cream_vb': princ('VB_Freeman_cream_brick_strong_UNVERIFIED'),
 'cream_vf': princ('VF_Freeman_N_cream_punch_UNVERIFIED'),
 'sky_objs': sorted([o.name for o in bpy.data.objects if 'sky_tint' in o.name.lower()]),
 'n_cream_objs': sorted([o.name for o in bpy.data.objects if ('cream' in o.name.lower() or 'pier' in o.name.lower() or 'belt' in o.name.lower()) and ('VF_' in o.name or 'VG_' in o.name or 'VE_' in o.name or 'VB_' in o.name)])[:60],
 'cams': sorted([o.name for o in bpy.data.objects if o.type=='CAMERA' and ('Freeman' in o.name or 'FREEMAN' in o.name)]),
 'letter': None,
}
let=bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw=let.matrix_world
    out['letter']={'body':let.data.body,'size':round(let.data.size,5),'loc':[round(mw[i][3],4) for i in range(3)]}
json.dump(out, open(D+'/vh_probe.json','w'), indent=2)
print(json.dumps(out, indent=2))
print('OBJECTS', len(bpy.data.objects))
