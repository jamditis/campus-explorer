"""2026-10-16 be: reload campus_assets after Tulip LOD1 bark prune.
Trees are NOT moved; prints location/scale/rotation checksum before/after.
Expects bd checksums: main 6173.0423, north 3521.4425.
Args: [--save]"""
import bpy, sys
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAVE = '--save' in argv
def tulips():
    return [o for o in bpy.data.objects if o.type == 'MESH' and o.data and 'TulipPoplar' in o.data.name]
def chk():
    s = 0.0
    for o in tulips():
        s += sum(o.location) + sum(o.scale) + sum(o.rotation_euler)
    return round(s, 4)
before = (len(tulips()), chk())
n = 0
for lib in bpy.data.libraries:
    if 'campus_assets.blend' in (lib.filepath or '').replace('\\', '/'):
        lib.reload(); n += 1; print('RELOAD', lib.filepath)
after = (len(tulips()), chk())
print('RELOADED', n, 'TULIP before', before, 'after', after, 'UNCHANGED', before == after)
me = bpy.data.meshes.get('Tree_TulipPoplar_LOD1')
print('MESH_FLAG', me and me.get('be_tulip_lod1_bark'),
      'deleted', me and me.get('be_tulip_lod1_bark_deleted'),
      'lib', me and (me.library.filepath if me.library else 'local'))
print('BD_FLAG', me and me.get('bd_tulip_lod1_leaf'))
m = bpy.data.materials.get('Leaf_TulipPoplar')
print('MAT_bc', m and m.get('bc_tulip_color'))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)
