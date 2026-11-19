import bpy
for im in bpy.data.images:
    if 'mask' in im.name: print('P221', im.name, im.filepath, bool(im.packed_file), im.users)
