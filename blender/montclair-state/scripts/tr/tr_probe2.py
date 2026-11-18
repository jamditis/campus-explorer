import bpy, json
from mathutils import Vector
# Inspect TQ brick shader for base-band nodes (look for Attribute ti_z0 / height mixes)
m=bpy.data.materials['TQ_Stone_buff_brick_UNVERIFIED']; nt=m.node_tree
info=[]
for n in nt.nodes:
    d={'name':n.name,'type':n.type,'label':n.label}
    if n.type=='ATTRIBUTE': d['attr']=n.attribute_name
    if n.type=='VALTORGB':
        d['els']=[(round(e.position,3),[round(c,3) for c in e.color]) for e in n.color_ramp.elements]
    if n.type=='MATH':
        d['op']=n.operation; d['v']=[round(i.default_value,4) if hasattr(i,'default_value') and isinstance(i.default_value,(int,float)) else None for i in n.inputs]
    if n.type=='MIX':
        try: d['fac']=round(n.inputs['Factor'].default_value,3); d['blend']=n.blend_type
        except: pass
        try: d['A']=[round(c,3) for c in n.inputs['A'].default_value]
        except: pass
        try: d['B']=[round(c,3) for c in n.inputs['B'].default_value]
        except: pass
    if n.type=='BUMP':
        d['str']=round(n.inputs['Strength'].default_value,3); d['dist']=round(n.inputs['Distance'].default_value,4)
    info.append(d)
# links summary involving base-ish
links=[]
for l in nt.links:
    links.append(f"{l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}")
open('/workspace/nj-scenes/montclair-state/data/tr/tq_nodes.json','w').write(json.dumps({'nodes':info,'links':links},indent=2))
print('nodes',len(info),'links',len(links))
# print attribute + color ramps + mixes with grey B
for n in info:
    if n['type'] in ('ATTRIBUTE','VALTORGB') or (n['type']=='MIX' and n.get('B') and n['B'][0]<0.55):
        print(n)
# inspect TJ base material if still around
m2=bpy.data.materials.get('TJ_dorm_wall_base_UNVERIFIED')
print('TJ_base exists', bool(m2))
# walk ends: QS_footway_546643369 and QW extension
for nm in ('QS_footway_546643369_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED'):
    o=bpy.data.objects.get(nm)
    if not o: print('missing',nm); continue
    # find endpoint verts (extremal)
    me=o.data; mw=o.matrix_world
    verts=[mw @ v.co for v in me.vertices]
    # southmost and northmost
    s=min(verts,key=lambda v:v.y); n=max(verts,key=lambda v:v.y)
    w=min(verts,key=lambda v:v.x); e=max(verts,key=lambda v:v.x)
    print(nm,'nverts',len(verts),'S',tuple(round(x,2) for x in s),'N',tuple(round(x,2) for x in n),'W',tuple(round(x,2) for x in w),'E',tuple(round(x,2) for x in e))
# OSM Footpaths collection: any ways west of Stone not modelled
fp=bpy.data.objects.get('Footpaths_OSM')
print('Footpaths_OSM', fp.type if fp else None)
# look for OSM ways in data files near Stone
import os
for root,dirs,files in os.walk('/workspace/nj-scenes/montclair-state/data'):
    for f in files:
        if '546643' in f or 'footway' in f.lower() and 'stone' in f.lower():
            print('datafile',os.path.join(root,f))
# check tj walk script for how walks were built
print('done')
