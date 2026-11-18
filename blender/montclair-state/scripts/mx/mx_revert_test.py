# mx REVERT test: run on an in-folder COPY of the mx final; compares to montclair_state_pre_20261030mx.blend
import bpy, os
BAK=os.path.abspath('montclair_state_pre_20261030mx.blend')
sc=bpy.context.scene
for nm in sc.get('mx_hidden',[]):
    o=bpy.data.objects.get(nm)
    if o: o.hide_render=False; o.hide_viewport=False
col=bpy.data.collections['MS_CCOM_newsroom_studio_detail_20261030mx']
for o in list(col.all_objects): bpy.data.objects.remove(o)
for c in list(col.children_recursive): bpy.data.collections.remove(c)
bpy.data.collections.remove(col)
ng=bpy.data.node_groups.get('MX_instance_proto_rot')
if ng: bpy.data.node_groups.remove(ng)
names=['School of Communication and Media walls','CCOM newsroom studio side + back walls (mw)']+list(sc.get('mx_trimmed',[]))
names=[n for n in names if n in bpy.data.objects]
with bpy.data.libraries.load(BAK) as (src,dst): pass
# map object -> mesh name in backup by loading the objects' data names via a temp load of objects
with bpy.data.libraries.load(BAK) as (src,dst):
    dst.objects=[n for n in names]
tmp={o.name.rsplit('.',1)[0] if o.name not in names else o.name:o for o in dst.objects if o}
for o in dst.objects:
    pass
for n,bo in zip(names,dst.objects):
    bpy.data.objects[n].data=bo.data
    bpy.data.objects.remove(bo)
fm=bpy.data.materials.get('MW_studio_raised_floor_grey_UNVERIFIED')
if fm is None:  # orphaned + dropped on the mx save; restore from the backup
    with bpy.data.libraries.load(BAK) as (src,dst2): dst2.materials=['MW_studio_raised_floor_grey_UNVERIFIED']
    fm=dst2.materials[0]
bpy.data.objects['CCOM newsroom studio floor (raised access, mw)'].data.materials[0]=fm
bpy.data.objects['CCOM newsroom set riser (mw)'].data.materials[0]=fm
bpy.data.materials['MW_studio_set_backdrop_blue_UNVERIFIED'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=6
def stat():
    return (len(bpy.data.objects), {n:len(bpy.data.objects[n].data.polygons) for n in names}, sum(1 for o in bpy.data.objects if not o.hide_render),
            bpy.data.materials['MW_studio_set_backdrop_blue_UNVERIFIED'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value)
cur=stat(); print("REV_CUR",cur)
bpy.ops.wm.open_mainfile(filepath=BAK)
bak=stat(); print("REV_BAK",bak)
print("REV_MATCH", cur==bak)
