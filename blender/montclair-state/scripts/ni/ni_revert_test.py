# ni REVERT test: run on an in-folder COPY of the ni final; compares to montclair_state_pre_20261030ni.blend
import bpy, os, hashlib
BAK=os.path.abspath('montclair_state_pre_20261030ni.blend')
src=open('scripts/ni/ni_build.py').read(); src=src[:src.index('if REVERT:')]
g={'__name__':'nirev'}; exec(src,g); g['revert'](); bpy.context.view_layer.update()
CHK=['CCOM atrium mullion v%d'%i for i in range(6)]
def stat():
    obs=sorted(bpy.data.objects, key=lambda o:o.name); h=hashlib.sha256()
    for o in obs:
        h.update(o.name.encode()); h.update(str((o.hide_render,o.hide_viewport,o.visible_glossy)).encode())
        if o.type=='MESH': h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
        if o.type=='LIGHT': h.update(str(round(o.data.energy,3)).encode())
        h.update(str([round(x,4) for x in o.matrix_world.translation]).encode())
        if o.name in CHK: h.update(str([tuple(round(c,4) for c in v.co) for v in o.data.vertices]).encode())
        h.update(str([s.material.name if s.material else None for s in o.material_slots]).encode())
    m=bpy.data.materials.get('NG_led_strip'); h.update(str(m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value).encode())
    return (len(obs), sum(1 for o in obs if not o.hide_render), len(bpy.data.collections), len(bpy.data.materials), len(bpy.data.meshes), h.hexdigest()[:16])
cur=stat(); print("REV_CUR",cur)
bpy.ops.wm.open_mainfile(filepath=BAK); bak=stat(); print("REV_BAK",bak); print("REV_MATCH", cur==bak)
