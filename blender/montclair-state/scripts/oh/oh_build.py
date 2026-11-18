# oh (Oct 31 2026): Schmitt Hall fixes from the confirmed env-team photos (schmitt_01-03, 'CONRAD J. SCHMITT HALL', 2011)
# 1) mansard sawtooth: em_ringforce FACE attr = 1 on 'Schmitt Hall roof (LiDAR)' faces outside the og deck polygon
#    (Roof_tile_or_membrane gates its flat-normal membrane switch with it) -> tile, not grey membrane
# 2) window frames dark red-brown: SCH_win_* instancers -> local copy collection with an object-level red frame material
# 3) grey split-face block base course on 'Schmitt Hall walls' (Schmitt-only copy of the stucco material, world z < 139.30)
# REVERT=1 undoes all. Run: blender -b montclair_state.blend --python scripts/oh/oh_build.py -- --save
import bpy, json, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
roof=bpy.data.objects['Schmitt Hall roof (LiDAR)']; me=roof.data
walls=bpy.data.objects['Schmitt Hall walls']
wins=[o for o in bpy.data.objects if o.name.startswith('SCH_win_') and o.instance_type=='COLLECTION']
ORIG_IC=bpy.data.collections['CCOM_Win_Wing_A']
CN='OH_SCH_Win_red_frame_20261031oh'
if REV:
    a=me.attributes.get('em_ringforce')
    if a: me.attributes.remove(a)
    for o in wins:
        if o.instance_collection and o.instance_collection.name==CN: o.instance_collection=ORIG_IC
    c=bpy.data.collections.get(CN)
    if c:
        for ob in list(c.objects): bpy.data.objects.remove(ob)
        bpy.data.collections.remove(c)
    for i,s in enumerate(walls.material_slots):
        if s.material and s.material.name=='OH_Schmitt_stucco_block_base_UNVERIFIED':
            s.material=bpy.data.materials['Wall_stucco_mission']
    for n in ('OH_Schmitt_win_frame_red_brown','OH_Schmitt_stucco_block_base_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    print('REVERTED')
else:
    # 1 roof
    d=json.load(open('data/og/schmitt_deck_inset3_og.json')); rings=[pg[0] for pg in d]
    def inside(x,y):
        for r in rings:
            n=len(r); j=n-1; ins=False
            for i in range(n):
                xi,yi=r[i]; xj,yj=r[j]
                if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: ins=not ins
                j=i
            if ins: return True
        return False
    a=me.attributes.get('em_ringforce') or me.attributes.new('em_ringforce','FLOAT','FACE')
    mw=roof.matrix_world; c=0
    for p in me.polygons:
        w=mw@p.center; v=0.0 if inside(w.x,w.y) else 1.0
        a.data[p.index].value=v; c+=int(v)
    print('ringforce faces',c,'of',len(me.polygons))
    # 2 windows
    red=bpy.data.materials.get('OH_Schmitt_win_frame_red_brown') or bpy.data.materials.new('OH_Schmitt_win_frame_red_brown')
    red.use_nodes=True; b=red.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(0.20,0.025,0.022,1); b.inputs['Roughness'].default_value=0.42; b.inputs['Metallic'].default_value=0.35
    c2=bpy.data.collections.get(CN)
    if not c2:
        c2=bpy.data.collections.new(CN)
        for ob in ORIG_IC.objects:
            nb=ob.copy(); c2.objects.link(nb)
            if ob.name.endswith('_frame'):
                for s in nb.material_slots: s.link='OBJECT'; s.material=red
        c2.instance_offset=ORIG_IC.instance_offset
    for o in wins: o.instance_collection=c2
    print('wins',len(wins))
    # 3 base course
    src=bpy.data.materials['Wall_stucco_mission']
    m=bpy.data.materials.get('OH_Schmitt_stucco_block_base_UNVERIFIED')
    if not m:
        m=src.copy(); m.name='OH_Schmitt_stucco_block_base_UNVERIFIED'
        nt=m.node_tree; N=nt.nodes; L=nt.links
        bsdf=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
        bc=bsdf.inputs['Base Color']; old=bc.links[0].from_socket if bc.is_linked else None
        geo=N.new('ShaderNodeNewGeometry'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'],sep.inputs[0])
        lt=N.new('ShaderNodeMath'); lt.operation='LESS_THAN'; lt.inputs[1].default_value=139.30; L.new(sep.outputs['Z'],lt.inputs[0])
        cap=N.new('ShaderNodeMath'); cap.operation='COMPARE'; cap.inputs[1].default_value=139.36; cap.inputs[2].default_value=0.06; L.new(sep.outputs['Z'],cap.inputs[0])
        brick=N.new('ShaderNodeTexBrick'); brick.inputs['Scale'].default_value=1.0
        brick.inputs['Brick Width'].default_value=0.40; brick.inputs['Row Height'].default_value=0.20; brick.inputs['Mortar Size'].default_value=0.008
        brick.inputs['Color1'].default_value=(0.30,0.30,0.29,1); brick.inputs['Color2'].default_value=(0.24,0.245,0.24,1); brick.inputs['Mortar'].default_value=(0.42,0.42,0.40,1)
        # horizontal-ish mapping of wall position: use (x+y, z)
        comb=N.new('ShaderNodeCombineXYZ'); add=N.new('ShaderNodeMath'); add.operation='ADD'
        L.new(sep.outputs['X'],add.inputs[0]); L.new(sep.outputs['Y'],add.inputs[1]); L.new(add.outputs[0],comb.inputs['X']); L.new(sep.outputs['Z'],comb.inputs['Y'])
        L.new(comb.outputs[0],brick.inputs['Vector'])
        mix=N.new('ShaderNodeMix'); mix.data_type='RGBA'
        if old: L.new(old,mix.inputs['A'])
        else: mix.inputs['A'].default_value=bc.default_value
        L.new(brick.outputs['Color'],mix.inputs['B']); L.new(lt.outputs[0],mix.inputs['Factor'])
        mix2=N.new('ShaderNodeMix'); mix2.data_type='RGBA'; mix2.inputs['B'].default_value=(0.55,0.54,0.51,1)
        L.new(mix.outputs['Result'],mix2.inputs['A']); L.new(cap.outputs[0],mix2.inputs['Factor'])
        L.new(mix2.outputs['Result'],bc)
    for s in walls.material_slots:
        if s.material and s.material.name=='Wall_stucco_mission': s.material=m
    print('walls mat',[s.material.name for s in walls.material_slots])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
