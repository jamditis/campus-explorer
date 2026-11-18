"""vz probe2: dump Mix/Math defaults on cream infill striping chain."""
import bpy, json
def ser(v):
    try:
        if hasattr(v, '__len__') and not isinstance(v, (str, bytes)):
            return [float(x) for x in v]
    except Exception:
        pass
    if isinstance(v, (int, float)):
        return float(v)
    return str(v)

m=bpy.data.materials['TR_Blanton_infill_cream_UNVERIFIED']
nt=m.node_tree
out={}
for name in ['Mapping','Mapping.001','Noise Texture','Noise Texture.001','Noise Texture.002','Noise Texture.003',
             'Color Ramp','Color Ramp.001','Color Ramp.002','Mix','Mix.001','Mix.007','Mix.008','Mix.009',
             'Math.037','Math.038','Math.039','Math.040','Bump']:
    n=nt.nodes.get(name)
    if not n:
        out[name]='MISSING'; continue
    d={'type':n.type}
    for inp in n.inputs:
        if inp.is_linked: continue
        try:
            d[inp.name]=ser(inp.default_value)
        except Exception as e:
            d[inp.name]=f'err:{e}'
    if n.type=='MATH':
        d['operation']=n.operation
        d['use_clamp']=bool(n.use_clamp)
    if n.type=='MIX':
        d['blend']=n.blend_type; d['data_type']=n.data_type
        for i,lab in [(6,'A'),(7,'B'),(0,'Factor')]:
            if i < len(n.inputs) and n.inputs[i].is_linked:
                ln=n.inputs[i].links[0]
                d[f'{lab}_from']=ln.from_node.name+'.'+ln.from_socket.name
            elif i < len(n.inputs):
                d[f'{lab}_default']=ser(n.inputs[i].default_value)
    if n.type=='VALTORGB':
        d['elements']=[{'pos':float(e.position),'color':[float(x) for x in e.color]} for e in n.color_ramp.elements]
    if n.type=='MAPPING':
        d['scale']=ser(n.inputs['Scale'].default_value)
    if n.type=='BUMP':
        d['strength']=float(n.inputs['Strength'].default_value)
        d['distance']=float(n.inputs['Distance'].default_value)
    out[name]=d
json.dump(out, open('/workspace/nj-scenes/montclair-state/data/vz/probe2.json','w'), indent=1)
print(json.dumps(out, indent=2))
