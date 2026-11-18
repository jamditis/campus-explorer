"""Reload campus_assets so Sweetgum star-leaf + tip trim pick up. Args: [--save]"""
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
for m in bpy.data.meshes:
    if 'Sweetgum' in m.name:
        print('MESH', m.name, 'lib', m.library.filepath if m.library else None,
              'ba_star_leaf', m.get('ba_star_leaf'), 'ba_tip_trim', m.get('ba_tip_trim'),
              'verts', len(m.vertices))
mat = bpy.data.materials.get('Leaf_Sweetgum')
if mat:
    print('MAT Leaf_Sweetgum ba_star_leaf', mat.get('ba_star_leaf'),
          'lib', mat.library.filepath if mat.library else None)
sg = [o for o in bpy.data.objects if o.type == 'MESH' and o.data and 'Sweetgum' in o.data.name]
print('SWEETGUM_INSTANCES', len(sg))
# sample one instance world height
if sg:
    o = sg[0]
    print('SAMPLE', o.name, 'loc', tuple(round(x,3) for x in o.location),
          'scale', tuple(round(x,3) for x in o.scale),
          'data', o.data.name)
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
