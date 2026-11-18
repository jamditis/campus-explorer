import bpy, os
SP=bpy.data.objects['TN_Blanton_spandrel_bands_UNVERIFIED']
if 'vu_obj' in SP:
    del SP['vu_obj']
    print('cleared vu_obj from SP')
else:
    print('no vu_obj on SP')
print('vu_orig', SP.get('vu_orig_mesh'), 'mesh', SP.data.name, 'verts', len(SP.data.vertices))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
