# ws126b: bed shrubs are now smaller -> leaf-card density 2600 -> 1700 /local m2 (render memory peak ~8.5 GB at 2600)
import bpy
n=0
for o in bpy.data.objects:
    if o.name.startswith(('WS125_bed_shrub_','WS126_bed_shrub_')):
        for m in o.modifiers:
            if m.type=='NODES' and 'Socket_2' in m.keys(): m['Socket_2']=1700.0; n+=1
        o.update_tag()
print('M126b density set',n)
bpy.ops.wm.save_mainfile(); print('M126b SAVED')
