"""Reload campus_assets library links so Honey Locust instances pick up smaller leaves.
Args after --: [--save]
"""
import bpy, sys
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SAVE = '--save' in argv
n = 0
for lib in bpy.data.libraries:
    fp = (lib.filepath or '').replace('\\', '/')
    if 'campus_assets.blend' in fp:
        print('RELOAD', lib.filepath)
        lib.reload()
        n += 1
print('RELOADED', n)
# verify a honey mesh
for m in bpy.data.meshes:
    if m.name == 'Tree_HoneyLocust_LOD1':
        print('MESH', m.name, 'lib', m.library.filepath if m.library else None,
              'ay_small_leaf', m.get('ay_small_leaf'), 'verts', len(m.vertices))
hl = [o for o in bpy.data.objects if o.type == 'MESH' and o.data and 'HoneyLocust' in o.data.name]
print('HONEY_INSTANCES', len(hl))
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
