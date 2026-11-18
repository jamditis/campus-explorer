# na REVERT test: run on an in-folder COPY of the na final; compares to montclair_state_pre_20261030na.blend
import bpy, os, hashlib
BAK=os.path.abspath('montclair_state_pre_20261030na.blend')
sc=bpy.context.scene
for nm in sc.get('na_hidden',[]):
    o=bpy.data.objects[nm]; o.hide_render=False; o.hide_viewport=False
for k in ('na_hidden','na_note'):
    if k in sc: del sc[k]
for cn in ('MS_CCM_office_interior_20261030na','MS_CCOM_back_rooms_furnish_20261030na'):
    col=bpy.data.collections[cn]
    for o in list(col.all_objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(col)
def stat():
    obs=sorted(bpy.data.objects, key=lambda o:o.name)
    h=hashlib.sha256()
    for o in obs:
        h.update(o.name.encode()); h.update(str((o.hide_render,o.hide_viewport)).encode())
        if o.type=='MESH': h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
        h.update(str([round(x,4) for x in o.matrix_world.translation]).encode())
    return (len(obs), sum(1 for o in obs if not o.hide_render), len(bpy.data.collections), h.hexdigest()[:16])
cur=stat(); print("REV_CUR",cur)
bpy.ops.wm.open_mainfile(filepath=BAK)
bak=stat(); print("REV_BAK",bak)
print("REV_MATCH", cur==bak)
