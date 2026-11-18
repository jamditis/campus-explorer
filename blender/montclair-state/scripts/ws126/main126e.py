# ws126e: self-review — burning bush read as red eggs. Euonymus alatus 'Compactus' is a broad rounded mound: undo the 1.22 z stretch, widen 1.12, leaf density 2300 so the core is covered.
import bpy
def minz(me): return min(v.co.z for v in me.vertices)
n=0
for o in bpy.data.objects:
    if o.name.startswith('WS126_bed_shrub_') and 'BurningBush' in o.name:
        base=o.location.z+minz(o.data)*o.scale.z
        o.scale=(o.scale.x/0.9*1.12,o.scale.y/0.9*1.12,o.scale.z/1.22*0.95); o.location.z=base-minz(o.data)*o.scale.z
        for m in o.modifiers:
            if m.type=='NODES' and 'Socket_2' in m.keys(): m['Socket_2']=2300.0
        o.update_tag(); n+=1
print('M126e bb reshaped',n)
bpy.ops.wm.save_mainfile(); print('M126e SAVED')
