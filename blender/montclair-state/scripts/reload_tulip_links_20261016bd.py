"""2026-10-16 bd: reload campus_assets after Tulip LOD1 leaf-card shrink.
Trees are NOT moved; prints location/scale/rotation checksum before/after.
Also prints mesh bd_tulip_lod1_leaf flag. Args: [--save]"""
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
m = bpy.data.materials.get('Leaf_TulipPoplar')
print('MAT', m and m.get('bc_tulip_color'), m and (m.library.filepath if m.library else None))
me = bpy.data.meshes.get('Tree_TulipPoplar_LOD1')
print('MESH_FLAG', me and me.get('bd_tulip_lod1_leaf'), me and (me.library.filepath if me.library else 'local'))
for nm in ('TulipPoplar_Color', 'TulipPoplar_Opacity'):
    im = bpy.data.images.get(nm)
    if im:
        im.reload(); px = im.pixels[:]
        print('IMG', nm, im.filepath, 'mean', round(sum(px[0::4 * 41]) / len(px[0::4 * 41]), 3))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)