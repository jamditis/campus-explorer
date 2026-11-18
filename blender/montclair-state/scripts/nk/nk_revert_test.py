# nk REVERT test: run on an in-folder COPY of the nk final; compares to montclair_state_pre_20261030nk.blend
import bpy, os, hashlib
BAK=os.path.abspath('montclair_state_pre_20261030nk.blend')
src=open('scripts/nk/nk_build.py').read(); src=src[:src.index('if REVERT:')]
g={'__name__':'nkrev'}; exec(src,g); g['revert'](); bpy.context.view_layer.update()
CHK=['CCOM atrium mullion v%d'%i for i in range(6)]
MATS=['NG_wall_white','NG_ceiling_white','NG_red_wall','NG_maroon_frame','NG_terrazzo_1F_open_floor','NH_terrazzo_1F_tone_variation_UNVERIFIED','NG_wood_cladding']
def stat():
    obs=sorted(bpy.data.objects, key=lambda o:o.name); h=hashlib.sha256()
    for o in obs:
        h.update(o.name.encode()); h.update(str((o.hide_render,o.hide_viewport,o.visible_glossy)).encode())
        if o.type=='MESH': h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
        if o.type=='LIGHT': h.update(str((round(o.data.energy,3),round(getattr(o.data,'size',0),3),round(getattr(o.data,'spot_size',0),3),[round(c,3) for c in o.data.color])).encode())
        h.update(str([round(x,4) for x in o.matrix_world.translation]).encode())
        if o.name in CHK: h.update(str([tuple(round(c,4) for c in v.co) for v in o.data.vertices]).encode())
        h.update(str([s.material.name if s.material else None for s in o.material_slots]).encode())
    m=bpy.data.materials.get('NG_led_strip'); h.update(str(m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value).encode())
    for mn in MATS:
        for nd in bpy.data.materials[mn].node_tree.nodes:
            for i in nd.inputs:
                if hasattr(i,'default_value') and not i.is_linked:
                    v=i.default_value; h.update(str([round(x,4) for x in v] if hasattr(v,'__len__') else round(v,4)).encode())
            if nd.type=='VALTORGB': h.update(str([[round(x,4) for x in e.color] for e in nd.color_ramp.elements]).encode())
    h.update(str(sorted((o.name,tuple(m.name for m in o.modifiers)) for o in obs if o.modifiers)).encode())
    h.update(str(sorted(m.name for m in bpy.data.meshes if m.use_fake_user)).encode())
    return (len(obs), sum(1 for o in obs if not o.hide_render), len(bpy.data.collections), len(bpy.data.materials), len(bpy.data.meshes), h.hexdigest()[:16])
cur=stat(); print("REV_CUR",cur)
bpy.ops.wm.open_mainfile(filepath=BAK); bak=stat(); print("REV_BAK",bak); print("REV_MATCH", cur==bak)
