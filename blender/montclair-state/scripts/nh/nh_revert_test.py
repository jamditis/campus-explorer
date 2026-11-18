# nh REVERT test: run on an in-folder COPY of the ng final; compares to montclair_state_pre_20261030nh.blend
import bpy, os, hashlib, json
BAK=os.path.abspath('montclair_state_pre_20261030nh.blend')
src=open('scripts/nh/nh_build.py').read(); src=src[:src.index('if REVERT:')]
g={'__name__':'nhrev'}; exec(src,g); g['revert'](); bpy.context.view_layer.update()
def stat():
    obs=sorted(bpy.data.objects, key=lambda o:o.name); h=hashlib.sha256()
    for o in obs:
        h.update(o.name.encode()); h.update(str((o.hide_render,o.hide_viewport)).encode())
        if o.type=='MESH': h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
        h.update(str([round(x,4) for x in o.matrix_world.translation]).encode())
        if o.name in ('School of Communication and Media walls','NG 1F open floor atrium terrazzo','NG atrium N wall (tower face)'): h.update(str([tuple(round(c,4) for c in v.co) for v in o.data.vertices]).encode()); h.update(o.data.name.encode())
        h.update(str([s.link for s in o.material_slots]).encode())
        h.update(str([s.material.name if s.material else None for s in o.material_slots]).encode())
    return (len(obs), sum(1 for o in obs if not o.hide_render), len(bpy.data.collections), len(bpy.data.materials), len(bpy.data.meshes), h.hexdigest()[:16])
cur=stat(); print("REV_CUR",cur)
bpy.ops.wm.open_mainfile(filepath=BAK); bak=stat(); print("REV_BAK",bak); print("REV_MATCH", cur==bak)
