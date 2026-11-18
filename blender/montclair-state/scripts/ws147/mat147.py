import bpy
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['WS27_CollegeAve_asphalt_2020ortho','Asphalt']
with bpy.data.libraries.load(P, link=False) as (src,dst):
    dst.materials=[n for n in names if n in src.materials]
for m in dst.materials:
    print("MAT",m.name)
    if not m.use_nodes: print("  diffuse",tuple(m.diffuse_color)); continue
    for n in m.node_tree.nodes:
        s=n.bl_idname
        if n.type=='TEX_IMAGE' and n.image: print("  IMG",n.image.filepath[-60:], n.image.size[:])
        if n.type=='RGB': print("  RGB",tuple(round(c,2) for c in n.outputs[0].default_value))
        if n.type=='VALTORGB': print("  RAMP",[tuple(round(c,2) for c in e.color) for e in n.color_ramp.elements])
        if n.type=='BSDF_PRINCIPLED' and not n.inputs['Base Color'].is_linked: print("  BASE",tuple(round(c,2) for c in n.inputs['Base Color'].default_value))
        if n.type=='MIX' or n.type=='MIX_RGB':
            for i in n.inputs:
                if i.type=='RGBA' and not i.is_linked: print("  MIXCOL",i.name,tuple(round(c,2) for c in i.default_value))
with bpy.data.libraries.load(P, link=False) as (src,dst):
    dst.objects=['PA_walk_panel_tone_chips_UNVERIFIED','QY_walk_junction_wear_decals_UNVERIFIED']
for o in dst.objects:
    print("OBJ",o.name,[s.material.name for s in o.material_slots if s.material],[ (m.type, m.node_group.name if getattr(m,'node_group',None) else None) for m in o.modifiers])
    for m in o.modifiers:
        if m.type=='NODES':
            for n in m.node_group.nodes:
                if n.type=='OBJECT_INFO': print("  OBJINFO",n.inputs[0].default_value and n.inputs[0].default_value.name)
                if n.type=='SET_MATERIAL': print("  SETMAT",n.inputs[2].default_value and n.inputs[2].default_value.name)
            for k,v in m.items(): print("  IN",k,getattr(v,'name',v))
    for s in o.material_slots:
        mm=s.material
        if mm and mm.use_nodes:
            for n in mm.node_tree.nodes:
                if n.type=='VALTORGB': print("  RAMP",mm.name,[tuple(round(c,2) for c in e.color) for e in n.color_ramp.elements])
                if n.type=='RGB': print("  RGB",mm.name,tuple(round(c,2) for c in n.outputs[0].default_value))
                if n.type=='BSDF_PRINCIPLED' and not n.inputs['Base Color'].is_linked: print("  BASE",mm.name,tuple(round(c,2) for c in n.inputs['Base Color'].default_value))
