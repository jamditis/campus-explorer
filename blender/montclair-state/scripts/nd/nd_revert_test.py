# nd REVERT test: run on an in-folder COPY of the nd final; compares to montclair_state_pre_20261030nd.blend
import bpy, os, hashlib, json
BAK=os.path.abspath('montclair_state_pre_20261030nd.blend')
sc=bpy.context.scene; O=bpy.data.objects; mats=bpy.data.materials
for on,lst in json.loads(sc.get('nd_swaps','{}')).items():
    o=O[on]
    for i,old in lst: o.material_slots[i].material=mats[old]
for k in ('nd_note','nd_swaps'):
    if k in sc: del sc[k]
col=bpy.data.collections['MS_CCOM_newsroom_studio_detail6_20261030nd']
for o in list(col.all_objects): O.remove(o)
bpy.data.collections.remove(col)
def stat():
    obs=sorted(bpy.data.objects, key=lambda o:o.name); h=hashlib.sha256()
    for o in obs:
        h.update(o.name.encode()); h.update(str((o.hide_render,o.hide_viewport)).encode())
        if o.type=='MESH': h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
        h.update(str([round(x,4) for x in o.matrix_world.translation]).encode())
        h.update(str([s.material.name if s.material else None for s in o.material_slots]).encode())
    return (len(obs), sum(1 for o in obs if not o.hide_render), len(bpy.data.collections), h.hexdigest()[:16])
cur=stat(); print("REV_CUR",cur)
bpy.ops.wm.open_mainfile(filepath=BAK); bak=stat(); print("REV_BAK",bak); print("REV_MATCH", cur==bak)
