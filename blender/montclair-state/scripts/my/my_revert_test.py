# my REVERT test: run on an in-folder COPY of the my final; compares to montclair_state_pre_20261030my.blend
import bpy, os, hashlib
BAK=os.path.abspath('montclair_state_pre_20261030my.blend')
col=bpy.data.collections['MS_CCOM_newsroom_studio_detail2_20261030my']
for o in list(col.all_objects): bpy.data.objects.remove(o)
for c in list(col.children_recursive): bpy.data.collections.remove(c)
bpy.data.collections.remove(col)
def stat():
    obs=sorted(bpy.data.objects, key=lambda o:o.name)
    h=hashlib.sha256()
    for o in obs:
        h.update(o.name.encode()); h.update(str(o.hide_render).encode())
        if o.type=='MESH': h.update(str((len(o.data.vertices),len(o.data.polygons))).encode())
        h.update(str([round(x,4) for x in o.matrix_world.translation]).encode())
    return (len(obs), sum(1 for o in obs if not o.hide_render), len(bpy.data.collections), h.hexdigest()[:16])
cur=stat(); print("REV_CUR",cur)
bpy.ops.wm.open_mainfile(filepath=BAK)
bak=stat(); print("REV_BAK",bak)
print("REV_MATCH", cur==bak)
