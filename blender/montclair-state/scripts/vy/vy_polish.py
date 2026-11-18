"""vy polish once: warm Stone buff (was too cool/white vs slide 285 #cfc8b8); reduce Mix.008 bleach."""
import bpy, json, os
STASH='/workspace/nj-scenes/montclair-state/data/vy/vy_brick_stash.json'
# keep original pre-vy stash intact; write polish deltas separately
POLISH='/workspace/nj-scenes/montclair-state/data/vy/vy_polish_stash.json'
m=bpy.data.materials['TR_Stone_brick_detail_UNVERIFIED']
nt=m.node_tree
bt=nt.nodes['Brick Texture']
cr=nt.nodes['Color Ramp']
cr1=nt.nodes['Color Ramp.001']
cr2=nt.nodes['Color Ramp.002']
mix=nt.nodes['Mix']
mix001=nt.nodes['Mix.001']
mix008=nt.nodes['Mix.008']
mix009=nt.nodes['Mix.009']
pre={
 'brick_color1':list(bt.inputs['Color1'].default_value),
 'brick_color2':list(bt.inputs['Color2'].default_value),
 'mortar':list(bt.inputs['Mortar'].default_value),
 'mortar_size':float(bt.inputs['Mortar Size'].default_value),
 'ramp0':list(cr.color_ramp.elements[0].color),
 'ramp1':list(cr.color_ramp.elements[1].color),
 'ramp001_0':list(cr1.color_ramp.elements[0].color),
 'ramp001_1':list(cr1.color_ramp.elements[1].color),
 'ramp002_0':list(cr2.color_ramp.elements[0].color),
 'ramp002_1':list(cr2.color_ramp.elements[1].color),
 'mix_b':list(mix.inputs[7].default_value),
 'mix001_b':list(mix001.inputs[7].default_value),
 'mix008_fac':float(mix008.inputs[0].default_value),
 'overlay_fac':float(mix009.inputs[0].default_value),
}
json.dump(pre, open(POLISH,'w'), indent=1)
# warmer buff (more yellow, less blue), slightly deeper so AgX doesn't bleach to white
bt.inputs['Color1'].default_value=(0.74, 0.66, 0.50, 1.0)
bt.inputs['Color2'].default_value=(0.64, 0.56, 0.42, 1.0)
bt.inputs['Mortar'].default_value=(0.82, 0.78, 0.68, 1.0)
bt.inputs['Mortar Size'].default_value=0.011
cr.color_ramp.elements[0].color=(0.60, 0.54, 0.44, 1.0)
cr.color_ramp.elements[1].color=(0.74, 0.68, 0.54, 1.0)
cr1.color_ramp.elements[0].color=(0.66, 0.58, 0.46, 1.0)
cr1.color_ramp.elements[1].color=(0.76, 0.68, 0.52, 1.0)
# Color Ramp.002 was bleaching to pure white — warm soft ceiling instead
cr2.color_ramp.elements[0].color=(0.90, 0.875, 0.82, 1.0)
cr2.color_ramp.elements[1].color=(0.98, 0.96, 0.90, 1.0)
mix.inputs[7].default_value=(0.88, 0.84, 0.74, 1.0)   # was 0.92 cool
mix001.inputs[7].default_value=(0.96, 0.93, 0.86, 1.0)
mix008.inputs[0].default_value=0.32  # was 0.60 — less highlight bleach
mix009.inputs[0].default_value=0.30
m['vy_mat']=1
m['vy_note']='Stone buff brick slide285 + polish warm UNVERIFIED'
# sync twin
m2=bpy.data.materials.get('TQ_Stone_buff_brick_UNVERIFIED')
if m2 and m2.use_nodes:
    nt2=m2.node_tree
    for src,dst_name in [(bt,'Brick Texture'),(cr,'Color Ramp'),(cr1,'Color Ramp.001'),(cr2,'Color Ramp.002')]:
        d=nt2.nodes.get(dst_name)
        if not d: continue
        if dst_name=='Brick Texture':
            d.inputs['Color1'].default_value=bt.inputs['Color1'].default_value[:]
            d.inputs['Color2'].default_value=bt.inputs['Color2'].default_value[:]
            d.inputs['Mortar'].default_value=bt.inputs['Mortar'].default_value[:]
            d.inputs['Mortar Size'].default_value=bt.inputs['Mortar Size'].default_value
        else:
            for i,e in enumerate(src.color_ramp.elements):
                d.color_ramp.elements[i].color=e.color[:]
    for nm,node in [('Mix',mix),('Mix.001',mix001),('Mix.008',mix008),('Mix.009',mix009)]:
        d=nt2.nodes.get(nm)
        if not d: continue
        if nm in ('Mix','Mix.001'):
            d.inputs[7].default_value=node.inputs[7].default_value[:]
        else:
            d.inputs[0].default_value=node.inputs[0].default_value
    m2['vy_mat']=1
bpy.ops.wm.save_mainfile()
print('POLISH saved', len(bpy.data.objects))
print('brick1', tuple(round(x,3) for x in bt.inputs['Color1'].default_value))
print('mix008_fac', mix008.inputs[0].default_value)
