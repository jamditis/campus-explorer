# record modifier flags + object/mesh stats at load_post (before eval), then disable all modifiers; dump json
import bpy, os, json, hashlib
from bpy.app.handlers import persistent
R={}
@persistent
def _rec(*a):
    mods=[]
    for o in bpy.data.objects:
        for m in o.modifiers:
            mods.append((o.name,m.name,m.type,m.show_viewport,m.show_render)); m.show_viewport=False
    R['mods']=mods
    R['nobj']=len(bpy.data.objects); R['nmesh']=len(bpy.data.meshes); R['nmat']=len(bpy.data.materials); R['nimg']=len(bpy.data.images)
    R['objs']={o.name:(o.type,o.data.name if o.data else None,len(o.data.vertices) if o.type=='MESH' else 0, o.hide_render, o.hide_viewport) for o in bpy.data.objects}
bpy.app.handlers.load_post.append(_rec)
bpy.ops.wm.open_mainfile(filepath=os.environ['F'])
json.dump(R,open(os.environ['J'],'w'))
print('CHK208 done',R['nobj'],R['nmesh'],len(R['mods']),flush=True)
