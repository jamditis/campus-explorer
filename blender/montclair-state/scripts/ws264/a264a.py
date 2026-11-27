# ws264 asset stream: relativise the 4 absolute leaf-texture paths stored inside assets/campus_assets.blend
# (SweetgumStar_*, TulipPoplar_*), so main's last 4 absolute paths go away. No other change.
import bpy, os
n=0
for i in bpy.data.images:
    fp=i.filepath
    if i.library or i.packed_file or not fp or fp.startswith('//'): continue
    if not os.path.exists(fp): print('A264A missing',i.name,fp); continue
    i.filepath='//'+os.path.relpath(os.path.normpath(fp),os.path.dirname(bpy.data.filepath)); n+=1; print('A264A rel',i.name,fp,'->',i.filepath,flush=True)
left=[(i.name,i.filepath) for i in bpy.data.images if not i.library and not i.packed_file and i.filepath and not i.filepath.startswith('//')]
left+= [(l.name,l.filepath) for l in bpy.data.libraries if not l.filepath.startswith('//')]
print('A264A relativised',n,'left',left,flush=True)
bpy.ops.wm.save_mainfile(compress=bpy.data.use_autopack or True)
print('A264A SAVED',flush=True)
