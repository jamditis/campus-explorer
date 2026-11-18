import bpy, os, json
BAK=os.path.abspath('montclair_state_pre_20261030ng.blend')
src=open('scripts/ng/ng_build.py').read(); src=src[:src.index('if REVERT:')]
g={'__name__':'ngrev'}; exec(src,g); g['revert'](); bpy.context.view_layer.update()
def sig():
    d={}
    for o in bpy.data.objects:
        d[o.name]=str((o.hide_render,o.hide_viewport,len(o.data.vertices) if o.type=='MESH' else 0,[round(x,4) for x in o.matrix_world.translation],[s.material.name if s.material else None for s in o.material_slots]))
    return d
a=sig(); bpy.ops.wm.open_mainfile(filepath=BAK); b=sig()
for k in sorted(a):
    if a[k]!=b.get(k): print('DIFF',k,'| cur',a[k][:150],'| bak',b.get(k,'')[:150])
